from types import SimpleNamespace

from agents.executor_agent import ExecutorAgent
from infrastructure.file_manager import FileManager


class DummyProvider:
    async def generate(self, *args, **kwargs):
        return "{}"


def test_create_project_files_supports_bounded_contexts(tmp_path):
    agent = ExecutorAgent(DummyProvider())
    fm = FileManager(str(tmp_path))
    config = SimpleNamespace(framework="fastapi", database="postgresql", include_docker=False, include_tests=False)

    data = {
        "bounded_contexts": [
            {
                "name": "orders",
                "files": [
                    {"path": "services/orders/main.py", "content": "app = 'ok'"}
                ],
            }
        ]
    }

    created = agent._create_project_files(fm, data, config)

    assert "services/orders/main.py" in created
    assert (tmp_path / "services/orders/main.py").exists()


def test_generated_main_and_routes_use_absolute_imports():
    agent = ExecutorAgent(DummyProvider())

    main_content = agent._generate_main("orders", SimpleNamespace())
    routes_content = agent._generate_routes("orders", "orders", ["Order"])

    assert "from api.routes import router" in main_content
    assert "from .api.routes import router" not in main_content
    assert "from application.use_cases import" in routes_content
    assert "from infrastructure.repositories import" in routes_content
    assert "from api.controllers import" in routes_content


def test_generated_docker_compose_pins_postgres_version():
    agent = ExecutorAgent(DummyProvider())

    compose_content = agent._generate_docker_compose("orders", "postgresql")

    assert "image: postgres:16" in compose_content


def test_generation_guards_add_missing_uvicorn_dependency():
    agent = ExecutorAgent(DummyProvider())

    guarded = agent._apply_generation_guards(
        "services/user_service/requirements.txt",
        "fastapi\nsqlalchemy\n",
    )

    assert "uvicorn>=0.24.0" in guarded


def test_generation_guards_fix_invalid_docker_cmd_quotes():
    agent = ExecutorAgent(DummyProvider())

    raw = """FROM python:3.9-slim
CMD ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000']
"""
    guarded = agent._apply_generation_guards("services/user_service/Dockerfile", raw)

    assert "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" in guarded


def test_generate_domain_and_layers_avoid_circular_import_patterns():
    agent = ExecutorAgent(DummyProvider())

    structure = agent._generate_ddd_structure(
        service_name="orders",
        domain="orders",
        microservice={"entities": ["Order"]},
        config=SimpleNamespace(database="postgresql", include_docker=False, include_tests=False),
    )

    domain_init = structure["services/orders/domain/__init__.py"]
    aggregates = structure["services/orders/domain/orders_aggregates.py"]
    use_cases = structure["services/orders/application/use_cases.py"]

    assert "from domain import" not in domain_init
    assert "from . import Order" not in aggregates
    assert "from .orders_entities import Order" in aggregates
    assert "from domain.orders_entities import Order" in use_cases


def test_sanitize_generated_content_fixes_known_circular_imports():
    agent = ExecutorAgent(DummyProvider())

    raw = """from domain import Order, Product, User
from . import User
"""
    fixed = agent._sanitize_generated_content("services/users/domain/__init__.py", raw)

    assert "from domain import" not in fixed
    assert "from .users_entities import User" in fixed


def test_normalize_llm_data_converts_list_to_microservices():
    agent = ExecutorAgent(DummyProvider())

    normalized = agent._normalize_llm_data([{"name": "orders"}])

    assert normalized["microservices"] == [{"name": "orders"}]
    assert normalized["files"] == []
    assert normalized["bounded_contexts"] == []


def test_normalize_llm_data_rejects_invalid_types():
    agent = ExecutorAgent(DummyProvider())

    try:
        agent._normalize_llm_data("invalid")
        assert False, "Expected ValueError for invalid type"
    except ValueError as exc:
        assert "Formato inválido" in str(exc)


def test_create_project_files_ignores_extra_files_outside_allowed_scope(tmp_path):
    agent = ExecutorAgent(DummyProvider())
    fm = FileManager(str(tmp_path))
    config = SimpleNamespace(framework="fastapi", database="postgresql", include_docker=False, include_tests=False)

    data = {
        "microservices": [],
        "files": [
            {"path": "microservico-de-pedidos/application/use_cases.py", "content": "def broken(:\n    pass"},
            {"path": "services/orders/main.py", "content": "app = 'ok'"},
        ],
        "bounded_contexts": [],
    }

    created = agent._create_project_files(fm, data, config)

    assert "services/orders/main.py" in created
    assert "microservico-de-pedidos/application/use_cases.py" not in created
    assert not (tmp_path / "microservico-de-pedidos/application/use_cases.py").exists()


def test_normalize_microservice_specs_sanitizes_names_and_entities():
    agent = ExecutorAgent(DummyProvider())

    normalized = agent._normalize_microservice_specs([
        {
            "name": "Microserviço de Usuários",
            "domain": "Usuários-App",
            "entities": ["usuario perfil", "123item", ""],
        }
    ])

    assert normalized[0]["name"] == "microservi_o_de_usu_rios"
    assert normalized[0]["domain"] == "usu_rios_app"
    assert normalized[0]["entities"] == ["UsuarioPerfil", "Entity123item"]


def test_normalize_microservice_specs_deduplicates_after_normalization():
    agent = ExecutorAgent(DummyProvider())

    normalized = agent._normalize_microservice_specs([
        {"name": "order-service", "domain": "orders", "entities": ["Order"]},
        {"name": "order_service", "domain": "orders", "entities": ["Order"]},
    ])

    assert len(normalized) == 1
    assert normalized[0]["name"] == "order_service"
