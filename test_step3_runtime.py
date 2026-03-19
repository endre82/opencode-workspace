#!/usr/bin/env python3
"""
Quick test to verify Step 3 renders without errors.
This will programmatically render the wizard and check Step 3.
"""
import sys
sys.path.insert(0, '/home/endre/.local/share/opencode-workspace')

from envman.screens.creation.wizard import CreationWizard
from envman.services.docker import DockerService
from envman.services.discovery import DiscoveryService
from pathlib import Path

# Create required services
docker_service = DockerService()
discovery_service = DiscoveryService()
workspace_root = Path("/home/endre/.local/share/opencode-workspace")

# Create wizard instance
wizard = CreationWizard(docker_service, discovery_service, workspace_root)

# Simulate being on Step 3
wizard.current_step = 3
wizard.form_data = {
    "env_name": "test-env",
    "base_image": "python:3.12"
}

# Try to render Step 3
try:
    print("Rendering Step 3...")
    step3_widgets = wizard._render_step_3()
    
    # Count widgets
    widget_list = list(step3_widgets)
    print(f"✅ Step 3 rendered successfully")
    print(f"   Total widgets: {len(widget_list)}")
    
    # Try to compose the entire wizard
    print("\nComposing full wizard...")
    composed = list(wizard.compose())
    print(f"✅ Wizard composition successful")
    print(f"   Total top-level widgets: {len(composed)}")
    
    print("\n✅ ALL CHECKS PASSED - No runtime errors")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
