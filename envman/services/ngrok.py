"""NgrokService for managing on-demand ngrok tunnels"""

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any
import urllib.request
import urllib.error


class NgrokService:
    """Service for starting/stopping ngrok tunnels on-demand"""
    
    def __init__(self):
        """Initialize NgrokService"""
        self.process: Optional[subprocess.Popen] = None
        self.tunneled_env_name: Optional[str] = None
        self.tunneled_service: Optional[str] = None
        self.config_dir = Path.home() / ".local" / "share" / "opencode-workspace" / "ngrok"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = "http://127.0.0.1:4040/api/tunnels"
    
    def is_available(self) -> bool:
        """Check if ngrok binary is installed"""
        return shutil.which("ngrok") is not None
    
    def is_running(self) -> bool:
        """Check if ngrok process is currently running"""
        if self.process is None:
            return False
        # Check if process is still alive
        return self.process.poll() is None
    
    def start(
        self,
        env_name: str,
        service: str,
        port: int,
    ) -> str:
        """
        Start ngrok tunnel for a specific service.
        
        If a tunnel is already running for a different service, it will be stopped first.
        
        Args:
            env_name: Name of the environment being tunneled
            service: Service name ('opencode' or 'vscode')
            port: Local port for the service
        
        Returns:
            Public URL string (e.g., https://abc.ngrok-free.app)
        
        Raises:
            RuntimeError: If ngrok is not installed or tunnel setup fails
        """
        if not self.is_available():
            raise RuntimeError(
                "ngrok is not installed. Install it with: snap install ngrok "
                "or visit https://ngrok.com/download"
            )
        
        # Stop any existing tunnel for a different service
        if self.is_running() and self.tunneled_service != service:
            self.stop()
        
        # If already tunneling this service, just return current URL
        if self.is_running() and self.tunneled_service == service:
            return self._get_tunnel_url(service)
        
        # Write ngrok config
        config_path = self._write_config(env_name, service, port)
        
        try:
            # Start ngrok process — pass default config first (authtoken) then ours (tunnel)
            default_config = Path.home() / ".config" / "ngrok" / "ngrok.yml"
            cmd = ["ngrok", "start", "--all"]
            if default_config.exists():
                cmd.extend(["--config", str(default_config)])
            cmd.extend(["--config", str(config_path)])

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.tunneled_env_name = env_name
            self.tunneled_service = service
            
            # Wait for tunnel to come up (poll API)
            url = self._wait_for_tunnel(service)
            return url
        
        except Exception as e:
            if self.process is not None:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=2)
                except Exception:
                    pass
            self.tunneled_env_name = None
            self.tunneled_service = None
            self.process = None
            raise RuntimeError(f"Failed to start ngrok tunnel: {e}")
    
    def stop(self) -> None:
        """Stop the current ngrok tunnel"""
        if self.process is not None:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            except Exception:
                pass  # Already dead or can't kill
            finally:
                self.process = None
                self.tunneled_env_name = None
                self.tunneled_service = None
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current tunnel status.
        
        Returns:
            Dict with keys: env_name, service, url, pid
            or None if no tunnel is running
        """
        if not self.is_running():
            return None
        
        try:
            url = self._get_tunnel_url(self.tunneled_service)
            return {
                "env_name": self.tunneled_env_name,
                "service": self.tunneled_service,
                "url": url,
                "pid": self.process.pid if self.process else None,
            }
        except Exception:
            return None
    
    def cleanup(self) -> None:
        """Clean up: stop tunnel and kill any orphaned process"""
        self.stop()
    
    # ─── Private helpers ───────────────────────────────────────────────────────
    
    def _write_config(self, env_name: str, service: str, port: int) -> Path:
        """Write ngrok config file for a single service"""
        config_path = self.config_dir / f"{env_name}-{service}.yml"
        
        config_content = f"""version: "3"
tunnels:
  {service}:
    addr: {port}
    proto: http
"""
        
        config_path.write_text(config_content)
        return config_path
    
    def _wait_for_tunnel(self, service: str, timeout: int = 10) -> str:
        """
        Poll the ngrok API until tunnel is available.
        
        Returns the public URL string.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                url = self._get_tunnel_url(service)
                if url:
                    return url
            except Exception:
                pass
            
            time.sleep(0.5)
        
        raise RuntimeError(
            f"Tunnel setup timed out after {timeout}s. Check ngrok status."
        )
    
    def _get_tunnel_url(self, service: str) -> str:
        """
        Query ngrok API to get the public URL for a service.
        
        Returns the URL string.
        """
        try:
            with urllib.request.urlopen(self.api_url, timeout=2) as response:
                data = json.loads(response.read().decode())
                tunnels = data.get("tunnels", [])
                
                for tunnel in tunnels:
                    if tunnel.get("name") == service:
                        url = tunnel.get("public_url")
                        if url:
                            return url
                
                raise RuntimeError(f"Tunnel '{service}' not found in ngrok API response")
        
        except urllib.error.URLError:
            raise RuntimeError("Could not reach ngrok API (http://127.0.0.1:4040)")
        except json.JSONDecodeError:
            raise RuntimeError("Invalid response from ngrok API")
