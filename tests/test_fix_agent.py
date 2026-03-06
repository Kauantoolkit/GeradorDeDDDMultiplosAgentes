import asyncio
from types import SimpleNamespace

from agents.fix_agent import FixAgent
from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ProjectConfig,
    Requirement,
    ValidationResult,
    ValidationStatus,
)


class DummyFixProvider:
    async def generate(self, *args, **kwargs):
        return '{"fixes":[{"file_path":"main.py","action":"modify","content":"def broken(:\\n    pass"}]}'


def _make_requirement(tmp_path):
    requirement = Requirement(
        description="Gerar aplicação",
        project_config=ProjectConfig(output_directory=str(tmp_path)),
    )
    requirement.execution_result = ExecutionResult(
        agent_type=AgentType.EXECUTOR,
        status=ExecutionStatus.SUCCESS,
        output="{}",
        files_created=["main.py"],
    )
    return requirement


def _make_validation(requirement):
    return ValidationResult(
        requirement_id=requirement.id,
        status=ValidationStatus.REJECTED,
        issues=["Erro de import"],
        score=0.2,
        feedback="corrigir",
    )


def test_fix_with_llm_skips_invalid_python_content(tmp_path):
    (tmp_path / "main.py").write_text("def ok():\n    return 1\n", encoding="utf-8")

    requirement = _make_requirement(tmp_path)
    validation = _make_validation(requirement)

    agent = FixAgent(DummyFixProvider())
    result = asyncio.run(agent.execute(requirement, validation, attempt=1))

    assert result.success is False
    assert result.files_modified == []
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "def ok():\n    return 1\n"


def test_fix_basic_creates_docker_compose_when_missing(tmp_path):
    requirement = _make_requirement(tmp_path)
    validation = ValidationResult(
        requirement_id=requirement.id,
        status=ValidationStatus.REJECTED,
        issues=["docker falhou"],
        score=0.1,
        feedback="adicionar docker",
    )

    agent = FixAgent(llm_provider=None)
    result = asyncio.run(agent.execute(requirement, validation, attempt=1))

    assert result.success is True
    assert "docker-compose.yml" in result.files_modified
    assert (tmp_path / "docker-compose.yml").exists()
