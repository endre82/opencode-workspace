#!/usr/bin/env python3
"""Test Step 3 layout structure"""

import sys
from pathlib import Path

# Read the wizard file
wizard_file = Path("/home/endre/opencode-workspace/envman/screens/creation/wizard.py")
content = wizard_file.read_text()

print("=" * 70)
print("Step 3 Layout Verification")
print("=" * 70)
print()

# Extract _render_step_3 method
step_3_start = content.find("def _render_step_3(self)")
step_3_end = content.find("\n    def _render_step_4", step_3_start)
step_3_code = content[step_3_start:step_3_end]

# Count critical widgets
section_headers = step_3_code.count('classes="section-header"')
switches = step_3_code.count('Switch(')
inputs = step_3_code.count('Input(')
hints = step_3_code.count('classes="mount-hint"')
radio_sets = step_3_code.count('RadioSet(')

print(f"✓ Section Headers: {section_headers} (expected: 4)")
print(f"✓ Switches: {switches} (expected: 4 - global, project, worktree, shared_auth)")
print(f"✓ Inputs: {inputs} (expected: 4 - env, global, project, worktree)")
print(f"✓ Mount Hints: {hints}")
print(f"✓ RadioSets: {radio_sets} (expected: 1 - SSH mode)")
print()

# Verify all required IDs are present
required_ids = [
    'ssh-mode',
    'switch-global',
    'switch-project', 
    'switch-worktree',
    'switch-shared-auth',
    'input-env-path',
    'input-global-path',
    'input-project-path',
    'input-worktree-path',
    'row-global',
    'row-project',
    'row-worktree',
    'row-shared-auth'
]

print("Widget ID Verification:")
print("-" * 70)
all_present = True
for widget_id in required_ids:
    present = f'id="{widget_id}"' in step_3_code
    status = "✓" if present else "✗"
    print(f"{status} {widget_id}")
    if not present:
        all_present = False

print()

# Check for layout-breaking CSS classes
bad_classes = ['mount-label', 'mount-toggle', 'mount-input']
print("CSS Class Check (should NOT be present):")
print("-" * 70)
clean_css = True
for css_class in bad_classes:
    present = f'classes="{css_class}"' in step_3_code
    if present:
        print(f"✗ Found '{css_class}' - this breaks layout!")
        clean_css = False

if clean_css:
    print("✓ No layout-breaking CSS classes found")

print()

# Verify compact layout (no excessive newlines)
excessive_newlines = step_3_code.count('\\n\\n')
print(f"Excessive newlines (\\n\\n): {excessive_newlines}")
if excessive_newlines > 2:
    print(f"⚠ Warning: Found {excessive_newlines} double newlines, layout may not be compact")
else:
    print("✓ Layout appears compact")

print()
print("=" * 70)

if section_headers == 4 and switches == 4 and inputs == 4 and all_present and clean_css:
    print("✅ ALL CHECKS PASSED - Layout is correct")
    print("=" * 70)
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED - Review issues above")
    print("=" * 70)
    sys.exit(1)
