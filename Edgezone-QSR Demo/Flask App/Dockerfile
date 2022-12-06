FROM python:3
WORKDIR /flaskapp-docker
RUN pip install flask-mqtt
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]