from agents.docker_test_agent import DockerTestAgent


def test_normalize_service_name_generates_lowercase_safe_identifier():
    agent = DockerTestAgent()

    assert agent._normalize_service_name("UserService") == "userservice"
    assert agent._normalize_service_name("Order-Service") == "order_service"
    assert agent._normalize_service_name("  Product Service  ") == "product_service"


def test_resolve_base_service_port_uses_safe_default(monkeypatch):
    monkeypatch.delenv("DOCKER_TEST_BASE_SERVICE_PORT", raising=False)

    agent = DockerTestAgent()

    assert agent._base_service_port == 18001


def test_resolve_base_service_port_reads_env_override(monkeypatch):
    monkeypatch.setenv("DOCKER_TEST_BASE_SERVICE_PORT", "28001")

    agent = DockerTestAgent()

    assert agent._base_service_port == 28001
