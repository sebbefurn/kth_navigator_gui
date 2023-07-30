FROM python:3

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

CMD ["gunicorn", "api_test.wsgi:application", "--bind", "0.0.0.0:8000"]