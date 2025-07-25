# pyproject-init

A powerful CLI tool to automate the creation of new Python projects, pre-configured with modern best practices.

`pyproject-init` aims to streamline the setup of Python projects by integrating:

* **Hatch:** For robust project management, build system, and environment handling.
* **`pytest` & `pytest-randomly`:** For comprehensive testing and ensuring test stability.
* **Ruff:** For lightning-fast code linting and formatting.
* **MyPy:** For static type checking to improve code quality.
* **GitHub Actions:** For automated Continuous Integration (CI/CD) workflows.

## Installation (for Users)

Users can install `pyproject-init` via pip:

```bash
pip install pyproject-init
```

## Usage (for Users)

Once installed, you can use the pyproject-init CLI:

```bash
pyproject-init new [PROJECT_NAME] --output-dir <path> --template <name>
```

Example:

```bash
# Create a new project interactively in the current directory
pyproject-init new

# Create a new project named 'my-cool-app' in a specific directory
pyproject-init new my-cool-app --output-dir C:\Users\YourUser\Documents\NewProjects

# Create a new project using default values without prompts
pyproject-init new --no-input
```

## Development (for Contributors/Maintainers)

To contribute to or develop pyproject-init itself:

1. Clone this repository:

    ```PowerShell
    git clone [https://github.com/your-username/pyproject-init.git](https://github.com/your-username/pyproject-init.git)
    cd pyproject-init
    ```

1. Install Hatch and set up the development environment:
Ensure you have Python 3.10.5 (or compatible) installed via pyenv and set locally:

    ```PowerShell
    pyenv install 3.10.5
    pyenv local 3.10.5
    pip install hatch
    hatch env create
    ```

1. Run Development Checks:

    ```PowerShell
    hatch run all # Runs linting, type checking, and tests for the CLI tool's code
    ```

1. Run the CLI tool locally during development:

    ```PowerShell
    # This executes your 'new' command directly within the Hatch environment
    hatch run pyproject-init new my-dev-project-test
    # Or interactively:
    hatch run pyproject-init new
    ```

## Project Structure (for Developers)

* `src/pyproject_init/`: Contains the Python source code for the pyproject-init CLI application.
  * `src/pyproject_init/cli.py`: The main Click CLI application.
  * `src/pyproject_init/templates/` (Future): Will hold the Cookiecutter template files that the CLI tool uses.
* `tests/`: Contains unit tests for the pyproject-init CLI application's own code.
* `pyproject.toml`: Project metadata, dependencies, and Hatch configuration for the pyproject-init CLI tool itself.
* `.github/workflows/`: GitHub Actions workflows for the pyproject-init CLI tool's CI/CD.

> * **Remember to update `your-username` in the `README.md`!**
