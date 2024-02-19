FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

COPY src/requirements.txt /app

RUN pip install -r requirements.txt

COPY src /app

CMD ["python3", "scraping_rss.py"]
