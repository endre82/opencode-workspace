#!/usr/bin/env python3
"""OpenCode Environment Manager TUI - Main Entry Point"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from envman.app import run_app


def main():
    """Main entry point"""
    try:
        # Run the TUI application
        run_app(base_dir=project_dir)
    
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
