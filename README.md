# Reference Solution - EdgeAI running on AzS HCI using AKS and Arc

This refrence solution is inteneded to give customers and partners an example of how one can deploy and manage an Edge AI workload by leverageing certified AzS HCI hardware and using AKS and ARC.  

<img width="411" alt="image" src="https://user-images.githubusercontent.com/47536604/193682639-d53a6a1c-8953-4cce-8341-32e1f9ffc574.png">

### Major sections of this E2E tutorial:
* Prerequesits
* Preparing AzSHCI - 2 node cluster
* Configuring ARC and AKS on AzSHCI
* Creating AI Workload AKS Cluster
* Integrating with GitHub
* Deploy AI Workload
* Validate E2E Solution Working
* Cleanup Resources


# Prerequesits
For this E2E refrence solution you would need the following prerequisits:
* 2 - node cluster [Deploy a 2-node cluster on AzSHCI](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/create-cluster?tabs=use-network-atc-to-deploy-and-manage-networking-recommended)
* [Azure subscription](https://azure.microsoft.com/free)
* [Windows Admin Center](https://azure.microsoft.com/en-us/contact/azure-stack-hci/) 

# Preparing AzSHCI - 2 node cluster
Follow the Microsoft Learn documentation to set up Windows Admin Center (WAC)
[Quickstart setup AzSHCI with WAC](https://learn.microsoft.com/en-us/azure-stack/hci/get-started)

Follow the Microsoft Learn documents to configure your two node cluster:
[Deploy a 2-node cluster on AzSHCI](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/create-cluster?tabs=use-network-atc-to-deploy-and-manage-networking-recommended)

# Configuring ARC and AKS on AzSHCI
When setting up AKS you will perform the steps to initally set up the AKS Management cluster and reserve IPs for all the Worker Clusters, then you will proceed to step below _Creating AI Workload AKS Cluster_. Work with your networking engineers to reserve a block of IP addressess and ensure you have vSwitch created. Gateway and DNS Servers can be found by looking at setting of the vSwitch in WAC. 
## Here is the Engineering Plan used for our E2E Demo:

> 
> Subnet prefix: 172.23.30.0/24
> Gateway: 172.23.30.1
> DNS Servers:
>	172.22.1.9
>	172.22.3.9
> Cloud agent IP – 172.23.30.151
> Virtual IP address pool start – 172.23.30.152
> Virtual IP address pool end – 172.23.30.172
> Kubernetes node IP pool start – 172.23.30.173
> Kubernetes node IP pool end – 172.23.30.193
> 

1. Prepare the 2-node cluster by installing AKS, follow this [Powershell QuickStart Guide](https://learn.microsoft.com/en-us/azure/aks/hybrid/kubernetes-walkthrough-powershell)
2. Alterntaivitally, you could setup with WAC. The demo was created with Static-IPs from above Engineering plan. [AKS using WAC](https://learn.microsoft.com/en-us/azure/aks/hybrid/setup)


# Creating AI Workload AKS Cluster
Now that you have AKS and ARC installed in your management cluster. You need to create a AI Workload cluster and prime the nodes to leverage the AI Accelerator hardware. 
## Create AI Workload Cluster
Follow [instructions](https://learn.microsoft.com/en-us/azure/aks/hybrid/create-kubernetes-cluster) to create an cluster named: AI Workload
We stood up a 3 node AKS cluster.

## Create a GPU Pool and attach GPUs to AI Workload Nodes
Once your AI Workload cluster is created, go to WAC Cluster Manager and look at VM list. Take note of VM names for the AI Workload. 
Follow [these steps](https://learn.microsoft.com/en-us/azure-stack/hci/manage/use-gpu-with-clustered-vm) to create a GPU Pool in WAC and assign the VMs from the AI Workload Cluster. 

## Preparing node for AI workload
Now that we have the GPUs assigned, we need to install Docker and the Nvidia plug-in. 
1.Go to Docker page and find your respective binary. For this example we use x86_64 docker-20.10.9.tgz.
[Docker binaries](https://docs.docker.com/engine/install/binaries/#install-static-binaries)

2. Get the Workload AI node IP address and connect using your rsa. When using WAC, these will be placed in your Cluster storage under volumes then AksHCI. You can run this from your dev machience command prompt, but ensure you are in the same folder as the rsa file. For command below we copied out the rsa file to dev machiene and renamed to _akshci_rsa.xml_. Learn more at [Connect with SSH to Linux or Windows worker nodes](https://learn.microsoft.com/en-us/azure/aks/hybrid/ssh-connection)
```shell
ssh -i akshci_rsa.xml clouduser@172.23.30.157
```

3. Once on the Workload AI node, download the docker binary.
```bash
sudo curl https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz -o docker-20.10.9.tgz
```

4. Inflate docker binaries.
```bash
sudo tar xzvf docker-20.10.9.tgz
```

5. Remove any running files.
```bash
sudo rm -rf '/usr/bin/containerd' 
sudo rm -rf '/usr/bin/containerd-shim-runc-v2'
``` 
	
6. Copy the binaries to your clouduser location. 
```bash
sudo cp docker/* /usr/bin/ 
```

7. Run docker in background.
```bash
sudo dockerd & 
```
	
8. Installing the Nvidia GPU plugin. Go to Nvidia page for full set of instructions. 
[GitHub - NVIDIA/k8s-device-plugin: NVIDIA device plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin#preparing-your-gpu-nodes)

9. Update docker as default runtime by createing daemon.json
```bash
sudo vim /etc/docker/daemon.json
```

10. Paste into newly created daemon.json file
```json
{
    "default-runtime": "nvidia",
     "runtimes": {
         "nvidia": {
             "path": "/usr/bin/nvidia-container-runtime",
             "runtimeArgs": []
         }
     }
}
```

11. Ceck to ensure changes took.
```bash
sudo cat /etc/docker/daemon.json
```
	
12. Remove running files and restart docker
```bash
sudo rm /var/run/docker.pid 
sudo rm -rf /var/lib/docker/volumes/*
sudo dockerd &
```


12. Configure containerd. Open the config.toml file and paste in modification from step 13.
<blockquote> sudo vim /etc/containerd/config.toml  </blockquote>

13. Paste into file
```json
version = 2
 [plugins]
   [plugins."io.containerd.grpc.v1.cri"]
     [plugins."io.containerd.grpc.v1.cri".containerd]
       default_runtime_name = "nvidia"

       [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
         [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
           privileged_without_host_devices = false
           runtime_engine = ""
           runtime_root = ""
           runtime_type = "io.containerd.runc.v2"
           [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
            BinaryName = "/usr/bin/nvidia-container-runtime"
```
14. Check to ensure changes took.
```bash
sudo cat /etc/containerd/config.toml
```

15. Restart containerd
```bash
sudo systemctl restart containerd
```

16. Optional troubleshooting:
```bash
sudo systemctl stop containerd
sudo systemctl start containerd
sudo containerd
``` 
	
17. From powershell in the kubectl command line. Enabeling GPU supporting in k8. 

Run deployment
```bash
kubectl apply -f edge-ai1.yaml
```
Run nvidia plugin
```bash
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.yml 
```
	

# Integrating with GitHub
# Deploy AI Workload
# Validate E2E Solution Working
### go to VCL and see inferencing results
rtsp://172.23.30.162:30007/ds-test 

# Cleanup Resources

	



### Configuring ARC and integration with GitHub


### Deploying Edge AI workload



## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
