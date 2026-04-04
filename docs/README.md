# Documentation Index

Welcome to the OpenCode Workspace documentation. This guide will help you find the information you need.

## 📖 Quick Navigation

### 🚀 Getting Started
Start here if you're new to the project:
- [Quick Start Guide](guides/quickstart.md) - Quick setup guide
- [Wizard User Guide](guides/wizard-guide.md) - Environment creation wizard
- [Remote Development Guide](guides/remote-dev-guide.md) - Remote development with code-server
- [Web UI Guide](user-guides/WEBUI_GUIDE.md) - Web Management UI documentation

### 🏗️ Feature Documentation
Implementation docs for each major feature:
- [Phase 1: Base System](features/phase1-base-system.md) - Dashboard and core architecture
- [Phase 3: Container Operations](features/phase3-container-ops.md) - Start/stop/restart functionality
- [Phase 4: Creation Wizard](features/phase4-creation-wizard.md) - Environment creation flow
- [ngrok Tunnel Management](features/ngrok-tunneling.md) - Internet access via ngrok tunneling
- [Feature Index →](features/README.md) - Complete feature list with status

### 🐛 Bug Fixes
Technical documentation of bug fixes:
- [Bug Timeline →](bugfixes/README.md) - Chronological bug fix history
- [Bug #001: AsyncIO](bugfixes/bug-001-asyncio-to-thread.md) - Fixed asyncio.to_thread issue
- [Bug #002: Wizard Compose](bugfixes/bug-002-wizard-compose.md) - Fixed compose query issue
- [Bug #003: Widget Mount](bugfixes/bug-003-widget-mount.md) - Fixed mount lifecycle error
- [Complete Summary](summaries/complete-bugfix-summary.md) - All bugs overview

### 📋 Summaries
Quick reference summaries:
- [Complete Bugfix Summary](summaries/complete-bugfix-summary.md) - All bug fixes overview
- [AsyncIO Bugfix Summary](summaries/bugfix-asyncio-summary.md) - Bug #001 summary
- [Wizard Bugfix Summary](summaries/bugfix-wizard-summary.md) - Bug #002 summary

### 🧪 Testing
Test scripts are located in `/tests/` at the project root:
- `test_wizard.py` - Comprehensive wizard testing
- `test_wizard_simple.py` - Simple wizard smoke test

## 📂 Directory Structure

```
docs/
├── README.md                 # This file
├── features/                 # Feature implementation docs
│   ├── README.md            # Feature index with status
│   ├── phase1-base-system.md
│   ├── phase3-container-ops.md
│   └── phase4-creation-wizard.md
├── bugfixes/                # Bug fix technical docs
│   ├── README.md           # Bug timeline
│   ├── bug-001-asyncio-to-thread.md
│   ├── bug-002-wizard-compose.md
│   └── bug-003-widget-mount.md
├── summaries/               # Quick reference summaries
│   ├── complete-bugfix-summary.md
│   ├── bugfix-asyncio-summary.md
│   └── bugfix-wizard-summary.md
└── guides/                  # User-facing guides
    ├── quickstart.md
    ├── wizard-guide.md
    └── remote-dev-guide.md

tests/                       # Test scripts (project root)
├── test_wizard.py
└── test_wizard_simple.py
```

## 🎯 Common Tasks

### I want to...
- **Create a new environment** → [Quick Start Guide](guides/quickstart.md)
- **Use the creation wizard** → [Wizard Guide](guides/wizard-guide.md)
- **Set up remote development** → [Remote Dev Guide](guides/remote-dev-guide.md)
- **Access from the internet** → [ngrok Tunnel Guide](features/ngrok-tunneling.md)
- **Understand container operations** → [Phase 3 Docs](features/phase3-container-ops.md)
- **See bug fix history** → [Bug Timeline](bugfixes/README.md)
- **Review all features** → [Feature Index](features/README.md)

## 📝 Documentation Standards

When adding new documentation:
1. Choose the appropriate directory based on content type:
   - `/features/` - Feature implementation and technical details
   - `/bugfixes/` - Bug fix documentation with root cause analysis
   - `/summaries/` - Quick reference and overview docs
   - `/guides/` - User-facing guides and tutorials
2. Use clear, descriptive filenames (e.g., `bug-001-description.md`)
3. Include a summary at the top of each document
4. Cross-reference related documents where relevant
5. Update the relevant README.md index when adding new docs

## 🔗 External Resources

- Main project: [../README.md](../README.md)
- Namespace documentation: [../shared/namespaces/README.md](../shared/namespaces/README.md)

---

**Need help?** Start with the [Quick Start Guide](guides/quickstart.md) or check the main [README.md](../README.md).
