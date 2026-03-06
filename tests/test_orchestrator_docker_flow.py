import json

from agents.orchestrator import OrchestratorAgent
from domain.entities import AgentType, ExecutionResult, ExecutionStatus


class DummyProvider:
    async def generate(self, *args, **kwargs):
        return "{}"


def test_analyze_docker_result_flags_user_action_requirement():
    orchestrator = OrchestratorAgent(DummyProvider())

    payload = {
        "docker_validation": {
            "success": False,
            "requires_user_action": True,
            "user_action_message": "Docker não está disponível no ambiente.",
            "user_action_items": ["Instale o Docker."]
        }
    }

    docker_test_result = ExecutionResult(
        agent_type=AgentType.DOCKER_TEST,
        status=ExecutionStatus.FAILED,
        output=json.dumps(payload),
        error_message="docker unavailable"
    )

    ok, issues, requires_action = orchestrator._analyze_docker_result(docker_test_result)

    assert ok is False
    assert requires_action is True
    assert any("Ação manual necessária" in issue for issue in issues)
    assert any("Instale o Docker" in issue for issue in issues)
