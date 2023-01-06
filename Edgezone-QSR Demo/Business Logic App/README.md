# Business Logic Application

Business Logic (BL) application is a MQTT client app written in Python that connects to a MQTT broker deployed on the Edgezone. The BL app accepts new orders from the Point of Service (PoS) application and inference results from the Edge AI container both via MQTT topics. It then compares the two inputs to determine if the correct item is being added.  

There are six business scenarios we have accounted for in this client:
1. A new Customers' order is created in POS system and needs to be fulfilled
2. Item being added in the bag matches the POS order
3. Item being added in the bag does not match the POS order
4. Item being removed from the bag matches the POS order
5. Item being removed from the bag does not match the POS order
6. The order has been fulfilled and ready to give to customer

The following image depects the processes logic.
![image](https://user-images.githubusercontent.com/47536604/210615521-8f4e45d6-132a-4e6e-862b-f1c3c18f9353.png)

A sample order would look as follows:
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
A sample inference result/action:
```json
{
    "bag_no": 1, 
    "item_name": "soda", 
    "action": "add"
}
```
The BL application will process the incoming inference and the corresponding order. It will determine a Status True or False for the current action (**True** meaning the action is correct and **False** meaning the action is incorrect). The BL will publish the processed JSON to the flask server via MQTT topic.
A sample post-processed JSON would look as follows:
```json
{
    "bag_no": 1, 
    "item_name": "soda", 
    "action": "add",
    "status": True
}
```

The business logic client will process the six use cases and return the following responses:
| Use Case | BL Result |
| --------------- | --- |
| 1. A new Customers' order is created in POS system and is in need of being fulfilled | No result returned |
| 2. Item being added in the bag matches the POS order | TRUE |
| 3. Item being added in the bag does not match the POS order | FALSE |
| 4. Item being removed from the bag matches the POS order | FALSE |
| 5. Item being removed from the bag does not match the POS order | TRUE |
| 6. The order has been fulfilled and ready to give to customer | "order-complete" |


## Preparing your image
1. Get the code for the BL application from this repository

`git clone https://github.com/microsoft/Azure-Edge-Solutions-Lab.git`

2. Navigate to "Edgezone-QSR Demo"/"Business Logic App" directory. This directory will have the Dockerfile required to create the container image. Build your image using docker and give it a tag.

`docker build tag <acrname>.azurecr.io/bl-client:v1 .`

3. Log in to your Azure Container Registry

`docker login -u <ACR username> -p <ACR password> <ACR login server>`

4. Push the created image to Azure Container Registry

`docker push <acrname>.azurecr.io/bl-client:v1`

## Creating a secret on K8s cluster

1. Run the following kubectl command on your K8s cluster

`kubectl create secret docker-registry <secret-name> --namespace <namespace> --docker-server=<container-registry-name>.azurecr.io --docker-username=<service-principal-ID>     --docker-password=<service-principal-password>`

2. Once the secret is created you can use it in the yaml file-

```
imagePullSecrets:
    - name: acr-secret-edgezone
```
Look at the BL-client.yaml file in this directory for more information.

## Deploy the BL-client application to K8s Cluster

### Option 1: From PowerShell/Command Line
Using the kubectl command on the K8s cluster running on the edgezone

`kubectl apply -f BL-client.yaml`

### Option 2: From Azure Arc
Navigate into the cluster pods. Click add new pod and paste in the BL-client.yaml code. Submit.






