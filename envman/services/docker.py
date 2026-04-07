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
    
    def start_container(self, env_dir: str) -> tuple[bool, str]:
        """Start container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            raise DockerError(f"Failed to start container: {e}")
    
    def stop_container(self, env_dir: str) -> tuple[bool, str]:
        """Stop container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "down"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            raise DockerError(f"Failed to stop container: {e}")
    
    def restart_container(self, env_dir: str) -> tuple[bool, str]:
        """Restart container"""
        stop_success, stop_output = self.stop_container(env_dir)
        if not stop_success:
            return (False, stop_output)
        
        start_success, start_output = self.start_container(env_dir)
        return (start_success, stop_output + "\n" + start_output)
    
    def build_container(self, env_dir: str) -> tuple[bool, str]:
        """Build container using docker compose"""
        try:
            result = subprocess.run(
                ["docker", "compose", "build"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            raise DockerError(f"Failed to build container: {e}")
    
    def build_and_start_container(self, env_dir: str) -> tuple[bool, str]:
        """Build and start container (used on first creation)"""
        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d", "--build"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            raise DockerError(f"Failed to build and start container: {e}")
    
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
    
    def stream_logs(self, container_name: str, tail: int = 100):
        """Stream container logs (generator)"""
        try:
            container = self.client.containers.get(container_name)
            for line in container.logs(tail=tail, follow=True, stream=True):
                yield line.decode('utf-8', errors='replace')
        except (NotFound, DockerException, APIError) as e:
            raise DockerError(f"Failed to stream logs: {e}")
    
    def inspect_container(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed container inspection data"""
        try:
            container = self.client.containers.get(container_name)
            return container.attrs
        except NotFound:
            return None
        except (DockerException, APIError) as e:
            raise DockerError(f"Failed to inspect container: {e}")
    
    def get_container_stats(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get container resource usage statistics"""
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)
            return stats
        except NotFound:
            return None
        except (DockerException, APIError) as e:
            raise DockerError(f"Failed to get container stats: {e}")
    
    def remove_container(self, env_dir: str, force: bool = False, volumes: bool = False) -> tuple[bool, str]:
        """Remove container using docker compose"""
        try:
            command = ["docker", "compose", "down"]
            if volumes:
                command.append("--volumes")
            if force:
                command.append("--remove-orphans")
            
            result = subprocess.run(
                command,
                cwd=env_dir,
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return (result.returncode == 0, output)
        except Exception as e:
            raise DockerError(f"Failed to remove container: {e}")
    
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
