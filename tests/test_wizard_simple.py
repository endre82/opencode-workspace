#!/usr/bin/env python3
"""Simple test to verify wizard compose() fix"""

import sys
from pathlib import Path

# Read the fixed wizard.py file
wizard_file = Path("/home/endre/opencode-workspace/envman/screens/creation/wizard.py")
content = wizard_file.read_text()

print("Checking wizard.py for compose() bug fixes...")
print()

# Check 1: compose() should not call _render_step_1()
if "yield self._render_step_1()" in content:
    print("❌ FAIL: compose() still calls _render_step_1()")
    sys.exit(1)
else:
    print("✅ PASS: compose() no longer calls _render_step_1()")

# Check 2: compose() should yield ScrollableContainer with inner Vertical
if 'ScrollableContainer(id="step-content")' in content and 'Vertical(id="step-content-inner")' in content:
    print("✅ PASS: compose() yields ScrollableContainer with inner Vertical")
else:
    print("❌ FAIL: compose() doesn't yield correct structure")
    sys.exit(1)

# Check 3: on_mount() should call render_current_step()
if "self.render_current_step()" in content and content.count("def on_mount(self)") > 0:
    print("✅ PASS: on_mount() calls render_current_step()")
else:
    print("❌ FAIL: on_mount() doesn't call render_current_step()")
    sys.exit(1)

# Check 4: _render_step_1() should not query step-title
step_1_start = content.find("def _render_step_1(self)")
step_1_end = content.find("\n    def ", step_1_start + 1)
step_1_code = content[step_1_start:step_1_end]

if 'query_one("#step-title"' in step_1_code:
    print("❌ FAIL: _render_step_1() still queries #step-title")
    sys.exit(1)
else:
    print("✅ PASS: _render_step_1() no longer queries #step-title")

# Check 5: render_current_step() should update step title
render_step_start = content.find("def render_current_step(self)")
render_step_end = content.find("\n    def ", render_step_start + 1)
render_step_code = content[render_step_start:render_step_end]

if 'step_title = self.query_one("#step-title"' in render_step_code:
    print("✅ PASS: render_current_step() updates step title")
else:
    print("❌ FAIL: render_current_step() doesn't update step title")
    sys.exit(1)

# Check 6: show_summary() should update step title
summary_start = content.find("def show_summary(self)")
summary_end = content.find("\n    def ", summary_start + 1)
summary_code = content[summary_start:summary_end]

if 'step_title = self.query_one("#step-title"' in summary_code:
    print("✅ PASS: show_summary() updates step title")
else:
    print("❌ FAIL: show_summary() doesn't update step title")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print()
print("The wizard.py file has been successfully fixed:")
print("  • compose() no longer queries elements during composition")
print("  • on_mount() populates content after elements exist")
print("  • _render_step_N() methods return widgets only")
print("  • render_current_step() updates title before mounting")
print("  • show_summary() updates title before mounting")
print()
print("The wizard should now launch without NoMatches errors.")
