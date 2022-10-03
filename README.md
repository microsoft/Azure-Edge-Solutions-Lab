## Reference Solution - EdgeAI running on AzS HCI using AKS and Arc

This refrence solution is inteneded to give customers and partners an example of how one can deploy and manage an Edge AI workload by leverageing certified AzS HCI hardware and using AKS and ARC.  

<img width="411" alt="image" src="https://user-images.githubusercontent.com/47536604/193682639-d53a6a1c-8953-4cce-8341-32e1f9ffc574.png">

## Prerequesets

## Preparing AzS HCI - 2 node cluster

## Configuring AKS on AzS HCI

# Initial AKS setup
# Preparing node for AI workload
Installing Docker on cluster
https://docs.docker.com/engine/install/binaries/#install-static-binaries

## find the VM you want docker installed on and SSH into it
	ssh -i akshci_rsa.xml clouduser@172.23.30.157 

# download docker binary
	sudo curl https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz -o docker-20.10.9.tgz

#inflate docker binaries
	sudo tar xzvf docker-20.10.9.tgz

# remove running files
	sudo rm -rf '/usr/bin/containerd'
	sudo rm -rf '/usr/bin/containerd-shim-runc-v2'
	
	
# copy the binaries 
	sudo cp docker/* /usr/bin/

# Run docker in background
	sudo dockerd &
	


Installing the Nvidia GPU plugin
GitHub - NVIDIA/k8s-device-plugin: NVIDIA device plugin for Kubernetes


## update docker as default runtime
## create daemon.json

	sudo vim /etc/docker/daemon.json

# paste into empty file

	{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}

## check to make sure changes took
	sudo cat /etc/docker/daemon.json
	

# remove running files and  restart docker

	sudo rm /var/run/docker.pid
	sudo rm -rf /var/lib/docker/volumes/*

	sudo dockerd &



#configure containerd 

#open config file

	sudo vim /etc/containerd/config.toml

# paste into file
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

## check to make sure changes took

	sudo cat /etc/containerd/config.toml


## restart containerd

	sudo systemctl restart containerd



	
	#optional troubleshooting ##
	sudo systemctl stop containerd
	sudo systemctl start containerd
	
	sudo containerd
	
	
	
	
	
#from powershell in the kubectl command line
#enabeling GPU supporting in k8

	
# run deployment

	kubectl apply -f edge-ai1.yaml
	
# run nvidia plugin
	kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.yml
	
	
	

	
# go to VCL and see inferencing results
rtsp://172.23.30.162:30007/ds-test ![image](https://user-images.githubusercontent.com/47536604/193683136-ff9896fa-c0ab-4616-b691-26f0193d4028.png)


## Configuring ARC and integration with GitHub


## Deploying Edge AI workload



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
