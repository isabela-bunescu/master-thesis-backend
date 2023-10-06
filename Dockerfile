FROM python:3.9-slim

WORKDIR /app

ADD DataGenerator /app
ADD requirements.txt /app 
ADD flaskServer.py /app

ENV PYTHONUNBUFFERED 1
RUN pip3 install -r /app/requirements.txt

ENV DB_HOST=localhost
ENV DB_USER=
ENV DB_PASS=
ENV DB_PORT=27017

CMD ["python","flaskServer.py"]

EXPOSE 5000