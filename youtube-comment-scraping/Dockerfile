FROM python:3.9

WORKDIR /app

COPY src/requirements.txt /app

RUN pip install -r requirements.txt

COPY src /app

CMD ["python", "main.py"]
