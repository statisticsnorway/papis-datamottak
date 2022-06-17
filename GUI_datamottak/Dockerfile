FROM python:3.8-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5010

ENTRYPOINT ["python3"]
CMD ["run.py"]