# Edgezone-QuickServiceResturant Lab

The EdgeZone Quick Service Resturant(QSR) Lab is intended to guide users in the implementation of a QSR distributed AI app scenario. The lab will take a simple Computer Vision app that has been deployed in an on-prem archicture using a container image and Kubernetes and then lift and shift the on-prem to an Azure EdgeZone. This lab will start with the traditional on-prem and the walk through detailed steps for lift and shift to Azure EdgeZone. 

On-prem is Store 1 which has a two node AzSHCI cluster with Kubernetes and ARC 
Azure Edge zone will also run AKS and ARC, but will be a cloud offereing located physcially close to Store 1

![arch1](Resources/edgezone-qsr-demo-architecture.png)
![arch2](Resources/edgezone-qsr-demo-architecture-2.png)

### Major sections of this E2E tutorial:
* Prerequisites
* Preparing AKS in an Azure EdgeZone
* Configuring ARC on Azure EdgeZone AKS
* Reviewing Store 1 deployment on AKS on AkSHCI (on-prem)
* Modify Store 1 deployment
* Deploy to AKS on Azure EdgeZone
* Validate E2E Solution Working
* Cleanup Resources

