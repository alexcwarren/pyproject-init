"""Main module for the {{ cookiecutter.project_name }} project."""


def hello_world() -> str:
    """Return a classic greeting."""
    return "Hello, World!"


def main() -> None:
    """Run the application."""
    print(hello_world())  # noqa: T201


if __name__ == "__main__":  # no cov
    main()
