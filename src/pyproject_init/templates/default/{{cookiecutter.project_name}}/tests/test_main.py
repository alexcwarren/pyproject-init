from {{ cookiecutter.project_slug }}.main import hello_world


def test_hello_world() -> None:
    """Test hello world."""
    assert hello_world() == "Hello, World!"
