# Deployment Script
#!/bin/bash
set -e

NAMESPACE="integration-platform"
RELEASE_NAME="integration-platform"
VALUES_FILE="helm/argo-workflows/values.yaml"

echo "Deploying to Kubernetes..."

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy API
kubectl apply -f k8s/deployment.yaml -n $NAMESPACE

# Verify deployment
kubectl rollout status deployment/integration-api -n $NAMESPACE

echo "Deployment successful!"