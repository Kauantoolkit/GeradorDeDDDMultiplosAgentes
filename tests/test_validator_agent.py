from pathlib import Path

from agents.validator_agent import ValidatorAgent
from domain.entities import AgentType, ExecutionResult, ExecutionStatus, ProjectConfig, Requirement, ValidationStatus


class ApprovingProvider:
    async def generate(self, *args, **kwargs):
        return (
            '{"status":"approved","score":0.95,'
            '"approved_items":["ok"],"rejected_items":[],'
            '"missing_items":[],"issues":[],"feedback":"ok"}'
        )


class CapturingApprovingProvider:
    def __init__(self):
        self.prompt = ""

    async def generate(self, *args, **kwargs):
        self.prompt = kwargs.get("prompt", "")
        return (
            '{"status":"approved","score":0.95,'
            '"approved_items":["ok"],"rejected_items":[],'
            '"missing_items":[],"issues":[],"feedback":"ok"}'
        )


def _make_requirement(tmp_path: Path, description: str = "Gerar backend") -> Requirement:
    return Requirement(
        description=description,
        project_config=ProjectConfig(output_directory=str(tmp_path)),
    )


def test_guardrail_rejects_service_with_wrong_entity_name(tmp_path):
    service_dir = tmp_path / "services" / "order_service"
    (service_dir / "domain").mkdir(parents=True)
    (service_dir / "domain" / "order_service_entities.py").write_text(
        "class Product:\n    pass\n",
        encoding="utf-8",
    )

    requirement = _make_requirement(tmp_path)
    execution = ExecutionResult(
        agent_type=AgentType.EXECUTOR,
        status=ExecutionStatus.SUCCESS,
        output="generated",
        files_created=["services/order_service/domain/order_service_entities.py"],
    )

    import asyncio
    result = asyncio.run(ValidatorAgent(ApprovingProvider()).validate(requirement, execution))

    assert result.status == ValidationStatus.REJECTED
    assert any("sem entidade coerente" in issue for issue in result.issues)


def test_guardrail_rejects_emailstr_without_dependency(tmp_path):
    service_dir = tmp_path / "services" / "user_service"
    (service_dir / "api").mkdir(parents=True)
    (service_dir / "api" / "schemas.py").write_text(
        "from pydantic import BaseModel, EmailStr\n\nclass UserIn(BaseModel):\n    email: EmailStr\n",
        encoding="utf-8",
    )
    (service_dir / "requirements.txt").write_text("pydantic>=2.0\n", encoding="utf-8")

    requirement = _make_requirement(tmp_path)
    execution = ExecutionResult(
        agent_type=AgentType.EXECUTOR,
        status=ExecutionStatus.SUCCESS,
        output="generated",
        files_created=[
            "services/user_service/api/schemas.py",
            "services/user_service/requirements.txt",
        ],
    )

    import asyncio
    result = asyncio.run(ValidatorAgent(ApprovingProvider()).validate(requirement, execution))

    assert result.status == ValidationStatus.REJECTED
    assert any("EmailStr" in issue for issue in result.issues)


def test_guardrail_rejects_missing_frontend_when_requested(tmp_path):
    requirement = _make_requirement(tmp_path, description="Criar backend e frontend React")
    execution = ExecutionResult(
        agent_type=AgentType.EXECUTOR,
        status=ExecutionStatus.SUCCESS,
        output="generated",
        files_created=["services/user_service/main.py"],
    )

    import asyncio
    result = asyncio.run(ValidatorAgent(ApprovingProvider()).validate(requirement, execution))

    assert result.status == ValidationStatus.REJECTED
    assert any("frontend" in issue.lower() for issue in result.issues)


def test_validator_uses_live_file_snapshot_in_prompt(tmp_path):
    service_dir = tmp_path / "services" / "user_service"
    (service_dir / "api").mkdir(parents=True)
    (service_dir / "api" / "schemas.py").write_text(
        "class UserSchema:\n    pass\n",
        encoding="utf-8",
    )

    requirement = _make_requirement(tmp_path)
    execution = ExecutionResult(
        agent_type=AgentType.EXECUTOR,
        status=ExecutionStatus.SUCCESS,
        output="conteudo_antigo",
        files_created=["services/user_service/api/schemas.py"],
    )

    import asyncio
    provider = CapturingApprovingProvider()
    asyncio.run(ValidatorAgent(provider).validate(requirement, execution))

    assert "conteudo_antigo" not in provider.prompt
    assert "class UserSchema" in provider.prompt
