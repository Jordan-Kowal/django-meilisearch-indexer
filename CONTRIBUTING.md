# Contributing

## Setup

We use `uv` as our package manager.
To get started, follow these steps:

```shell
pip install uv
uv sync
. .venv/bin/activate
```

## QA

### Tests

The test suite is composed of both **unittests** and **integration tests** (ran against a local Meilisearch instance).
To start the meilisearch instance, simply run the following command:

```shell
docker-compose up
```

Then, you can run tests using either `unittest` or `coverage`.

With `unittest`:

```shell
python -m unittest discover .
```

With `coverage`:

```shell
coverage run -m unittest discover .
coverage report --fail-under=90
coverage html
```

In the CI, tests are run on multiple Python versions (from 3.9 to 3.13)
to ensure compatibility on each version.

### Using git hooks

Git hooks are set in the [.githooks](.githooks) folder
_(as `.git/hooks` is not tracked in `.git`)_

Run the following command to tell `git` to look for hooks in this folder:

```shell
git config core.hooksPath .githooks
```

Pre-commit hooks will run `ruff`, `mypy`, and `coverage` on each commit.
Make sure to have your **Meilisearch** instance running before committing.

### CI/CD

We use GitHub actions to verify, build, and deploy the application. We currently have:

- [code_quality](.github/workflows/code_quality.yml): runs `ruff`, `mypy`, and `coverage`
- [dependabot](.github/dependabot.yml): Dependabot configuration for frontend/backend dependencies
- [publish_package](.github/workflows/publish_package.yml): Deploys the package on PyPi
- [tests](.github/workflows/tests.yml): runs unittests on multiple Python versions (from 3.9 to 3.13)
