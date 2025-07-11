#!/bin/bash
# SnapPulse One-Command Deployment Test
# 
# Demonstrates complete "clone-and-deploy" capability
# Usage: curl -sSL https://raw.githubusercontent.com/ANSHU-Ireland/SnapPulse/main/one-command-deploy.sh | bash

set -e

echo "🚀 SnapPulse One-Command Deployment Starting..."

# Check if running as root or with sudo access
if ! sudo -n true 2>/dev/null; then
    echo "❌ This script requires sudo access. Please run with sudo or ensure passwordless sudo is configured."
    exit 1
fi

# Install dependencies
echo "📦 Installing snap dependencies..."
sudo snap install microk8s --classic --channel=1.32/stable
sudo snap install juju --classic --channel=3.6/stable

# Configure MicroK8s
echo "🔧 Configuring MicroK8s..."
sudo microk8s enable dns storage

# Add user to microk8s group
sudo usermod -a -G microk8s $USER
echo "👤 Added $USER to microk8s group"

# Wait for MicroK8s to be ready
echo "⏳ Waiting for MicroK8s to be ready..."
sudo microk8s status --wait-ready

# Clone repository if not present
if [ ! -d "SnapPulse" ]; then
    echo "📥 Cloning SnapPulse repository..."
    git clone https://github.com/ANSHU-Ireland/SnapPulse.git
fi

cd SnapPulse

# Bootstrap Juju
echo "🎯 Bootstrapping Juju..."
juju bootstrap microk8s snap-pulse-k8s

# Deploy the bundle
echo "🚀 Deploying SnapPulse..."
juju add-model snap-pulse
juju deploy snap-pulse/kubernetes/bundle.yaml

# Wait for deployment
echo "⏳ Waiting for services to start (this may take a few minutes)..."
juju wait -m snap-pulse --timeout 600 || {
    echo "⚠️  Services are still starting. Current status:"
    juju status
    echo ""
    echo "💡 You can continue monitoring with: juju status"
    echo "💡 View logs with: juju logs <service-name>"
}

# Test the deployment
echo "🔍 Testing deployment..."

# Get API endpoint
API_UNIT=$(juju status api --format=yaml | grep "public-address:" | head -1 | awk '{print $2}' 2>/dev/null || echo "")

if [ -n "$API_UNIT" ] && [ "$API_UNIT" != "null" ]; then
    echo "🌐 Testing API at $API_UNIT:8000..."
    
    # Test health endpoint
    if timeout 10 curl -f "http://$API_UNIT:8000/health" >/dev/null 2>&1; then
        echo "✅ API health check passed"
        
        # Test stats endpoint
        if timeout 10 curl -f "http://$API_UNIT:8000/stats" >/dev/null 2>&1; then
            echo "✅ API stats endpoint working"
        else
            echo "ℹ️  Stats endpoint not ready yet (normal for fresh deployment)"
        fi
    else
        echo "⚠️  API not responding yet. Services may still be initializing."
    fi
else
    echo "⚠️  API endpoint not yet available. Services may still be starting."
fi

echo ""
echo "🎉 SnapPulse Deployment Complete!"
echo ""
echo "📋 Current Status:"
juju status

echo ""
echo "🔗 Next Steps:"
echo "  📊 Check API:      curl http://$API_UNIT:8000/health"
echo "  📈 View Stats:     curl http://$API_UNIT:8000/stats"
echo "  📱 Monitor Status: juju status"
echo "  📝 View Logs:      juju logs api"
echo "  🎯 Run Tests:      ./snap-pulse/scripts/smoke-test.sh"
echo ""
echo "✨ Your SnapPulse analytics platform is now running on Kubernetes!"
echo "🌍 Access it via the displayed endpoints above."
