from infrastructure.file_manager import FileManager


def test_normalize_generated_prefixed_path(tmp_path):
    manager = FileManager(str(tmp_path / "generated"))
    assert str(manager._normalize_relative_path("generated/services/orders/main.py")) == "services/orders/main.py"


def test_create_file_with_prefixed_path(tmp_path):
    base = tmp_path / "generated"
    manager = FileManager(str(base))
    ok = manager.create_file("generated/services/orders/main.py", "print('ok')")
    assert ok
    assert (base / "services/orders/main.py").exists()
    assert not (base / "generated/services/orders/main.py").exists()
