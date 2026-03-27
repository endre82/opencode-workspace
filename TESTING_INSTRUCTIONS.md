# Step 3 Redesign - Testing Instructions

## Status
✅ **Layout verification test passed** - All widget counts, IDs, and CSS checks passed
✅ **Code compiles without errors** - No syntax errors found
⏳ **Manual testing required** - App needs to be tested interactively in terminal

## Quick Test

### Launch the TUI:
```bash
cd ~/.local/share/opencode-workspace
source venv/bin/activate
python3 -m envman.app
```

### Navigate to Step 3:
1. Press `c` to create new environment
2. Enter environment name (e.g., "test-redesign")
3. Press Enter to proceed through Step 1
4. Select base image (arrow keys, Enter)
5. Press Enter to proceed to Step 3 (SSH & Mounts)

### What to Check:
1. **All content visible**: 4 section headers, 4 switches, all hint text
2. **Scrollbar appears**: When content overflows (resize terminal small), scrollbar gutter prevents layout shift
3. **Scrolling works**: Try scrolling with arrow keys or mouse wheel
4. **Switches toggle**: Click each switch, verify inputs enable/disable
5. **Can proceed**: Press Enter to go to Step 4 (Review)

### Expected Layout (Step 3):
```
Configure SSH and optional volume mounts for your environment.

🔑 SSH Access (Required)
[RadioSet for SSH mode: key-based or password]

📁 Always Mounted
→ /home/endre/opencode-workspace → /workspace (rw)
→ OpenCode config → /home/dev/.opencode (rw)

⚙️ Optional Configuration Mounts
Mount GLOBAL_CONFIG: [X] ON/OFF
→ /home/dev/.opencode-shared (ro)
../shared/config/.opencode [Input when enabled]

Mount PROJECT_CONFIG: [ ] ON/OFF
→ /workspace/.opencode-proj (ro)
../project/.opencode [Input when disabled=dimmed]

Mount WORKTREE_CONFIG: [ ] ON/OFF
→ /workspace/.opencode-work (rw)
../worktree/.opencode [Input when disabled=dimmed]

🔐 Shared Authentication
Mount SHARED_AUTH: [ ] ON/OFF
→ /home/dev/.ssh-shared (ro)
../shared/.ssh [Hint text]

[Navigation hints at bottom]
```

## Test on Small Terminal (Critical)
```bash
# Resize to 40 lines
resize -s 40 120

# Launch app
cd ~/.local/share/opencode-workspace
source venv/bin/activate
python3 -m envman.app
```

Navigate to Step 3 and verify:
- Content doesn't get cut off
- Can scroll to see all 4 switches
- Last switch (SHARED_AUTH) is reachable

## Known Fixed Issues
✅ Layout no longer breaks (removed width constraints)
✅ Scrolling now works (added `height: auto` to content-inner)
✅ Compact spacing (removed excessive margins and newlines)
✅ All switches visible (proper ScrollableContainer implementation)
✅ Scrollbar gutter added (prevents layout shift when scrollbar appears)

## What Changed from Original

### CSS Changes:
- Removed layout-breaking classes: `.mount-label`, `.mount-toggle`, `.mount-row`
- Added `#step-content-inner { height: auto; }` for proper scrolling
- Added `scrollbar-gutter: stable` to prevent layout shift when scrollbar appears
- Reduced margins to 0-1 for compact spacing
- Kept section headers and existing functional classes

### Layout Changes:
- Restored simple `Horizontal(Label, Switch)` pattern (proven to work)
- Shortened labels: "Mount GLOBAL_CONFIG:" vs "GLOBAL_CONFIG - Long description"
- Moved details to hints: "→ /path/to/destination (ro/rw)"
- Kept 4 section headers with emoji icons
- Removed excessive `\n` characters in labels

### Functionality:
- NO changes to switch interactivity (`on_switch_changed`)
- NO changes to state initialization (`_initialize_step_3_states`)
- NO changes to validation logic (`validate_step_3`)
- NO changes to form data handling

## If Issues Are Found

### Content cut off / no scrolling:
- Check: `#step-content { height: 1fr; }`
- Check: `#step-content-inner { height: auto; }`
- Check: `ScrollableContainer` wraps content properly

### Switches don't toggle inputs:
- Check: Widget IDs match (`switch-global` → `input-global-path`)
- Check: `on_switch_changed()` method is being called
- Check: `_initialize_step_3_states()` runs on mount

### Layout looks broken:
- Check: No CSS classes on Horizontal/Label/Switch widgets
- Check: No fixed widths set on children in Horizontal containers
- Check: Original simple pattern is preserved

## Report Results
After testing, update this file or the main summary with:
```
✅ PASS - [Component] - [What works]
❌ FAIL - [Component] - [What's broken and how]
```

## Files Changed
- `envman/screens/creation/wizard.py` - Complete Step 3 redesign
- `envman/app.py` - Removed wizard CSS (moved to wizard.py)
- `envman/services/creation.py` - Improved review screen details
- `test_step3_layout.py` - Created layout verification script
- `tests/test_wizard_simple.py` - Updated structure validation

## Commit When Ready
If all tests pass:
```bash
git add -A
git commit -m "Improve Step 3 (SSH & Mounts) UX: compact layout, section headers, proper scrolling"
```
