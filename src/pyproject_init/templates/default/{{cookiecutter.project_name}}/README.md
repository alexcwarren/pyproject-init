# `{{ cookiecutter.project_name }}`

{{ cookiecutter.project_short_description }}

## Getting Started

### Prerequisites

* Python {{ cookiecutter.python_version }} or later (recommended to use `pyenv` or similar for managing Python versions).
* [`Hatch`](https://hatch.pypa.io/latest/) for project management. Install it globally:

    ```shell
    pip install hatch
    ```

### Installation

1. **Clone the repository:**

    ```shell
    git clone [https://github.com/](https://github.com/){{ cookiecutter.user_name }}/{{ cookiecutter.project_slug }}.git
    cd {{ cookiecutter.project_slug }}
    ```

1. **Set up Hatch environment:**

    ```shell
    hatch env create
    ```

    This command will create a virtual environment (`.venv`) and install all project dependencies.

### Running the Project

You can run the main function using Hatch:

```shell
hatch run python src/{{ cookiecutter.project_slug }}/main.py
```

This should print "Hello, World!".

## Development

### Running Tests

To run tests for this project:

```shell
hatch run test
```

To run tests with coverage:

```shell
hatch run cov
```

### Linting and Formatting

To check for linting issues and formatting problems:

```shell
hatch run lint
```

To automatically format the code:

```shell
hatch run format
```

### Type Checking

To run static type checks using MyPy:

```shell
hatch run typecheck
```

### Running All Checks

To run all checks (lint, typecheck, test):

```shell
hatch run all
```
