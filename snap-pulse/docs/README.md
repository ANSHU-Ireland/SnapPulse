# SnapPulse 📊

> **Self-hosted analytics for Snap Store packages**

SnapPulse addresses the transparency gap in the Snap Store ecosystem by providing comprehensive analytics that developers and users have been requesting. It demonstrates modern cloud-native architecture using Canonical's technology stack.

## 🎯 What SnapPulse Solves

The Snap Store is often called a "black box" because it doesn't surface:
- Download counts and trends
- Crash rates and stability metrics  
- Upgrade patterns and user retention
- Performance benchmarks

**SnapPulse changes that** by providing a self-hosted analytics platform that:

✅ **Pulls public store data** + opt-in client telemetry  
✅ **Stores it** in a small analytics lake (Feast)  
✅ **Exposes** a REST API and slick dashboard  
✅ **Ships an LLM copilot** that suggests optimizations via GitHub PRs  

## 🏗️ Architecture

SnapPulse is built as four microservices, each deployed as a **Charmed Operator**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Collector  │    │     API     │    │  Dashboard  │    │   Copilot   │
│   Service   │───▶│   Service   │───▶│   Service   │    │   Service   │
│             │    │             │    │             │    │             │
│ • snapstore │    │ • FastAPI   │    │ • Next.js   │    │ • Mistral   │
│ • feast     │    │ • OpenSearch│    │ • Charts.js │    │ • GitHub    │
│ • asyncio   │    │ • CORS      │    │ • SWR       │    │ • Webhooks  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**Tech Stack:**
- **Orchestration:** Juju + MicroK8s
- **Data:** Feast (feature store) + SQLite/OpenSearch
- **API:** FastAPI with automatic OpenAPI docs
- **Frontend:** Next.js 15 + Tailwind CSS + Chart.js
- **AI:** Transformers + BitsAndBytes (4-bit quantization)
- **Packaging:** Charmed Operators + Snap

## 🚀 Quick Start

### Prerequisites (One-time setup)

```bash
# Install MicroK8s and Juju
sudo snap install microk8s --classic --channel=1.32/stable
sudo snap install juju --classic --channel=3.6/stable
sudo snap alias microk8s.kubectl kubectl

# Enable required addons
microk8s enable dns storage
```

### Option 1: Install as a Snap (Recommended)

```bash
# Build the snap
cd snap-pulse/snap
snapcraft pack --destructive-mode

# Install it
sudo snap install snap-pulse_*.snap --dangerous

# SnapPulse will auto-deploy and show you the dashboard URL
```

### Option 2: Manual Deployment

```bash
# Clone and deploy
git clone <repository>
cd snap-pulse
./scripts/deploy.sh

# Check status
juju status

# Access services
curl http://<api-ip>:8000/health
open http://<dashboard-ip>:3000
```

## 📊 Using SnapPulse

### Dashboard Features

- **📈 Download Trends:** Real-time charts showing package adoption
- **⭐ Ratings & Reviews:** Community feedback aggregation  
- **🏆 Trending Packages:** Most popular and fastest-growing snaps
- **🔄 Channel Comparison:** Stable vs Edge download patterns
- **📋 Publisher Insights:** Package portfolio performance

### API Endpoints

```bash
# Get stats for a specific snap/channel
GET /stats/{snap_name}/{channel}

# Get all channels for a snap
GET /stats/{snap_name}

# Get trending snaps
GET /trending?limit=10

# Health check
GET /health
```

### Copilot Features

The AI copilot analyzes `snapcraft.yaml` files and suggests optimizations:

1. **Comment `/snappulse fix`** on any GitHub issue
2. **Copilot analyzes** your snapcraft.yaml
3. **Opens a PR** with 3 specific improvements:
   - Package size reduction
   - Tighter confinement
   - Security/performance enhancements

## 🧪 Demo Data

Generate realistic demo data for presentations:

```bash
python3 scripts/seed_demo.py
```

This creates 6 months of synthetic download data for popular snaps.

## 🔧 Development

### Project Structure

```
snap-pulse/
├── services/           # Source code for each microservice
│   ├── collector/      # Data collection from Snap Store
│   ├── api/           # REST API endpoints
│   ├── dashboard/     # Next.js web interface
│   └── copilot/       # AI optimization suggestions
├── charms/            # Charmed Operator definitions
├── kubernetes/        # Juju bundle configuration
├── scripts/           # Deployment and utility scripts
└── snap/             # Snap package definition
```

### Running Services Locally

```bash
# Start collector
cd services/collector
python3 app.py

# Start API  
cd services/api
uvicorn main:app --reload

# Start dashboard
cd services/dashboard
npm run dev

# Start copilot
cd services/copilot
python3 main.py
```

### Building Charms

```bash
# Build individual charms
cd charms/collector
charmcraft pack

# Or build all at once
./scripts/build-charms.sh
```

## 🎤 Interview Talking Points

### Community Empathy
*"I saw repeated Reddit complaints that the Snap Store hides adoption numbers, so I built portable analytics that developers can self-host and customize."*

### Business Impact  
*"When developers can see that `snap install` actually moves the needle, they'll publish faster, which lifts Ubuntu desktop retention and ecosystem growth."*

### Technical Credibility
*"This demonstrates fluency with Canonical's entire stack: **charmed operators**, **Juju models**, **MicroK8s add-ons**, **Feast online store**, and modern cloud-native patterns."*

## 🧪 Smoke Test Checklist

Before presenting, verify:

- [ ] `curl http://<api-ip>:8000/stats/firefox/stable` returns JSON
- [ ] Dashboard loads in fresh incognito window  
- [ ] `juju remove-application copilot` doesn't break other services
- [ ] Demo data script generates realistic download spikes
- [ ] `/snappulse fix` comment creates GitHub PR

## 🤝 Contributing

SnapPulse is designed to showcase integration skills with Canonical technologies. Key areas for extension:

- **Data Sources:** Add crash reporting, user surveys, A/B testing
- **Analytics:** Implement cohort analysis, retention funnels  
- **AI Features:** Expand copilot to suggest marketing strategies
- **Integrations:** Connect with Launchpad, GitHub Actions, snap metrics

## 📜 License

MIT License - Feel free to use this in your own projects and interviews!

---

**Built with ❤️ to bridge the gap between developers and Snap Store users**
