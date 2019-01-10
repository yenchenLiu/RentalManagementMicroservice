# RentalManagementMicroservice
微服務系統範例 by python

## 部屬環境
* [Kubernetes](https://kubernetes.io/) (K8s)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## 開發環境
* Python 3
* Docker
* [Kubernetes](https://kubernetes.io/) (K8s)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## 資料夾说明

* gateway       API的進入程式
* k8s           所有Kubernets的yaml檔案
* microservice  每個資料夾都是一個完整的服務

## 如何部屬
### 建立Kubernetes的環境
* GCE K8s
* 實驗環境，建議使用[minikube](https://github.com/kubernetes/minikube)減少複雜度
#### macOS的minikube與kubectl 下載與安裝
```shell
brew cask install minikube
brew install kubernetes-cli
```

### 建置 Pods 和 Services
```shell
kubectl create -f k8s/file.yaml
```

## 範例架構
![Demonstration Architecture](https://github.com/yenchenLiu/RentalManagementMicroservice/blob/master/demo/Microservice.png)
