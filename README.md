# codebeep

> Your AI coding agent, accessible from anywhere via Beeper/Matrix.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**codebeep** is a self-hosted AI coding agent that lets you assign coding tasks from your phone via [Beeper](https://beeper.com) (Matrix protocol). It integrates with [OpenCode](https://opencode.ai) to provide the same powerful coding capabilities you have on desktop, but accessible from anywhere.

## Why codebeep?

| Feature | Cursor Slack | Copilot Slack | codebeep |
|---------|--------------|---------------|----------|
| Self-hosted | No | No | **Yes** |
| Open Source | No | No | **Yes** |
| Privacy | Cloud | Cloud | **Local** |
| Platform | Slack only | Slack only | **Matrix/Beeper** |
| AI Provider | Cursor models | GitHub models | **Any (Antigravity, Copilot, etc.)** |
| Cost | Paid | Paid | **Free*** |

*Free when using Antigravity Manager with Google AI Studio quotas

## Features

- **Mobile-first**: Assign coding tasks from your phone via Beeper
- **OpenCode Integration**: Full access to OpenCode's build and plan agents
- **GitHub Integration**: Assign yourself to issues, create PRs, review code
- **MCP Tools**: Access all your MCP tools from mobile
- **Self-hosted**: Your code, your data, your control

## Quick Start

### Prerequisites

- Python 3.11+
- [Beeper](https://beeper.com) account
- [OpenCode](https://opencode.ai) installed and configured

### Installation

#### Method 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/Mihai-Codes/codebeep.git
cd codebeep

# Build and run with Docker (solves python-olm compilation issues)
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Method 2: Native Python
```bash
# Clone the repository
git clone https://github.com/Mihai-Codes/codebeep.git
cd codebeep

# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Configuration
cp config.example.yaml config.yaml
# Edit config.yaml with your Beeper credentials
```

### Auto-Start Options

#### Option 1: Docker (Recommended - Solves python-olm issues)
```bash
# Build and run with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Option 2: macOS LaunchAgent
This project includes a LaunchAgent to keep the bot running in the background.

1. **Install the Service:**
   ```bash
   cp com.mihai.codebeep.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.mihai.codebeep.plist
   ```

2. **Check Logs:**
   ```bash
   tail -f /tmp/codebeep.log
   tail -f /tmp/codebeep.error.log
   ```

## Configuration

Edit `config.yaml`:

```yaml
matrix:
  homeserver: "https://matrix.beeper.com"
  username: "@your-bot:beeper.local"
  password: "your-password"  # or use access_token

opencode:
  server_url: "http://127.0.0.1:4096"
  default_agent: "build"
```

## Architecture

```
Phone (Beeper App)
       │
       │ Matrix Protocol (E2EE)
       ▼
Your Mac (codebeep bot)
       │
       ├──► OpenCode Server (:4096)
       │         │
       │         └──► MCP Tools, Agents
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Note**: This project is not built by the OpenCode team and is not affiliated with them in any way.
