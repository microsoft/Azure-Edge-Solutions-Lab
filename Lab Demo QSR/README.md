# Reference Solution - EdgeAI running on AzS HCI using AKS and Arc

This reference solution is intended to give customers and partners an example of how one can deploy and manage an Edge AI workload by leveraging [certified AzSHCI hardware](https://azurestackhcisolutions.azure.microsoft.com/#/catalog) and using [AKS](https://learn.microsoft.com/en-us/azure/aks/hybrid/) and [ARC](https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/overview).  

<img width="411" alt="image" src="https://user-images.githubusercontent.com/47536604/193682639-d53a6a1c-8953-4cce-8341-32e1f9ffc574.png">

### Major sections of this E2E tutorial:
1. Prerequisites
2. Preparing AzSHCI - 2 node cluster
3. Configuring ARC and AKS on AzSHCI
4. Creating AI Workload AKS Cluster
5. Integrating with GitHub
6. Deploy AI Workload
7. Validate E2E Solution Working
8. Cleanup Resources


# 1. Prerequisites
For this E2E reference  solution you would need the following prerequisites:
* 2 - node cluster [Deploy a 2-node cluster on AzSHCI](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/create-cluster?tabs=use-network-atc-to-deploy-and-manage-networking-recommended)
* [Azure subscription](https://azure.microsoft.com/free)
* [Windows Admin Center](https://azure.microsoft.com/en-us/contact/azure-stack-hci/) 

# 2. Preparing AzSHCI - 2 node cluster
Follow the Microsoft Learn documentation to set up Windows Admin Center (WAC)
[QuickStart setup AzSHCI with WAC](https://learn.microsoft.com/en-us/azure-stack/hci/get-started)

Follow the Microsoft Learn documents to configure your two-node cluster:
[Deploy a 2-node cluster on AzSHCI](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/create-cluster?tabs=use-network-atc-to-deploy-and-manage-networking-recommended)

# 3. Configuring ARC and AKS on AzSHCI
When setting up AKS you will perform the steps to initially set up the AKS Management cluster and reserve IPs for all the Worker Clusters, then you will proceed to step below _Creating AI Workload AKS Cluster_. Work with your networking engineers to reserve a block of IP addresses and ensure you have vSwitch created. Gateway and DNS Servers can be found by looking at setting of the vSwitch in WAC. Below is an example when configuring with Static IP. 
## Here is the Engineering Plan used for our E2E Lab:

> 
> **Host configuration**
> 
> Management cluster name:	aks-management-cluster-1
> 
> Folder to store VM images:                C:\ClusterStorage\Volume01
> 
> Virtual network name:                        aks-default-network
> 
> Internet-connected virtual switch:   lab-Vswitch
> 
> VLAN ID                                                  0
> 
> Cloudagent IP                                       172.23.30.151
> 
> IP address allocation method            Static (Recommended)
> 
> Subnet prefix                                        172.23.30.0/24
> 
> Gateway                                                172.23.30.1
> 
> DNS servers                                          172.22.1.9,172.22.3.9
> 
> Virtual IP pool start                             172.23.30.152
> 
> Virtual IP pool end                              172.23.30.172
> 
> Kubernetes node IP pool start          172.23.30.173
> 
> Kubernetes node IP pool end           172.23.30.193
> 
> MAC address allocation                     Automatic
>
> *Azure registration*
> 
> Azure subscription                            myAzureSubName
> 
> Resource group                                 edgeaiDemo2
>
>


1. Prepare the 2-node cluster by installing AKS, follow this [PowerShell QuickStart Guide](https://learn.microsoft.com/en-us/azure/aks/hybrid/kubernetes-walkthrough-powershell)
2. Alternatively, you could setup with WAC. The demo was created with Static-IPs from the above Engineering plan. [AKS using WAC](https://learn.microsoft.com/en-us/azure/aks/hybrid/setup). Aside form Engineering plan above all other options were left default We did not use VLANs. We worked with our IT Admin to block out 20 sub IP addresses and found the networking information on each node in the HCI cluster, in WAC under the virtual switch tool. Alternatively you can work with your IT Admin to build your Engineering Plan. 


# 4. Creating AI Workload AKS Cluster
Now you have AKS and ARC installed in your management cluster. You need to create a AI Workload cluster and prime the nodes to leverage the AI Accelerator hardware. 
## Create AI Workload Cluster
Follow [instructions](https://learn.microsoft.com/en-us/azure/aks/hybrid/create-kubernetes-cluster) to create a cluster named: AI Workload
We stood up a 3 node AKS cluster.
>
> Basic
> Connection to Azure Arc:Enabled
>
> Azure subscription: <myAzureSub>
> 
> Resource group: edgeaiDemo2
>
> Kubernetes cluster name: ai1-workload-cluster
>
> Azure Kubernetes Service hybrid host: <AKSHCI cluster host name>
>
> Cluster admin group or user name: <domain>\<user>
>
> Kubernetes version: v1.24.6
>
> Load balancer node size: Standard_D4s_v3 (16 GB Memory, 4 CPU)
>	
> Load balancer node count: 1
>
> Control plane node size: Standard_A4_v2 (8 GB Memory, 4 CPU)
>
> Control plane node count: 1
>
> Node pools
> Node pools: 1
>
> Authentication: AD authentication Disabled
>
> Networking
>
> Network configuration: flannel
>
> Load balancer: Standard
> 
> Network policy: none
>
>
	
## Create a GPU Pool and attach GPUs to AI Workload Nodes
Once your AI Workload cluster is created, go to WAC Cluster Manager, and look at VM list. Take note of VM names for the AI Workload.

Follow [these steps](https://learn.microsoft.com/en-us/azure-stack/hci/manage/use-gpu-with-clustered-vm) to create a GPU Pool in WAC and assign the VMs from the AI Workload Cluster. 

## Preparing node for AI workload
Now that we have the GPUs assigned, we need to install Docker and the Nvidia plug-in. 

1.Go to Docker page and find your respective binary. For this example, we use x86_64 docker-20.10.9.tgz.
[Docker binaries](https://docs.docker.com/engine/install/binaries/#install-static-binaries)

2. Get the Workload AI node IP address and connect using your rsa. When using WAC, these will be placed in your Cluster storage under volumes then AksHCI. You can run this from your dev machine command prompt, but ensure you are in the same folder as the rsa file. For command below we copied out the rsa file to dev machine and renamed to _akshci_rsa.xml_. Learn more at [Connect with SSH to Linux or Windows worker nodes](https://learn.microsoft.com/en-us/azure/aks/hybrid/ssh-connection)
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
```bash
sudo vim /etc/containerd/config.toml
```

13. Paste into file
```yaml
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
	

# 5. Integrating with GitHub
1. Follow the [QuickStart](https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/conceptual-gitops-flux2) to configure your ARC enabled AKS cluster with GitHub using Flux.

Remember to have the Kubernetes default namespace identified in your deployment yaml.


# 6. Deploy AI Workload
# 7. Validate E2E Solution Working
### go to VCL and see inferencing results
rtsp://172.23.30.162:30007/ds-test 


# 8. Cleanup Resources



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
