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
* Check E2E Solution
* Cleanup Resources


# Prerequesits
For this E2E refrence solution you would need the following prerequisits:
* 2 - node cluster (add link?)
* Azure subscription
* Windows Admin Center

# Preparing AzSHCI - 2 node cluster
Follow the Microsoft Learn documentation to set up Windows Admin Center (WAC)
[Quickstart setup AzSHCI with WAC](https://learn.microsoft.com/en-us/azure-stack/hci/get-started)

Follow the Microsoft Learn documents to configure your two node cluster:
[Deploy a 2-node cluster on AzSHCI](https://learn.microsoft.com/en-us/azure-stack/hci/deploy/create-cluster?tabs=use-network-atc-to-deploy-and-manage-networking-recommended)

# Configuring ARC and AKS on AzSHCI
(add steps)

# Creating AI Workload AKS Cluster
Now that you have AKS and ARC installed in your management cluster. You need to create a AI Workload cluster and prime the nodes to leverage the AI Accelerator hardware. 
## Create AI Workload Cluster
## Create a GPU Pool and attach GPUs to AI Workload Nodes
## Preparing node for AI workload

Now that we have the GPUs assigned, we need to install Docker and the Nvidia plug-in. 
1.Go to Docker page and find your respective binary. For this example we use x86_64 docker-20.10.9.tgz.
[Docker binaries](https://docs.docker.com/engine/install/binaries/#install-static-binaries)

2. Get the Workload AI node IP address and connect using your rsa. When using WAC, these will be placed in your Cluster storage under volumes then AksHCI. You can run this from your dev machience command prompt, but ensure you are in the same folder as the rsa file. For command below we copied out the rsa file to dev machiene and renamed to _akshci_rsa.xml_. Learn more at [Connect with SSH to Linux or Windows worker nodes](https://learn.microsoft.com/en-us/azure/aks/hybrid/ssh-connection)
<blockquote> ssh -i akshci_rsa.xml clouduser@172.23.30.157 </blockquote>

3. Once on the Workload AI node, download the docker binary.
<blockquote> sudo curl https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz -o docker-20.10.9.tgz </blockquote>

4. Inflate docker binaries.
<blockquote> sudo tar xzvf docker-20.10.9.tgz </blockquote>

5. Remove any running files.
> sudo rm -rf '/usr/bin/containerd' 
> sudo rm -rf '/usr/bin/containerd-shim-runc-v2'
	
6. Copy the binaries to your clouduser location. 
(HTML <blockquote> sudo cp docker/* /usr/bin/ </blockquote>)

7. Run docker in background.
(HTML <blockquote> sudo dockerd &
	
8. Installing the Nvidia GPU plugin. Go to Nvidia page for full set of instructions. 
[GitHub - NVIDIA/k8s-device-plugin: NVIDIA device plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin#preparing-your-gpu-nodes)

9. Update docker as default runtime by createing daemon.json
(HTML <blockquote> sudo vim /etc/docker/daemon.json

10. Paste into newly created daemon.json file
(HTML <blockquote> {
(HTML <blockquote>     "default-runtime": "nvidia",
(HTML <blockquote>     "runtimes": {
(HTML <blockquote>         "nvidia": {
(HTML <blockquote>             "path": "/usr/bin/nvidia-container-runtime",
(HTML <blockquote>             "runtimeArgs": []
(HTML <blockquote>         }
(HTML <blockquote>     }
(HTML <blockquote> }

11. Ceck to ensure changes took.
(HTML <blockquote> sudo cat /etc/docker/daemon.json
	
12. Remove running files and restart docker
(HTML <blockquote> sudo rm /var/run/docker.pid
(HTML <blockquote> sudo rm -rf /var/lib/docker/volumes/*
(HTML <blockquote> sudo dockerd &


12. Configure containerd. Open the config.toml file and paste in modification from step 13.
(HTML <blockquote> sudo vim /etc/containerd/config.toml

13. Paste into file
(HTML <blockquote> version = 2
(HTML <blockquote> [plugins]
(HTML <blockquote>   [plugins."io.containerd.grpc.v1.cri"]
(HTML <blockquote>     [plugins."io.containerd.grpc.v1.cri".containerd]
(HTML <blockquote>       default_runtime_name = "nvidia"
(HTML <blockquote>
(HTML <blockquote>       [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
(HTML <blockquote>         [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
(HTML <blockquote>           privileged_without_host_devices = false
(HTML <blockquote>           runtime_engine = ""
(HTML <blockquote>           runtime_root = ""
(HTML <blockquote>           runtime_type = "io.containerd.runc.v2"
(HTML <blockquote>           [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
(HTML <blockquote>             BinaryName = "/usr/bin/nvidia-container-runtime"

14. Check to ensure changes took.
(HTML <blockquote> sudo cat /etc/containerd/config.toml

15. Restart containerd
(HTML <blockquote> sudo systemctl restart containerd

16. Optional troubleshooting:
(HTML <blockquote> sudo systemctl stop containerd
(HTML <blockquote> sudo systemctl start containerd
(HTML <blockquote> sudo containerd
	
17. From powershell in the kubectl command line. Enabeling GPU supporting in k8. 
(HTML <blockquote> Run deployment
(HTML <blockquote> kubectl apply -f edge-ai1.yaml
	
(HTML <blockquote> Run nvidia plugin
(HTML <blockquote> kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.yml
	
	

# Integrating with GitHub
# Deploy AI Workload
# Check E2E Solution
# Cleanup Resources

	
### go to VCL and see inferencing results
rtsp://172.23.30.162:30007/ds-test ![image](https://user-images.githubusercontent.com/47536604/193683136-ff9896fa-c0ab-4616-b691-26f0193d4028.png)


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
