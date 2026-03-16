#!/usr/bin/env python3
"""
Test that the wizard can be instantiated without errors.
This verifies that all the bug fixes are working correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_wizard_imports():
    """Test that wizard can be imported"""
    try:
        from envman.screens.creation.wizard import CreationWizard
        print("✅ Wizard import successful")
        return True
    except Exception as e:
        print(f"❌ Wizard import failed: {e}")
        return False

def test_wizard_instantiation():
    """Test that wizard can be instantiated"""
    try:
        from envman.screens.creation.wizard import CreationWizard
        from envman.services.docker import DockerService
        from envman.services.discovery import DiscoveryService
        from pathlib import Path
        
        # Create required services
        workspace_root = Path.home() / "opencode-envs"
        docker_service = DockerService()
        discovery_service = DiscoveryService(workspace_root)
        
        # Create wizard instance (this will call __init__ and compose)
        wizard = CreationWizard(
            docker_service=docker_service,
            discovery_service=discovery_service,
            workspace_root=workspace_root
        )
        
        print("✅ Wizard instantiation successful")
        print(f"   - Initial step: {wizard.current_step}")
        print(f"   - Total steps: {wizard.total_steps}")
        print(f"   - Workspace root: {wizard.workspace_root}")
        
        # Test compose method (creates widget structure)
        widgets = list(wizard.compose())
        print(f"✅ Wizard compose successful")
        print(f"   - Generated {len(widgets)} top-level widgets")
        
        return True
    except Exception as e:
        print(f"❌ Wizard instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_render_methods():
    """Test that all render methods work without errors"""
    try:
        from envman.screens.creation.wizard import CreationWizard
        from envman.services.docker import DockerService
        from envman.services.discovery import DiscoveryService
        from pathlib import Path
        
        # Create required services
        workspace_root = Path.home() / "opencode-envs"
        docker_service = DockerService()
        discovery_service = DiscoveryService(workspace_root)
        
        wizard = CreationWizard(
            docker_service=docker_service,
            discovery_service=discovery_service,
            workspace_root=workspace_root
        )
        
        # Test all step render methods
        steps = [
            ("Step 1", wizard._render_step_1),
            ("Step 2", wizard._render_step_2),
            ("Step 3", wizard._render_step_3),
            ("Step 4", wizard._render_step_4),
            ("Summary", wizard._render_summary),
        ]
        
        for name, render_func in steps:
            container = render_func()
            print(f"✅ {name} render successful")
            print(f"   - Type: {type(container).__name__}")
            print(f"   - Children: {len(container.children)}")
        
        return True
    except Exception as e:
        print(f"❌ Render methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Wizard Bug Fixes")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Test", test_wizard_imports),
        ("Instantiation Test", test_wizard_instantiation),
        ("Render Methods Test", test_render_methods),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        result = test_func()
        results.append((name, result))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Wizard is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
