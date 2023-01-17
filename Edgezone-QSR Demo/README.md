# Edgezone Quick Service Restaurant Lab

The EdgeZone Quick Service Restaurant (QSR) Lab is intended to guide users in the implementation of a QSR distributed AI app scenario. The lab will take a simple Computer Vision app that has been deployed in an on-prem archicture using a container image and Kubernetes and then lift and shift the on-prem to an Azure EdgeZone. This lab will start with the traditional on-prem and the walk-through detailed steps for lift and shift to Azure EdgeZone. https://azure.microsoft.com/en-us/solutions/public-multi-access-edge-compute-mec/#overview

On-prem is Store 1 which has a two node AzSHCI cluster with Kubernetes and ARC 
Azure Edge zone will also run AKS and ARC, but will be a cloud offering located physically close to Store 1.

Step 1 | Step 2 | Step 3 | Step 4 
-----|-----|-----|-----
![image](https://user-images.githubusercontent.com/47536604/212991641-0c7e182c-1665-4bfb-8634-7341d49302f6.png) | ![image](https://user-images.githubusercontent.com/47536604/212991772-8d60b298-a2fa-4d5a-b6b7-86c022d49bd9.png) | ![image](https://user-images.githubusercontent.com/47536604/212992057-a52daa70-c99b-4511-a571-53cb0bc3a522.png) | ![image](https://user-images.githubusercontent.com/47536604/212993518-de503e29-8270-4257-a265-ffa4217be8f6.png)




### Major sections of this E2E tutorial:
<!--Ordered List0-->
* Step 0. Prerequisites
* Step 1. Preparing AKS in an Azure EdgeZone
	* 1.a. Configuring ARC on Azure EdgeZone AKS
	* 1.b. Build Flask Web Application
	* 1.c. Build Point of Sale Application
	* 1.d Build Business Logic Application
	* 1.e. Deploy app modules to your edge K8s cluster
	* 1.f. Reviewing Store 1 deployment on AKS on AkSHCI (on-prem)
* Step 2. Modify Store 1 deployment
* Step 3. Deploy to AKS on Azure EdgeZone
* Step 4. Validate E2E Solution Working
* Step 5. Cleanup Resources

## Step 0. Prerequisites

Please refer to previous lab on setting up the two-node AzS HCI cluster and deploying AKS.

https://github.com/microsoft/Azure-Edge-Solutions-Lab#preparing-azshci---2-node-cluster

https://github.com/microsoft/Azure-Edge-Solutions-Lab#configuring-arc-and-aks-on-azshci

## Step 1. Preparing AKS in an Azure EdgeZone

Azure Edge Zone with Operators (Public MEC) is Generally Availalbe and allows Customers to development distributed applications across cloud, on-premises, and edge using the same Azure Portal, APIs, development, and security tools. ![image](https://user-images.githubusercontent.com/47536604/212989224-d3a5d81f-a28b-4add-88d2-859bda1e7c46.png)


In Azure Portal, open CLI and switch to Bash shell
	
`az account set --subscription <Azure Subscription ID> myAKSCluster=<your AKS cluster name> myResourceGroup=<your resource group name>`
	
`az account set --subscription <Azure Subscription ID>` 

`az group create --location <resource group location> --resource-group $myResourceGroup`
  
`az aks create --name $myAKSCluster --resource-group $myResourceGroup --kubernetes-version 1.22.11  --edge-zone <edge zone name> --location <edge zone loacation>`


### Step 1.a. Configuring ARC on Azure EdgeZone AKS
https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli
 
1. Register providers with ARC service
2. Connect existing Kubernetes cluster, same variables from step 1 above.
			
`az account set --subscription <Azure Subscription ID>`

`$myAKSCluster=<your AKS cluster name>`

`$myResourceGroup= <your resource group name>`
		
`az connectedk8s connect --name $myAKSCluster --resource-group $myResourceGroup`

### Step 1.b. Build Flask Web Application
1. Go to the `Flask App` folder and complete the steps in the README to prepare your Flask-app image. Make sure you push the image to your Azure container registry. Get the path to this container which will be as follows - `<acr name>.azurecr.io/flask-app:v1`
2. Make a note of your `Login Server`, `Username` and `password` from your Azure Container Registry.
3. Go back to the `Flask App` folder and create a secret on K8s cluster following the steps in the README. Make a note of the name of your secret. 
4. Open the `on-prem-deployment.yaml` file and find the deployment for the Flask Web application and update the `<path-to-container>` with the path from step 1. Now update the `<name-of-secret-required-if-container-pull-needs-username-password>` with the name of the secret you created in step 3. 

#### Step 1.c. Build Point of Sale Application
1. Go to the `Point of Sale App` folder and complete the steps in the README to prepare your pos-app image. Make sure you push the image to your Azure container registry. Get the path to this container which will be as follows - `<acr name>.azurecr.io/pos-app:v1`
2. Make a note of your `Login Server`, `Username` and `password` from your Azure Container Registry.
3. Go back to the `Point of Sale App` folder and create a secret on K8s cluster following the steps in the README. Make a note of the name of your secret. 
4. Open the `on-prem-deployment.yaml` file and update the `<path-to-container>` with the path from step 1. Now update the `<name-of-secret-required-if-container-pull-needs-username-password>` with the name of the secret you created in step 3. 

#### Step 1.d Build Business Logic Application
1. Go to the `Business Logic App` folder and complete the steps in the README to prepare your pos-app image. Make sure you push the image to your Azure container registry. Get the path to this container which will be as follows - `<acr name>.azurecr.io/bl-client:v1`
2. Make a note of your `Login Server`, `Username` and `password` from your Azure Container Registry.
3. Go back to the `Business Logic App` folder and create a secret on K8s cluster following the steps in the README. Make a note of the name of your secret. 
4. Open the `on-prem-deployment.yaml` file and update the `<path-to-container>` with the path from step 1. Now update the `<name-of-secret-required-if-container-pull-needs-username-password>` with the name of the secret you created in step 3.

### Step 1.e. Deploy app modules to your edge K8s cluster
Next we will deploy the Flask, Point of Sale, and Business Logic modules to AKS. Run the following command on your edge K8s cluster -

`kubectl create -f on-prem-deployment.yaml`

This will create all the required pods and services within the cluster.

Run the following command on your edge K8s cluster to get the IP address to access the frontend UI/UX 

`kubectl get svc --all-namespaces`

From all the results copy the `EXTERNAL-IP` of `contoso-webapp-service`. Open a web browser window and go to `http://<EXTERNAL-IP>:5000` 

Run the following command to delete the on-prem deployment

`kubectl delete -f on-prem-deployment.yaml`


### Step 1.f. Reviewing Store 1 deployment on AKS on AkSHCI (on-prem)
The on-prem deployment is on your K8s cluster deployed at the Edge (Store 1). The deployment consists of the following components-
1. Flask Web application - sink for incoming inference and result data.
2. EdgeAI Applicaiton - container trained on the order accuracy model.
3. Business Logic Application - analyzes inference data and sends back results to the Flask web server.
4. Point of Sale Application - sends orders to Flask web application and Business Logic Application.


## Step 2. Deploy to AKS on Azure EdgeZone
For this deployment you will remove the `Business Logic Application` from the edge and move it the edgezone. 

Open the `edgezone-deployment.yaml` file and update the `<path-to-container>` with the path to the Business Logic App from section 3. Now update the `<name-of-secret-required-if-container-pull-needs-username-password>` with the name of the secret you created for the Business Logic App in section 3.

Go to the edgezone K8s cluster and run the following command to deploy the `Business Logic Application` -

`kubectl create -f edgezone-deployment.yaml`

## Step 3. Modify Store 1 deployment
Open the `edge-deployment.yaml` file and update the `<path-to-container>` and `<name-of-secret-required-if-container-pull-needs-username-password>` with the values you created for all applications in section 3.

Go to the edge K8s cluster and run the following command to deploy `Flask App`, `edgeAI` and `Point of Sale App` -

`kubectl create -f edge-deployment.yaml`

## Step 4. Validate E2E Solution Working
Run the following command on your edge K8s cluster to get the IP address to access the frontend UI/UX 

`kubectl get svc --all-namespaces`

From all the results copy the `EXTERNAL-IP` of `contoso-webapp-service`. Open a web browser window and go to `http://<EXTERNAL-IP>:5000`

## 7. Configure GitOps (Optional)
In this section you will configure GitOps. GitOps is an operational framework for Kubernetes cluster management and application delivery. GitOps applies development practices like version control, collaboration, compliance, and continuous integration/continuous deployment (CI/CD) to infrastructure automation.

1. Go to your K8s cluster on the Azure Portal. On the left column select `GitOps` under `Settings`, then click `Create`. This will initiate the GitOps configuration creation process.
2. On the `Basics` tab give the configuration a name under `Configuration name`. For `Namespace` use `contoso` as that is what we have used in all the files provided in this repository. The `scope` is `Namespace`. Leave everthing else unchanged and click `Next`.
3. On the `Source` tab enter the GitHub `Repository URL` that you want to configure. Specify the `Reference Type` as `Branch` and for `Branch` add the branch name to monitor. Specify the `Repository type` as either `Private` or `Public` depending on your GitHub repository. Under `Sync configuration` change `Sync interval (minutes)` to `1`. Now click `Next`.
4. On the `Kustomization` tab click `+ Create`, this will open a section on the right. Give your kustomization a name under `Instance name`. For `Path`, add the complete path location to the YAML configuration, for example `./contoso-app/yaml-file`. Enable `Prune`. Leave everything else unchanged and click `Save`, then click `Next`.
5. On the `Review + create` tab, verify all fields are as mentioned, then click `Create`. In a few moments the GitOps configuration will be created.
6. Once the GitOps configuration is successfully created you can make changes to the YAML file and verify that this triggers a new deployment, old pods are stopped and new ones are created depending on the changes that were made.  

## Step 5. Cleanup Resources
1. Delete all your deployments via `K8s - Azure Arc` on the `Azure Portal`.
2. Delete the K8s clusters from Windows Admin Center (WAC).
