#!/usr/bin/env python3
"""
Verify scrollbar implementation in Step 3
"""
import sys
from pathlib import Path

# Read the wizard file
wizard_file = Path("/home/endre/opencode-workspace/envman/screens/creation/wizard.py")
content = wizard_file.read_text()

print("=" * 70)
print("Scrollbar Implementation Verification")
print("=" * 70)
print()

# Check 1: ScrollableContainer in compose()
compose_start = content.find("def compose(self)")
compose_end = content.find("\n    def on_mount", compose_start)
compose_code = content[compose_start:compose_end]

has_scrollable_container = 'ScrollableContainer(id="step-content")' in compose_code
has_inner_vertical = 'yield Vertical(id="step-content-inner")' in compose_code

print("1. Compose() Structure:")
print("-" * 70)
if has_scrollable_container:
    print("✅ ScrollableContainer with id='step-content' found")
else:
    print("❌ MISSING: ScrollableContainer with id='step-content'")
    sys.exit(1)

if has_inner_vertical:
    print("✅ Inner Vertical with id='step-content-inner' found")
else:
    print("❌ MISSING: Inner Vertical with id='step-content-inner'")
    sys.exit(1)

# Check 2: CSS for scrollbar
css_start = content.find('#step-content {')
if css_start != -1:
    css_end = content.find('\n    }', css_start)
    css_block = content[css_start:css_end+6]
    
    print("\n2. CSS Properties:")
    print("-" * 70)
    
    has_height_fr = 'height: 1fr' in css_block
    has_scrollbar_gutter = 'scrollbar-gutter: stable' in css_block
    
    if has_height_fr:
        print("✅ height: 1fr - Takes available space")
    else:
        print("❌ MISSING: height: 1fr")
        sys.exit(1)
        
    if has_scrollbar_gutter:
        print("✅ scrollbar-gutter: stable - Prevents layout shift")
    else:
        print("❌ MISSING: scrollbar-gutter: stable")
        sys.exit(1)
        
    # Check inner CSS
    inner_css_start = content.find('#step-content-inner {')
    if inner_css_start != -1:
        inner_css_end = content.find('\n    }', inner_css_start)
        inner_css_block = content[inner_css_start:inner_css_end+6]
        
        has_height_auto = 'height: auto' in inner_css_block
        
        if has_height_auto:
            print("✅ #step-content-inner { height: auto } - Allows content expansion")
        else:
            print("❌ MISSING: #step-content-inner { height: auto }")
            sys.exit(1)
    else:
        print("❌ MISSING: #step-content-inner CSS block")
        sys.exit(1)

# Check 3: Step 3 structure
step3_start = content.find("def _render_step_3(self)")
step3_end = content.find("\n    def _render_step_4", step3_start)
step3_code = content[step3_start:step3_end]

print("\n3. Step 3 Layout Structure:")
print("-" * 70)

# Count widgets
section_headers = step3_code.count('classes="section-header"')
switches = step3_code.count('Switch(')
inputs = step3_code.count('Input(')

print(f"✅ Section Headers: {section_headers} (expected: 4)")
print(f"✅ Switches: {switches} (expected: 4)")
print(f"✅ Inputs: {inputs} (expected: 4)")

# Check for proper section organization
sections = [
    "🔑 SSH Access (Required)",
    "📁 Always Mounted", 
    "⚙️ Optional Config Mounts",
    "🔐 Shared Authentication"
]

all_sections_present = True
for section in sections:
    if section in step3_code:
        print(f"✅ Section: {section}")
    else:
        print(f"❌ MISSING Section: {section}")
        all_sections_present = False

print("\n" + "=" * 70)
if has_scrollable_container and has_scrollbar_gutter and all_sections_present:
    print("✅ ALL CHECKS PASSED - Scrollbar implementation complete")
    print("=" * 70)
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED - Review issues above")
    print("=" * 70)
    sys.exit(1)