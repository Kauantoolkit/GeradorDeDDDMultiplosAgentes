from agents.docker_test_agent import DockerTestAgent


def test_normalize_service_name_generates_lowercase_safe_identifier():
    agent = DockerTestAgent()

    assert agent._normalize_service_name("UserService") == "userservice"
    assert agent._normalize_service_name("Order-Service") == "order_service"
    assert agent._normalize_service_name("  Product Service  ") == "product_service"
