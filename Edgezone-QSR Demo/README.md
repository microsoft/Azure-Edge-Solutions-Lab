# Edgezone-QuickServiceResturant Lab

The EdgeZone Quick Service Resturant(QSR) Lab is intended to guide users in the implementation of a QSR distributed AI app scenario. The lab will take a simple Computer Vision app that has been deployed in an on-prem archicture using a container image and Kubernetes and then lift and shift the on-prem to an Azure EdgeZone. This lab will start with the traditional on-prem and the walk through detailed steps for lift and shift to Azure EdgeZone. https://azure.microsoft.com/en-us/solutions/public-multi-access-edge-compute-mec/#overview

On-prem is Store 1 which has a two node AzSHCI cluster with Kubernetes and ARC 
Azure Edge zone will also run AKS and ARC, but will be a cloud offereing located physcially close to Store 1

![image](https://user-images.githubusercontent.com/47536604/207954780-d8b06255-d483-4231-9090-d8eefa2eeb68.png)
![image](https://user-images.githubusercontent.com/47536604/207954839-ff205d65-8493-4b1c-b898-42dc919d3d0b.png)


### Major sections of this E2E tutorial:
1. Prerequisites
2. Preparing AKS in an Azure EdgeZone
3. Configuring ARC on Azure EdgeZone AKS
4. Reviewing Store 1 deployment on AKS on AkSHCI (on-prem)
5. Modify Store 1 deployment
6. Deploy to AKS on Azure EdgeZone
7. Validate E2E Solution Working
8. Cleanup Resources

## Prerequisites

Please refer to previous lab on setting up the two-node AzS HCI cluster and deploying AKS.
https://github.com/microsoft/Azure-Edge-Solutions-Lab#preparing-azshci---2-node-cluster
https://github.com/microsoft/Azure-Edge-Solutions-Lab#configuring-arc-and-aks-on-azshci

## 1. Preparing AKS in an Azure EdgeZone

In Azure Portal, open CLI and switch to Bash shell
	
az account set --subscription <Azure Subscription ID>
myAKSCluster=<your AKS cluster name>
myResourceGroup= <your resource group name>
	
az account set --subscription <Azure Subscription ID> 
az group create --location <resource group location> --resource-group $myResourceGroup 
  
az aks create --name $myAKSCluster --resource-group $myResourceGroup --kubernetes-version 1.22.11  --edge-zone <edge zone name> --location <edge zone loacation>


## 2. Configuring ARC on Azure EdgeZone AKS
https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli
 
1. Register providers with ARC service
2. Connect existing Kubernetes cluster, same variables from step 1 above.
			
az account set --subscription <Azure Subscription ID>
$myAKSCluster=<your AKS cluster name>
$myResourceGroup= <your resource group name>
		
az connectedk8s connect --name $myAKSCluster --resource-group $myResourceGroup

## 3. Reviewing Store 1 deployment on AKS on AkSHCI (on-prem)
## 4. Modify Store 1 deployment
## 5. Deploy to AKS on Azure EdgeZone
## 6. Validate E2E Solution Working
## 7. Cleanup Resources
