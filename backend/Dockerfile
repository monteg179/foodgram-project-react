FROM python:3.9

WORKDIR /app

RUN apt update && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "foodgram.wsgi"]