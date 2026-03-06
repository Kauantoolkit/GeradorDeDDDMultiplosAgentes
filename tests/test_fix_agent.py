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


def test_fix_adds_email_validator_when_schema_uses_emailstr(tmp_path):
    service_dir = tmp_path / "services" / "user_service"
    (service_dir / "api").mkdir(parents=True)
    (service_dir / "api" / "schemas.py").write_text(
        "from pydantic import BaseModel, EmailStr\n\nclass UserIn(BaseModel):\n    email: EmailStr\n",
        encoding="utf-8",
    )
    (service_dir / "requirements.txt").write_text("fastapi>=0.110\npydantic>=2.0\n", encoding="utf-8")

    requirement = _make_requirement(tmp_path)
    requirement.execution_result.files_created = [
        "services/user_service/api/schemas.py",
        "services/user_service/requirements.txt",
    ]
    validation = ValidationResult(
        requirement_id=requirement.id,
        status=ValidationStatus.REJECTED,
        issues=["EmailStr sem dependência"],
        score=0.2,
        feedback="corrigir dependência",
    )

    agent = FixAgent(llm_provider=None)
    result = asyncio.run(agent.execute(requirement, validation, attempt=1))

    assert result.success is True
    assert "services/user_service/requirements.txt" in result.files_modified
    requirements = (service_dir / "requirements.txt").read_text(encoding="utf-8")
    assert "email-validator>=2.0.0" in requirements


class PatchFixProvider:
    async def generate(self, *args, **kwargs):
        return '{"fixes":[{"file_path":"main.py","action":"patch","search":"return 1","replace":"return 2"}]}'


class PlaceholderFixProvider:
    async def generate(self, *args, **kwargs):
        return '{"fixes":[{"file_path":"main.py","action":"modify","content":"# TODO: implementar"}]}'


def test_fix_with_llm_applies_patch_action(tmp_path):
    (tmp_path / "main.py").write_text("def ok():\n    return 1\n", encoding="utf-8")

    requirement = _make_requirement(tmp_path)
    validation = _make_validation(requirement)

    agent = FixAgent(PatchFixProvider())
    result = asyncio.run(agent.execute(requirement, validation, attempt=1))

    assert result.success is True
    assert "main.py" in result.files_modified
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "def ok():\n    return 2\n"


def test_fix_with_llm_skips_placeholder_content(tmp_path):
    (tmp_path / "main.py").write_text("def ok():\n    return 1\n", encoding="utf-8")

    requirement = _make_requirement(tmp_path)
    validation = _make_validation(requirement)

    agent = FixAgent(PlaceholderFixProvider())
    result = asyncio.run(agent.execute(requirement, validation, attempt=1))

    assert result.success is False
    assert result.files_modified == []
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "def ok():\n    return 1\n"
