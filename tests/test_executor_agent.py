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
