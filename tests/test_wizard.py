#!/usr/bin/env python3
"""Test script to verify wizard launches without errors"""

import sys
from pathlib import Path

# Add the installation directory to path
sys.path.insert(0, str(Path.home() / ".local/share/opencode-workspace"))

from envman.services.docker import DockerService
from envman.services.discovery import DiscoveryService
from envman.screens.creation.wizard import CreationWizard

def test_wizard_instantiation():
    """Test that wizard can be instantiated without errors"""
    workspace_root = Path("/home/endre/opencode-workspace")
    
    print("Creating services...")
    docker_service = DockerService()
    discovery_service = DiscoveryService(workspace_root)
    
    print("Creating wizard...")
    wizard = CreationWizard(
        docker_service=docker_service,
        discovery_service=discovery_service,
        workspace_root=workspace_root
    )
    
    print("Testing compose() method...")
    # This should not raise NoMatches error anymore
    widgets = list(wizard.compose())
    print(f"✓ compose() returned {len(widgets)} widgets")
    
    print("\n✅ SUCCESS: Wizard can be instantiated and composed without errors!")
    print("   The compose() method no longer queries elements during composition.")
    return True

if __name__ == "__main__":
    try:
        test_wizard_instantiation()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
