#!/usr/bin/env python3
"""Test docker-compose.yml generation with volume mounts"""

import sys
import yaml
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from envman.services.creation import CreationService

def test_docker_compose_generation():
    """Test that docker-compose.yml generation produces valid YAML"""

    print("Testing docker-compose.yml generation...")

    # Create a temporary directory for testing
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Initialize creation service with actual workspace
        creation_service = CreationService(project_dir)

        # Test configurations - just the mount flags
        test_configs = [
            {
                'mount_global_config': False,
                'mount_project_config': False,
            },
            {
                'mount_global_config': True,
                'mount_project_config': False,
            },
            {
                'mount_project_config': True,
                'mount_global_config': False,
            },
            {
                'mount_global_config': True,
                'mount_project_config': True,
            },
        ]

        template_path = project_dir / "environments" / "template" / "docker-compose.yml.template"

        for i, config in enumerate(test_configs):
            print(f"\nTesting config {i+1}: {config}")

            # Generate docker-compose.yml directly
            target_file = temp_path / f"test-compose-{i+1}.yml"
            try:
                creation_service._create_compose_file(target_file, template_path, "test-env", config)

                # Validate YAML syntax
                with open(target_file, 'r') as f:
                    yaml_content = yaml.safe_load(f)

                print("✅ YAML syntax is valid")

                # Check volume mounts
                services = yaml_content.get('services', {})
                if not services:
                    print("❌ No services found in YAML")
                    continue

                service_name = list(services.keys())[0]
                volumes = services[service_name].get('volumes', [])

                # Check for expected mounts
                has_global = any('${GLOBAL_CONFIG}' in vol for vol in volumes)
                has_project = any('${PROJECT_CONFIG}' in vol for vol in volumes)

                if config['mount_global_config'] and not has_global:
                    print("❌ GLOBAL_CONFIG mount missing")
                elif not config['mount_global_config'] and has_global:
                    print("❌ GLOBAL_CONFIG mount should not be present")
                else:
                    print("✅ GLOBAL_CONFIG mount correct")

                if config['mount_project_config'] and not has_project:
                    print("❌ PROJECT_CONFIG mount missing")
                elif not config['mount_project_config'] and has_project:
                    print("❌ PROJECT_CONFIG mount should not be present")
                else:
                    print("✅ PROJECT_CONFIG mount correct")

            except yaml.YAMLError as e:
                print(f"❌ YAML parsing error: {e}")
                # Print the content for debugging
                if target_file.exists():
                    with open(target_file, 'r') as f:
                        print("Generated content:")
                        print(f.read())
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    print("\n" + "="*60)
    print("Docker-compose.yml generation test completed")

if __name__ == "__main__":
    test_docker_compose_generation()