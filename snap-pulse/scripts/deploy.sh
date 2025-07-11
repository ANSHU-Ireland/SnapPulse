#!/bin/bash
set -e

echo "🚀 SnapPulse Deployment Script"
echo "==============================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v microk8s &> /dev/null; then
    echo "❌ microk8s not found. Please install it first:"
    echo "   sudo snap install microk8s --classic --channel=1.32/stable"
    exit 1
fi

if ! command -v juju &> /dev/null; then
    echo "❌ juju not found. Please install it first:"
    echo "   sudo snap install juju --classic --channel=3.6/stable"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl not found. Setting up alias..."
    sudo snap alias microk8s.kubectl kubectl
fi

echo "✅ Prerequisites check passed"

# Enable required microk8s addons
echo "🔧 Enabling microk8s addons..."
microk8s enable dns storage

# Wait for microk8s to be ready
echo "⏳ Waiting for microk8s to be ready..."
microk8s status --wait-ready

# Bootstrap Juju if not already done
echo "🎯 Setting up Juju..."
if ! juju show-controller microk8s &> /dev/null; then
    echo "   Bootstrapping Juju controller..."
    juju bootstrap microk8s
else
    echo "   Juju controller already exists"
fi

# Add model if it doesn't exist
if ! juju show-model snap-pulse &> /dev/null; then
    echo "   Creating snap-pulse model..."
    juju add-model snap-pulse
else
    echo "   Using existing snap-pulse model"
    juju switch snap-pulse
fi

# Build charms
echo "🏗️  Building charms..."
cd "$(dirname "$0")/.."

for charm in collector api dashboard copilot; do
    echo "   Building $charm charm..."
    cd "charms/$charm"
    charmcraft pack --force
    cd ../..
done

# Deploy the bundle
echo "🚢 Deploying SnapPulse bundle..."
juju deploy ./kubernetes/bundle.yaml

echo "⏳ Waiting for deployment to complete..."
echo "   This may take several minutes as containers are pulled and started..."

echo "⏳ Waiting for deployment to complete..."
echo "   This may take several minutes as containers are pulled and started..."

# Use juju wait for better status checking
echo "   Using juju wait to monitor deployment..."
if juju wait --timeout 5m -m snap-pulse; then
    echo "✅ All applications are ready!"
else
    echo "⚠️  Deployment taking longer than expected or failed. Current status:"
    juju status
    echo "   You can continue monitoring with: juju status"
    exit 1
fi
echo "🎉 SnapPulse deployed successfully!"
echo ""
echo "📊 Service URLs:"
api_ip=$(juju status snap-pulse-api --format=yaml | grep public-address | awk '{print $2}' | head -1)
dashboard_ip=$(juju status snap-pulse-dashboard --format=yaml | grep public-address | awk '{print $2}' | head -1)

if [ -n "$api_ip" ]; then
    echo "   API: http://$api_ip:8000"
    echo "   Dashboard: http://$dashboard_ip:3000"
else
    echo "   Use 'juju status' to get service IPs"
fi

echo ""
echo "🧪 Quick test:"
echo "   curl http://$api_ip:8000/health"
echo ""
echo "📝 To monitor the deployment:"
echo "   juju status"
echo "   juju debug-log"
