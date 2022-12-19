# Flask Application

![video](static/video.gif)

## Introduction
The Flask application acts as a MQTT client and a Flask server. The AI inferencing container deployed as K8s pod communicates with this application via a POST request on /post_items_placement endpoint. The MQTT client publishes the inference action to the Business Logic application running in a K8s cluster on the edgezone. The Business Logic application process the inference action along with the corresponding order and sends back a result via MQTT. The Flask application renders this result on the Alerting UI/UX application as shown above.

## Preparing your image
1. Get the code for the BL application from this repository

`git clone https://github.com/microsoft/Azure-Edge-Solutions-Lab.git`

2. Navigate to "Edgezone-QSR Demo"/"Flask App" directory. This directory will have the Dockerfile required to create the container image. Build your image using docker and give it a tag.

`docker build tag <acrname>.azurecr.io/flask-app:v1 .`

3. Log in to your Azure Container Registry

`docker login -u <ACR username> -p <ACR password> <ACR login server>`

4. Push the created image to Azure Container Registry

`docker push <acrname>.azurecr.io/flask-app:v1`

## Creating a secret on K8s cluster

Run the following kubectl command on your K8s cluster

`kubectl create secret docker-registry <secret-name> --namespace <namespace> --docker-server=<container-registry-name>.azurecr.io --docker-username=<service-principal-ID> --docker-password=<service-principal-password>`

Once the secret is created you can use it in the yaml file-

```
imagePullSecrets:
    - name: acr-secret-edgezone
```
Look at the flask-app.yaml file in this directory for more information.

