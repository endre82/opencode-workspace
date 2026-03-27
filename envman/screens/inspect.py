"""Inspect environment screen"""

import asyncio
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Tree, Static
from textual.containers import Container
from textual.binding import Binding

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

        set_context(screen="InspectEnvironment", environment_name=self.environment.name)

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="inspect-container"):
            yield Static(f"Inspect: {self.environment.name}", id="title")
            yield Tree(f"Environment: {self.environment.name}", id="inspector-tree")
            yield Static("Loading...", id="status-bar")

        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._load_inspection_data(), exclusive=True)

    async def _load_inspection_data(self) -> None:
        """Load container inspection data asynchronously."""
        tree = self.query_one("#inspector-tree", Tree)
        tree.clear()
        tree.root.expand()

        try:
            self.inspection_data = await asyncio.to_thread(
                self.docker_service.inspect_container,
                self.environment.container_name,
            )

            if not self.inspection_data:
                tree.root.add_leaf("Container not found or not running")
                self.update_status("Container not found")
                return

            # Get stats (if running) — best-effort
            try:
                self.stats_data = await asyncio.to_thread(
                    self.docker_service.get_container_stats,
                    self.environment.container_name,
                )
            except Exception:
                self.stats_data = None

            self._build_tree()
            self.update_status("Inspection data loaded")

        except DockerError as e:
            tree.root.add_leaf(f"Error: {e}")
            self.update_status(f"Error: {e}")
            self.notify(f"Failed to inspect container: {e}", severity="error")
        except Exception as e:
            tree.root.add_leaf(f"Unexpected error: {e}")
            self.update_status(f"Error: {e}")

    def _build_tree(self) -> None:
        tree = self.query_one("#inspector-tree", Tree)

        if not self.inspection_data:
            return

        details_node = tree.root.add("📦 Container Details", expand=True)
        self._add_container_details(details_node)

        config_node = tree.root.add("⚙️  Configuration", expand=True)
        self._add_configuration(config_node)

        network_node = tree.root.add("🌐 Network", expand=True)
        self._add_network_settings(network_node)

        mounts_node = tree.root.add("💾 Mounts", expand=True)
        self._add_mounts(mounts_node)

        if self.stats_data:
            stats_node = tree.root.add("📊 Resource Usage", expand=True)
            self._add_resource_stats(stats_node)

        state_node = tree.root.add("🔄 State", expand=True)
        self._add_state_info(state_node)

    def _add_container_details(self, parent_node) -> None:
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
        config = self.inspection_data.get("Config", {})

        parent_node.add_leaf(f"Hostname: {config.get('Hostname', 'Unknown')}")
        parent_node.add_leaf(f"Working Dir: {config.get('WorkingDir', 'Unknown')}")
        parent_node.add_leaf(f"User: {config.get('User', 'root')}")

        env_vars = config.get("Env", [])
        if env_vars:
            env_node = parent_node.add(f"Environment Variables ({len(env_vars)})")
            for env_var in env_vars[:20]:
                env_node.add_leaf(env_var)
            if len(env_vars) > 20:
                env_node.add_leaf(f"... and {len(env_vars) - 20} more")

        exposed_ports = config.get("ExposedPorts", {})
        if exposed_ports:
            ports_node = parent_node.add(f"Exposed Ports ({len(exposed_ports)})")
            for port in exposed_ports.keys():
                ports_node.add_leaf(port)

        labels = config.get("Labels", {})
        if labels:
            labels_node = parent_node.add(f"Labels ({len(labels)})")
            for key, value in list(labels.items())[:10]:
                labels_node.add_leaf(f"{key}: {value}")
            if len(labels) > 10:
                labels_node.add_leaf(f"... and {len(labels) - 10} more")

    def _add_network_settings(self, parent_node) -> None:
        network_settings = self.inspection_data.get("NetworkSettings", {})

        parent_node.add_leaf(f"IP Address: {network_settings.get('IPAddress', 'N/A')}")
        parent_node.add_leaf(f"Gateway: {network_settings.get('Gateway', 'N/A')}")
        parent_node.add_leaf(f"MAC Address: {network_settings.get('MacAddress', 'N/A')}")

        networks = network_settings.get("Networks", {})
        if networks:
            networks_node = parent_node.add(f"Networks ({len(networks)})")
            for network_name, network_data in networks.items():
                net_node = networks_node.add(network_name)
                net_node.add_leaf(f"IP: {network_data.get('IPAddress', 'N/A')}")
                net_node.add_leaf(f"Gateway: {network_data.get('Gateway', 'N/A')}")
                net_node.add_leaf(f"Network ID: {network_data.get('NetworkID', 'N/A')[:12]}")

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
        if not self.stats_data:
            parent_node.add_leaf("Stats not available")
            return

        # Memory
        memory_stats = self.stats_data.get("memory_stats", {})
        usage = memory_stats.get("usage", 0)
        limit = memory_stats.get("limit", 0)
        memory_mb = usage / (1024 * 1024) if usage else 0
        limit_mb = limit / (1024 * 1024) if limit else 0
        memory_percent = (usage / limit * 100) if limit else 0
        parent_node.add_leaf(
            f"Memory: {memory_mb:.1f} MB / {limit_mb:.1f} MB ({memory_percent:.1f}%)"
        )

        # CPU — calculate % from pre/post cpu_stats if available
        cpu_stats = self.stats_data.get("cpu_stats", {})
        precpu_stats = self.stats_data.get("precpu_stats", {})

        cpu_delta = (
            cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
        )
        system_delta = (
            cpu_stats.get("system_cpu_usage", 0)
            - precpu_stats.get("system_cpu_usage", 0)
        )
        num_cpus = len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [])) or 1

        if system_delta > 0 and cpu_delta >= 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            parent_node.add_leaf(f"CPU: {cpu_percent:.2f}% (across {num_cpus} CPUs)")
        else:
            parent_node.add_leaf("CPU: insufficient data for percentage")

        # Block I/O
        blkio_stats = self.stats_data.get("blkio_stats", {})
        io_service_bytes = blkio_stats.get("io_service_bytes_recursive", [])
        if io_service_bytes:
            read_bytes = sum(
                item["value"] for item in io_service_bytes if item.get("op") == "read"
            )
            write_bytes = sum(
                item["value"] for item in io_service_bytes if item.get("op") == "write"
            )
            parent_node.add_leaf(f"Disk Read: {read_bytes / (1024 * 1024):.2f} MB")
            parent_node.add_leaf(f"Disk Write: {write_bytes / (1024 * 1024):.2f} MB")

    def _add_state_info(self, parent_node) -> None:
        state = self.inspection_data.get("State", {})

        parent_node.add_leaf(f"Status: {state.get('Status', 'unknown')}")
        parent_node.add_leaf(f"Running: {state.get('Running', False)}")
        parent_node.add_leaf(f"Paused: {state.get('Paused', False)}")
        parent_node.add_leaf(f"Restarting: {state.get('Restarting', False)}")
        parent_node.add_leaf(f"Started: {state.get('StartedAt', 'Unknown')}")

        finished_at = state.get("FinishedAt", "Unknown")
        if finished_at and finished_at != "0001-01-01T00:00:00Z":
            parent_node.add_leaf(f"Finished: {finished_at}")

        exit_code = state.get("ExitCode", 0)
        if exit_code != 0:
            parent_node.add_leaf(f"Exit Code: {exit_code}")

    def update_status(self, status: str) -> None:
        self.query_one("#status-bar", Static).update(status)

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.run_worker(self._load_inspection_data(), exclusive=True)
        self.notify("Refreshing...", severity="information", timeout=1)

    def action_expand_all(self) -> None:
        tree = self.query_one("#inspector-tree", Tree)
        for node in tree.root.children:
            node.expand_all()

    def action_collapse_all(self) -> None:
        tree = self.query_one("#inspector-tree", Tree)
        for node in tree.root.children:
            node.collapse_all()
