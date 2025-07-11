#!/bin/bash
set -e

echo "🏗️  Building all SnapPulse charms..."
echo "=================================="

cd "$(dirname "$0")/.."

for charm in collector api dashboard copilot; do
    echo "📦 Building $charm charm..."
    cd "charms/$charm"
    
    if ! charmcraft pack --force; then
        echo "❌ Failed to build $charm charm"
        exit 1
    fi
    
    echo "✅ $charm charm built successfully"
    cd ../..
done

echo ""
echo "🎉 All charms built successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Deploy with: ./scripts/deploy.sh"
echo "   2. Or test locally by running services individually"
echo "   3. Build snap package: cd snap && snapcraft pack"
