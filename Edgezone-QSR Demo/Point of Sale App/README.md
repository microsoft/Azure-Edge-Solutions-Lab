# Point of Sale Application

Point of Sale (PoS) application is a MQTT client app written in Python that connects to a MQTT broker deployed on the Edgezone. The PoS app sends new orders to the Business Logic (BL) application running on the edge zone via MQTT publish messages.

A sample order would look as follows-
```json
{
    "bag_no" : 1, 
    "items" : [{
        "French Fries" : 1, 
        "Cheeseburger" : 1, 
        "Soda" : 1, 
        "Chicken Nuggets" : 1
        }]
}
```

## Preparing your image
1. Get the code for the BL application from this repository

`git clone https://github.com/microsoft/Azure-Edge-Solutions-Lab.git`

2. Navigate to "Edgezone-QSR Demo"/"Point of Sale App" directory. This directory will have the Dockerfile required to create the container image. Build your image using docker and give it a tag.

`docker build tag <acrname>.azurecr.io/pos-app:v1 .`

3. Log in to your Azure Container Registry

`docker login -u <ACR username> -p <ACR password> <ACR login server>`

4. Push the created image to Azure Container Registry

`docker push <acrname>.azurecr.io/pos-app:v1`

## Creating a secret on K8s cluster

Run the following kubectl command on your K8s cluster

`kubectl create secret docker-registry <secret-name> --namespace <namespace> --docker-server=<container-registry-name>.azurecr.io --docker-username=<service-principal-ID> --docker-password=<service-principal-password>`

Once the secret is created you can use it in the yaml file-

```
imagePullSecrets:
    - name: acr-secret-edgezone
```
Look at the BL-client.yaml file in this directory for more information.