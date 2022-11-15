FROM python:3.10

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python", "scheduler.py"]