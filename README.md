# Quiz App
Quiz app using FastAPI.

## Setup
This project uses [Poetry](https://python-poetry.org/) for dependency management.
```bash
$ curl -sSL https://install.python-poetry.org | python3 -   # install Poetry
$ poetry install                                            # install project dependencies using Poetry
```

Poetry is also used to run different commands to start the server or run tests, which requires installing the [Poe the Poet](https://poethepoet.natn.io/index.html) task runner. Poe the Poet is already added as a dependency in the `pyproject.toml` file, so it should have been installed with the `poetry install` command, but the separate [Poetry plugin](https://poethepoet.natn.io/poetry_plugin.html) must also be added.

```
$ poetry self add 'poethepoet[poetry_plugin]'
```

At this point, the following commands can be run:
```bash
$ poetry poe start      # run Uvicorn server
$ poetry poe test       # run testcases
$ poetry poe lint       # run Ruff linter
$ poetry poe format     # format code with Ruff
$ poetry poe precommit  # run pre-commit hooks
```

More arguments can be added to the base commands, for example `poetry poe start --reload`.

There are also [pre-commit hooks](https://pre-commit.com/) configured to run the [Ruff](https://github.com/astral-sh/ruff) linter and code formatter. To install them, run `pre-commit install`.

## Run with Docker

1. Build the image (`-t` to tag the image).
```bash
$ docker build -f docker/Dockerfile -t fastapi_quiz .
```
2. Run the container (`-d` for detached mode to run the container in the background, `-p HOST:CONTAINER` to map the ports).
```bash
$ docker run -d -p 8000:8000 --name fastapi_cont fastapi_quiz
```
3. The app can now be accessed from http://0.0.0.0:8000 (docs at http://0.0.0.0:8000/docs).
4. Access app logs (`-f` to follow the logs).
```bash
$ docker logs fastapi_cont -f
```
