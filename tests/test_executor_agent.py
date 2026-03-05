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
