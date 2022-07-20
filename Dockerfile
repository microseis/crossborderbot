FROM python:3.9-alpine

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir "/app"

COPY . /app

WORKDIR /app

CMD ["python", "main.py"]
