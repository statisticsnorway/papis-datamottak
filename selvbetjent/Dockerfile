FROM python:3.8

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001
#ENV FLASK_APP run.py
ENTRYPOINT ["python"]
CMD ["run.py"]
#CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]