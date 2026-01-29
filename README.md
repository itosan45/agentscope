# AgentScope 🔭

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Deploy on Render](https://img.shields.io/badge/Render-Deploy%20Live-brightgreen)](https://render.com)

**AgentScope** is an open-source observability and tracing platform designed specifically for AI Agents and LLM-powered applications. Gain full visibility into your agent's thought process, costs, and performance in minutes.

[**Live Demo (Landing Page)**](https://agentscope-landing-v3.onrender.com) | [**Dashboard**](https://agentscope-dashboard-v3.onrender.com)

---

## ✨ Features

- 🔍 **Seamless Tracing**: Auto-instrumentation for OpenAI, LangChain, and more.
- 📊 **Visual Dashboard**: Real-time timeline view of agent chains and decision trees.
- ⚡ **Performance Metrics**: Track latency, token usage, costs, and error rates.
- 🔔 **Smart Alerts**: Get instant notifications via Slack/Webhook when anomalies occur.
- 🚀 **Cloud-Native**: Ready to deploy on Render or Docker with a single click.

## 🚀 Quick Start (SDK)

### 1. Install the SDK

```bash
pip install agentscope-sdk
```

### 2. Initialize & Trace

Add just a few lines to your existing AI application:

```python
from agentscope import trace, init

# Initialize with your local or cloud endpoint
init(api_key="your-api-key", endpoint="https://agentscope-backend-v3.onrender.com/api/v1")

@trace
def my_ai_agent(prompt):
    # Your LLM logic here (OpenAI, Anthropic, etc.)
    return "Agent response..."
```

## 🏗️ Architecture

AgentScope consists of three main components:

- **`sdk/`**: Lightweight Python library for data collection.
- **`backend/`**: High-performance FastAPI server and data processing.
- **`frontend/`**: Modern React dashboard for real-time visualization.

## 🚢 Deployment

### Using Render

This repository includes a `render.yaml` for instant deployment.
Simply connect your GitHub repo to Render and click "Create Resources".

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/agentscope.git

# Start the dashboard
cd agentscope/frontend && npm install && npm run dev
```

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---
Built with ❤️ for the AI community. Give it a ⭐ if you find it useful!
