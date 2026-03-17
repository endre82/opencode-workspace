"""Inspect environment screen"""

import asyncio
import json
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Tree, Static
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text

from envman.models.environment import Environment
from envman.services.docker import DockerService
from envman.utils.exceptions import DockerError
from envman.utils.exception_logger import set_context


class InspectScreen(Screen):
    """Environment inspection screen showing detailed container information"""
    
    CSS = """
    InspectScreen {
        layout: vertical;
    }
    
    #inspect-container {
        height: 100%;
        width: 100%;
    }
    
    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $panel;
        padding: 1;
    }
    
    #inspector-tree {
        height: 1fr;
        border: solid $primary;
        scrollbar-gutter: stable;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "expand_all", "Expand All"),
        Binding("c", "collapse_all", "Collapse All"),
    ]
    
    def __init__(
        self,
        environment: Environment,
        docker_service: DockerService,
    ):
        super().__init__()
        self.environment = environment
        self.docker_service = docker_service
        self.inspection_data: dict | None = None
        self.stats_data: dict | None = None
        
        # Set context early so it's available during compose()
        set_context(screen="InspectEnvironment", environment_name=self.environment.name)
    
    def compose(self) -> ComposeResult:
        """Compose the inspection UI"""
        yield Header()
        
        with Container(id="inspect-container"):
            yield Static(f"Inspect: {self.environment.name}", id="title")
            yield Tree(f"Environment: {self.environment.name}", id="inspector-tree")
            yield Static("Loading...", id="status-bar")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Setup the inspector when mounted"""
        self.load_inspection_data()
    
    def load_inspection_data(self) -> None:
        """Load container inspection data"""
        tree = self.query_one("#inspector-tree", Tree)
        tree.clear()
        tree.root.expand()
        
        try:
            # Get inspection data
            self.inspection_data = self.docker_service.inspect_container(self.environment.container_name)
            
            if not self.inspection_data:
                tree.root.add_leaf("Container not found or not running")
                self.update_status("Container not found")
                return
            
            # Get stats data (if running)
            try:
                self.stats_data = self.docker_service.get_container_stats(self.environment.container_name)
            except:
                self.stats_data = None
            
            # Build tree structure
            self._build_tree()
            self.update_status("Inspection data loaded")
        
        except DockerError as e:
            tree.root.add_leaf(f"Error: {e}")
            self.update_status(f"Error: {e}")
            self.notify(f"Failed to inspect container: {e}", severity="error")
    
    def _build_tree(self) -> None:
        """Build the inspection tree"""
        tree = self.query_one("#inspector-tree", Tree)
        
        if not self.inspection_data:
            return
        
        # Container Details
        details_node = tree.root.add("📦 Container Details", expand=True)
        self._add_container_details(details_node)
        
        # Configuration
        config_node = tree.root.add("⚙️  Configuration", expand=True)
        self._add_configuration(config_node)
        
        # Network Settings
        network_node = tree.root.add("🌐 Network", expand=True)
        self._add_network_settings(network_node)
        
        # Mounts / Volumes
        mounts_node = tree.root.add("💾 Mounts", expand=True)
        self._add_mounts(mounts_node)
        
        # Resource Usage (if available)
        if self.stats_data:
            stats_node = tree.root.add("📊 Resource Usage", expand=True)
            self._add_resource_stats(stats_node)
        
        # State Information
        state_node = tree.root.add("🔄 State", expand=True)
        self._add_state_info(state_node)
    
    def _add_container_details(self, parent_node) -> None:
        """Add container details to tree"""
        data = self.inspection_data
        
        container_id = data.get("Id", "Unknown")[:12]
        parent_node.add_leaf(f"ID: {container_id}")
        
        name = data.get("Name", "Unknown").lstrip("/")
        parent_node.add_leaf(f"Name: {name}")
        
        image = data.get("Config", {}).get("Image", "Unknown")
        parent_node.add_leaf(f"Image: {image}")
        
        created = data.get("Created", "Unknown")
        parent_node.add_leaf(f"Created: {created}")
        
        platform = data.get("Platform", "Unknown")
        parent_node.add_leaf(f"Platform: {platform}")
    
    def _add_configuration(self, parent_node) -> None:
        """Add configuration details to tree"""
        config = self.inspection_data.get("Config", {})
        
        # Hostname
        hostname = config.get("Hostname", "Unknown")
        parent_node.add_leaf(f"Hostname: {hostname}")
        
        # Working Directory
        workdir = config.get("WorkingDir", "Unknown")
        parent_node.add_leaf(f"Working Dir: {workdir}")
        
        # User
        user = config.get("User", "root")
        parent_node.add_leaf(f"User: {user}")
        
        # Environment Variables
        env_vars = config.get("Env", [])
        if env_vars:
            env_node = parent_node.add(f"Environment Variables ({len(env_vars)})")
            for env_var in env_vars[:20]:  # Limit to first 20
                env_node.add_leaf(env_var)
            if len(env_vars) > 20:
                env_node.add_leaf(f"... and {len(env_vars) - 20} more")
        
        # Exposed Ports
        exposed_ports = config.get("ExposedPorts", {})
        if exposed_ports:
            ports_node = parent_node.add(f"Exposed Ports ({len(exposed_ports)})")
            for port in exposed_ports.keys():
                ports_node.add_leaf(port)
        
        # Labels
        labels = config.get("Labels", {})
        if labels:
            labels_node = parent_node.add(f"Labels ({len(labels)})")
            for key, value in list(labels.items())[:10]:  # Limit to first 10
                labels_node.add_leaf(f"{key}: {value}")
            if len(labels) > 10:
                labels_node.add_leaf(f"... and {len(labels) - 10} more")
    
    def _add_network_settings(self, parent_node) -> None:
        """Add network settings to tree"""
        network_settings = self.inspection_data.get("NetworkSettings", {})
        
        # IP Address
        ip_address = network_settings.get("IPAddress", "N/A")
        parent_node.add_leaf(f"IP Address: {ip_address}")
        
        # Gateway
        gateway = network_settings.get("Gateway", "N/A")
        parent_node.add_leaf(f"Gateway: {gateway}")
        
        # MAC Address
        mac_address = network_settings.get("MacAddress", "N/A")
        parent_node.add_leaf(f"MAC Address: {mac_address}")
        
        # Networks
        networks = network_settings.get("Networks", {})
        if networks:
            networks_node = parent_node.add(f"Networks ({len(networks)})")
            for network_name, network_data in networks.items():
                net_node = networks_node.add(network_name)
                net_node.add_leaf(f"IP: {network_data.get('IPAddress', 'N/A')}")
                net_node.add_leaf(f"Gateway: {network_data.get('Gateway', 'N/A')}")
                net_node.add_leaf(f"Network ID: {network_data.get('NetworkID', 'N/A')[:12]}")
        
        # Port Bindings
        ports = network_settings.get("Ports", {})
        if ports:
            ports_node = parent_node.add(f"Port Bindings ({len(ports)})")
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_ip = binding.get("HostIp", "0.0.0.0")
                        host_port = binding.get("HostPort", "?")
                        ports_node.add_leaf(f"{container_port} → {host_ip}:{host_port}")
                else:
                    ports_node.add_leaf(f"{container_port} (not bound)")
    
    def _add_mounts(self, parent_node) -> None:
        """Add mount information to tree"""
        mounts = self.inspection_data.get("Mounts", [])
        
        if not mounts:
            parent_node.add_leaf("No mounts configured")
            return
        
        for mount in mounts:
            mount_type = mount.get("Type", "unknown")
            source = mount.get("Source", "?")
            destination = mount.get("Destination", "?")
            rw = "rw" if mount.get("RW", True) else "ro"
            
            mount_node = parent_node.add(f"{mount_type}: {destination}")
            mount_node.add_leaf(f"Source: {source}")
            mount_node.add_leaf(f"Mode: {rw}")
            
            if mount_type == "volume":
                volume_name = mount.get("Name", "unnamed")
                mount_node.add_leaf(f"Volume: {volume_name}")
    
    def _add_resource_stats(self, parent_node) -> None:
        """Add resource usage statistics to tree"""
        if not self.stats_data:
            parent_node.add_leaf("Stats not available")
            return
        
        # CPU Stats
        cpu_stats = self.stats_data.get("cpu_stats", {})
        cpu_usage = cpu_stats.get("cpu_usage", {})
        total_usage = cpu_usage.get("total_usage", 0)
        
        # Memory Stats
        memory_stats = self.stats_data.get("memory_stats", {})
        usage = memory_stats.get("usage", 0)
        limit = memory_stats.get("limit", 0)
        
        # Calculate percentages
        memory_mb = usage / (1024 * 1024) if usage else 0
        limit_mb = limit / (1024 * 1024) if limit else 0
        memory_percent = (usage / limit * 100) if limit else 0
        
        # Add to tree
        parent_node.add_leaf(f"Memory: {memory_mb:.1f} MB / {limit_mb:.1f} MB ({memory_percent:.1f}%)")
        parent_node.add_leaf(f"CPU Usage: {total_usage}")
        
        # Block I/O
        blkio_stats = self.stats_data.get("blkio_stats", {})
        io_service_bytes = blkio_stats.get("io_service_bytes_recursive", [])
        if io_service_bytes:
            read_bytes = sum(item["value"] for item in io_service_bytes if item.get("op") == "read")
            write_bytes = sum(item["value"] for item in io_service_bytes if item.get("op") == "write")
            
            read_mb = read_bytes / (1024 * 1024)
            write_mb = write_bytes / (1024 * 1024)
            
            parent_node.add_leaf(f"Disk Read: {read_mb:.2f} MB")
            parent_node.add_leaf(f"Disk Write: {write_mb:.2f} MB")
    
    def _add_state_info(self, parent_node) -> None:
        """Add state information to tree"""
        state = self.inspection_data.get("State", {})
        
        status = state.get("Status", "unknown")
        parent_node.add_leaf(f"Status: {status}")
        
        running = state.get("Running", False)
        parent_node.add_leaf(f"Running: {running}")
        
        paused = state.get("Paused", False)
        parent_node.add_leaf(f"Paused: {paused}")
        
        restarting = state.get("Restarting", False)
        parent_node.add_leaf(f"Restarting: {restarting}")
        
        started_at = state.get("StartedAt", "Unknown")
        parent_node.add_leaf(f"Started: {started_at}")
        
        finished_at = state.get("FinishedAt", "Unknown")
        if finished_at != "0001-01-01T00:00:00Z":
            parent_node.add_leaf(f"Finished: {finished_at}")
        
        exit_code = state.get("ExitCode", 0)
        if exit_code != 0:
            parent_node.add_leaf(f"Exit Code: {exit_code}")
    
    def update_status(self, status: str) -> None:
        """Update the status bar"""
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(status)
    
    def action_close(self) -> None:
        """Close the inspector"""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh inspection data"""
        self.load_inspection_data()
        self.notify("Inspection data refreshed", severity="information")
    
    def action_expand_all(self) -> None:
        """Expand all tree nodes"""
        tree = self.query_one("#inspector-tree", Tree)
        for node in tree.root.children:
            node.expand_all()
        self.notify("All nodes expanded", severity="information")
    
    def action_collapse_all(self) -> None:
        """Collapse all tree nodes"""
        tree = self.query_one("#inspector-tree", Tree)
        for node in tree.root.children:
            node.collapse_all()
        self.notify("All nodes collapsed", severity="information")
