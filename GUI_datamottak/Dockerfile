FROM python:3.8-slim-buster

# Install software
#RUN apt-get -y update
#RUN apt-get -y install git

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

#RUN git clone https://github.com/statisticsnorway/papis-service.git #/app/papis_service
#RUN git clone https://github.com/statisticsnorway/papis-pyffx.git #/app/papis_pyffx

COPY . .

EXPOSE 5010

ENTRYPOINT ["python3"]
CMD ["run.py"]