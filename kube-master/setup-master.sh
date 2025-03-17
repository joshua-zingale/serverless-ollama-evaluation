# Modifying from https://earthly.dev/blog/deploy-kubernetes-cri-o-container-runtime/

sudo apt update

# swapoff
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Network forwarding
sudo cat >>/etc/sysctl.d/kubernetes.conf<<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system

# CRI-O settings
sudo cat >>/etc/modules-load.d/crio.conf<<EOF
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# CRI-O listing
OS=xUbuntu_22.04
CRIO_VERSION=1.26
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /"|sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS/ /"|sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$CRIO_VERSION.list

curl -L https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable:cri-o:$CRI_VERSION/$OS/Release.key | sudo apt-key --keyring /etc/apt/trusted.gpg.d/libcontainers.gpg add -
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | sudo apt-key --keyring /etc/apt/trusted.gpg.d/libcontainers.gpg add -

# Download and run crio
sudo apt-get update 
sudo apt-get install -qq -y cri-o cri-o-runc cri-tools

sudo systemctl daemon-reload
sudo systemctl enable --now crio

# Kubernetes listings
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Download and Install kubernetes
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Initialize master node
sudo kubeadm init #--control-plane-endpoint=$(host node0 | awk '{print $4}') --apiserver-advertise-address $(curl -s ifconfig.me)
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml

# kn
[ $(uname -m) = x86_64 ] && curl -L https://github.com/knative/client/releases/download/knative-v1.17.0/kn-linux-amd64 --output kn
[ $(uname -m) = aarch64 ] && curl -L https://github.com/knative/client/releases/download/knative-v1.17.0/kn-linux-arm64 --output kn
chmod +x kn
sudo mv kn /usr/local/bin

# Install the Knative Serving component
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-core.yaml

# Install a networking layer
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.17.0/kourier.yaml
kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

# Change to Nodeport
kubectl patch service kourier \
  -n kourier-system \
  -p '{"spec":{"type":"NodePort"}}'

kubectl --namespace kourier-system get service kourier


# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Prometheus
sudo echo "kube-state-metrics:
  metricLabelsAllowlist:
    - pods=[*]
    - deployments=[app.kubernetes.io/name,app.kubernetes.io/component,app.kubernetes.io/instance]
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false" > values.yaml

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n default -f values.yaml

# Install KNative Eventing
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.17.3/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.17.3/eventing-core.yaml

# Install KNative Metrics
kubectl apply -f https://raw.githubusercontent.com/knative-extensions/monitoring/main/servicemonitor.yaml


# Printout information
printf "\nThe ingress is accessible on the internet at %s:%s\n" $(curl -s ifconfig.me) $(kubectl get svc kourier -n kourier-system -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
echo $(kubeadm token create --print-join-command)
echo "If something does not work, try running all the commands as the super user, which can be done by executing 'sudo su' before running all the commands"


# Make Prometheus accessible outside cluster
kubectl port-forward -n default svc/prometheus-kube-prometheus-prometheus 9090:9090

# kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-default-domain.yaml
# kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-hpa.yaml