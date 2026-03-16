"""Docker service for container operations and queries"""

import subprocess
from typing import Optional, List, Dict, Any
import docker
from docker.errors import DockerException, NotFound, APIError

from envman.utils.exceptions import DockerError
from envman.utils.constants import STATUS_RUNNING, STATUS_STOPPED, STATUS_UNKNOWN


class DockerService:
    """Service for Docker operations"""
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except DockerException as e:
            raise DockerError(f"Failed to connect to Docker: {e}")
    
    def get_container_status(self, container_name: str) -> str:
        """Get status of a container by name"""
        try:
            container = self.client.containers.get(container_name)
            status = container.status.lower()
            
            if status == "running":
                return STATUS_RUNNING
            elif status in ("exited", "stopped", "created"):
                return STATUS_STOPPED
            else:
                return status
        
        except NotFound:
            return STATUS_STOPPED
        except (DockerException, APIError) as e:
            print(f"Error getting container status: {e}")
            return STATUS_UNKNOWN
    
    def is_container_running(self, container_name: str) -> bool:
        """Check if container is running"""
        return self.get_container_status(container_name) == STATUS_RUNNING
    
    def get_container_info(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed container information"""
        try:
            container = self.client.containers.get(container_name)
            image_info = "unknown"
            if hasattr(container, 'image') and container.image:
                if hasattr(container.image, 'tags') and container.image.tags:
                    image_info = container.image.tags[0]
                elif hasattr(container.image, 'id'):
                    image_info = str(container.image.id)[:12]
            
            ports_info = container.ports if hasattr(container, 'ports') else {}
            attrs = container.attrs if hasattr(container, 'attrs') else {}
            
            container_id = "unknown"
            if hasattr(container, 'id') and container.id:
                container_id = str(container.id)[:12]
            
            return {
                "id": container_id,
                "name": container.name if hasattr(container, 'name') else container_name,
                "status": container.status if hasattr(container, 'status') else "unknown",
                "image": image_info,
                "created": attrs.get("Created", ""),
                "ports": ports_info,
                "networks": list(attrs.get("NetworkSettings", {}).get("Networks", {}).keys()),
            }
        except NotFound:
            return None
        except (DockerException, APIError) as e:
            print(f"Error getting container info: {e}")
            return None
    
    def start_container(self, env_dir: str) -> bool:
        """Start container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            raise DockerError(f"Failed to start container: {e}")
    
    def stop_container(self, env_dir: str) -> bool:
        """Stop container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "down"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            raise DockerError(f"Failed to stop container: {e}")
    
    def restart_container(self, env_dir: str) -> bool:
        """Restart container"""
        return self.stop_container(env_dir) and self.start_container(env_dir)
    
    def build_container(self, env_dir: str) -> bool:
        """Build container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "build"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            raise DockerError(f"Failed to build container: {e}")
    
    def exec_command(self, container_name: str, command: List[str]) -> Optional[str]:
        """Execute command in container"""
        try:
            container = self.client.containers.get(container_name)
            result = container.exec_run(command)
            return result.output.decode('utf-8') if result.output else None
        except (NotFound, DockerException, APIError) as e:
            raise DockerError(f"Failed to execute command: {e}")
    
    def get_logs(self, container_name: str, tail: int = 100, follow: bool = False) -> str:
        """Get container logs"""
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, follow=follow, stream=False)
            return logs.decode('utf-8') if logs else ""
        except (NotFound, DockerException, APIError) as e:
            raise DockerError(f"Failed to get logs: {e}")
    
    def list_networks(self) -> List[str]:
        """List Docker networks"""
        try:
            networks = self.client.networks.list()
            return [net.name for net in networks if net.name]
        except (DockerException, APIError) as e:
            raise DockerError(f"Failed to list networks: {e}")
    
    def network_exists(self, network_name: str) -> bool:
        """Check if network exists"""
        return network_name in self.list_networks()
    
    def create_network(self, network_name: str) -> bool:
        """Create Docker network"""
        try:
            self.client.networks.create(network_name, driver="bridge")
            return True
        except APIError as e:
            if "already exists" in str(e):
                return True
            raise DockerError(f"Failed to create network: {e}")
