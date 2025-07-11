# SnapPulse 📊

**Self-hosted analytics for Snap Store packages**

SnapPulse addresses the transparency gap in the Snap Store by providing comprehensive analytics that developers and users have been requesting. Built with Canonical's cloud-native stack.

## 🚀 Quick Start Options

### Option 1: Local Development (Fastest)

```bash
# Navigate to the project directory
cd /workspaces/SnapPulse/snap-pulse

# 1. Start the API Service
cd services/api
python main.py &
# API will be available at http://localhost:8000

# 2. Open the Demo Dashboard
# Open services/dashboard/demo.html in your browser
# The dashboard will automatically connect to the API

# 3. Test the APIs
curl http://localhost:8000/health
curl http://localhost:8000/stats/firefox/stable
curl http://localhost:8000/trending

# 4. View API Documentation
# Open http://localhost:8000/docs in your browser for interactive API docs
```

**Demo Features:**
- ✨ Real-time analytics dashboard with interactive charts
- 📊 Snap download statistics and trends
- ⭐ Rating and version tracking
- 🔥 Top trending snaps with growth metrics
- 🔄 Auto-refreshing data every 5 seconds
- 🎛️ Channel and snap selection (Firefox, Discord, VS Code, Spotify)

### Option 2: Full Production Deployment

```bash
# Install prerequisites (Ubuntu 22.04+)
sudo snap install microk8s --classic --channel=1.32/stable
sudo snap install juju --classic --channel=3.6/stable
sudo snap alias microk8s.kubectl kubectl

# Enable required MicroK8s addons
microk8s enable dns storage

# Clone and deploy
git clone https://github.com/ANSHU-Ireland/SnapPulse.git
cd SnapPulse/snap-pulse
./scripts/deploy.sh

# Access services at the URLs shown
```

### Option 3: Individual Service Testing

```bash
# Test each service independently
cd SnapPulse/snap-pulse

# 1. API Service
cd services/api && python -m uvicorn main:app --port 8000 &

# 2. Dashboard (requires Node.js)
cd services/dashboard && npm install && npm run dev &

# 3. Collector (requires snapstore-client)
cd services/collector && python app.py &

# 4. Copilot (requires transformers)
cd services/copilot && python main.py &
```

## 🎯 What This Demonstrates

✅ **Community empathy** - Addressing real developer pain points  
✅ **Product thinking** - Metrics-first approach to ecosystem growth  
✅ **Technical depth** - Modern cloud-native architecture with Canonical tech  

## 🏗️ Architecture

- **Collector:** Python service pulling Snap Store data via snapstore-client
- **API:** FastAPI with OpenSearch backend, CORS-enabled for dashboard
- **Dashboard:** Next.js 15 with Tailwind, Chart.js, and SWR for real-time updates
- **Copilot:** AI service using Mistral-7B for snapcraft.yaml optimization

All deployed as **Charmed Operators** on **MicroK8s** via **Juju**.

## 📊 Features

- Real-time download tracking and trend visualization
- Multi-channel analytics (stable/candidate/beta/edge)
- AI-powered snapcraft.yaml optimization via GitHub PRs
- Self-hosted with complete data ownership
- RESTful API for programmatic access

## 📁 Project Structure

```
snap-pulse/
├── services/          # Source code (collector, api, dashboard, copilot)
├── charms/           # Charmed Operator definitions  
├── kubernetes/       # Juju bundle configuration
├── scripts/          # Deployment and demo utilities
├── snap/            # Snap package for one-click install
└── docs/            # Comprehensive documentation
```

## 🧪 Demo

```bash
# Generate realistic demo data
python3 scripts/seed_demo.py

# Test the API
curl http://<api-ip>:8000/stats/firefox/stable

# Try the copilot (comment "/snappulse fix" on GitHub)
```

**Full documentation:** [docs/README.md](docs/README.md)

---

*Proving you can hear community pain, stitch Canonical tech together, and think like a product owner* 🚀