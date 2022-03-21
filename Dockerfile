FROM python:3.9 as base

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


FROM base as dev

COPY ./requirements-dev.txt /code/requirements-dev.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements-dev.txt
COPY ./tests /code/tests
COPY ./mypy.ini /code/mypy.ini
