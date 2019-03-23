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

## 如何部署
### 建立Kubernetes的環境
* GCE K8s
* 實驗環境，建議使用[minikube](https://github.com/kubernetes/minikube)減少複雜度
#### macOS的minikube與kubectl 下載與安裝

1. 安裝 [VirtualBox](https://www.virtualbox.org/)

2. 安裝 Mac 套件管理工具 [Homebrew](https://brew.sh/index_zh-tw)

3. 使用 Homebrew 下載 minikube
    ```shell
    brew cask install minikube
    ```
4. 建置 minikube
    ``` shell
    minikube start
    ```
## 開始使用
### 建置 Pods 和 Services
##### 因為程式相依的關係，所以必須要分配磁碟空間、建立資料庫後再建立其他程式
1. 建立volume
   ```shell
   kubectl apply -f k8s/volume/,
   ```
2. 建立資料庫
   ```shell
   kubectl apply -f k8s/database/,
   ```
3. 啟動 Message Broker
   ```shell
   kubectl apply -f k8s/message/.
4. 建立其他程式
    ```shell
    kubectl apply -f k8s/.
    ```
* item 與 profile 這兩個service因為尚未配置過資料庫(scheme) ，所以會無法成功運行。
### 其他指令
* 查看minikube 儀表板
    ```shell
    minikube dashboard
    ```
* 使用minikube 將服務對外開放
    ```shell
    minikube service [service name]
    ```

## 範例架構
![Demonstration Architecture](https://github.com/yenchenLiu/RentalManagementMicroservice/blob/master/demo/Microservice.png)

