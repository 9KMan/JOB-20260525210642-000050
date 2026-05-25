# Azure Infrastructure Setup Script
#!/bin/bash
set -e

# Variables
RESOURCE_GROUP="integration-platform-rg"
LOCATION="germanywestcentral"
AKS_NAME="integration-aks"
ACR_NAME="integrationacr"

echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "Creating ACR..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Standard --location $LOCATION

echo "Creating AKS cluster..."
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --location $LOCATION \
  --enable-managed-identity

echo "Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME --overwrite-existing

echo "Installing Argo Workflows..."
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argo-workflows argo/argo-workflows -n argo --create-namespace

echo "Installing Temporal..."
helm repo add temporal https://helm.io/temporal
helm repo update
helm install temporal temporal/temporal -n temporal --create-namespace

echo "Installing Redis..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis -n redis --create-namespace

echo "Installing PostgreSQL..."
helm install postgresql bitnami/postgresql -n postgresql --create-namespace

echo "Setup complete!"