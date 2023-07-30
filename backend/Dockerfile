FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 8000

CMD ["gunicorn", "api_test.wsgi", "-b", "0.0.0.0:8000"]
