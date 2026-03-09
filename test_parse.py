import json
import re

# Test parsing of the LLM output
test_outputs = [
    '{"services": [{"id": 1}]}',
    '{"microservices": [{"name": "pedidos"}]}',
    '```json\n{"microservices": [{"name": "test"}]}\n```',
    'Something before {"key": "value"} something after'
]

def parse_llm_output(llm_output):
    # Strategy 1: Find JSON in markdown
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            print(f'Strategy 1 failed: {e}')
            pass
    
    # Strategy 2: Find JSON without markdown
    json_start = llm_output.find('{')
    json_end = llm_output.rfind('}')
    
    if json_start >= 0 and json_end > json_start:
        json_str = llm_output[json_start:json_end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f'Strategy 2 failed: {e}')
            pass
    
    return None

for test in test_outputs:
    result = parse_llm_output(test)
    print(f'Input: {test[:50]}... -> Result: {result}')

