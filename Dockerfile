# start from the official Python 3.11 image
FROM python:3.11

# set current working directory to /code
WORKDIR /code

# install Poetry
RUN pip install "poetry==1.6.1"

# copy only the requirements files (to take advantage of Docker cache)
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

# install dependencies
RUN poetry install
RUN poetry self add 'poethepoet[poetry_plugin]'

# copy Alembic files to create/migrate DB
COPY alembic.ini /code
COPY alembic /code/alembic
COPY start_server.sh /code

# copy the app inside the /code directory
COPY ./app /code/app

ENV PYTHONPATH /code

EXPOSE 8000

# run command to start Uvicorn server
# CMD ["poetry", "poe", "start"]
CMD [ "/bin/bash", "start_server.sh"]
