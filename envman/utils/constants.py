"""Constants and default values"""

# Base directory paths
ENVIRONMENTS_DIR = "environments"
SCRIPTS_DIR = "scripts"
SHARED_DIR = "shared"
BASE_DIR = "base"

# Docker configuration
DOCKER_COMPOSE_FILE = "docker-compose.yml"
ENV_FILE = ".env"
CONTAINER_NAME_PREFIX = "opencode-"
NETWORK_NAME = "opencode-network"

# Server configuration
DEFAULT_BASE_PORT = 4096
MAX_PORT = 4196
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_USERNAME = "opencode"

# Status indicators
STATUS_RUNNING = "running"
STATUS_STOPPED = "stopped"
STATUS_BUILDING = "building"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"

# Status icons
ICON_RUNNING = "🟢"
ICON_STOPPED = "🔴"
ICON_BUILDING = "🟡"
ICON_ERROR = "🔴"
ICON_UNKNOWN = "⚪"

STATUS_ICONS = {
    STATUS_RUNNING: ICON_RUNNING,
    STATUS_STOPPED: ICON_STOPPED,
    STATUS_BUILDING: ICON_BUILDING,
    STATUS_ERROR: ICON_ERROR,
    STATUS_UNKNOWN: ICON_UNKNOWN,
}

# Auto-refresh interval (seconds)
AUTO_REFRESH_INTERVAL = 3.0

# File patterns to skip during discovery
SKIP_DIRS = {"template", "shared", "worktree"}
