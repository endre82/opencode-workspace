# Manual Testing Guide - Step 3 Redesign

## Test Checklist

### 1. Launch and Navigate
```bash
cd ~/.local/share/opencode-workspace
python3 -m envman.app
```
- Press `c` to create new environment
- Navigate to Step 3 (SSH & Mounts)

### 2. Visual Layout Check
- [ ] All 4 section headers visible with emoji icons:
  - 🔑 SSH Access (Required)
  - 📁 Always Mounted
  - ⚙️ Optional Configuration Mounts
  - 🔐 Shared Authentication
- [ ] All 4 switches visible (may need scrolling):
  - Mount GLOBAL_CONFIG
  - Mount PROJECT_CONFIG
  - Mount WORKTREE_CONFIG
  - Mount SHARED_AUTH
- [ ] All mount hints visible with proper format:
  - Example: "→ /home/dev/.opencode-shared (ro)"
- [ ] No content cut off
- [ ] Compact layout with minimal whitespace

### 3. Scrolling Test (Critical)
- Resize terminal to ~40 lines height: `resize -s 40 120`
- [ ] Can scroll down to see all content
- [ ] Last switch (SHARED_AUTH) is reachable
- [ ] Scroll indicator shows when content overflows
- [ ] Smooth scrolling with arrow keys or mouse wheel

### 4. Switch Interactivity Test
For each optional mount switch:
- [ ] **GLOBAL_CONFIG Switch**:
  - Toggle ON: Input below becomes enabled (bright)
  - Toggle OFF: Input becomes disabled (dim)
  - Path input accepts text when enabled
  
- [ ] **PROJECT_CONFIG Switch**:
  - Same behavior as GLOBAL_CONFIG
  
- [ ] **WORKTREE_CONFIG Switch**:
  - Same behavior as GLOBAL_CONFIG
  
- [ ] **SHARED_AUTH Switch**:
  - Toggle ON: Enables (no input, just toggle)
  - Toggle OFF: Disabled state

### 5. Validation Test
- [ ] Can proceed to Step 4 (Review) with all switches OFF
- [ ] Can proceed with GLOBAL_CONFIG ON and valid path
- [ ] Can proceed with all switches ON and valid paths
- [ ] Cannot proceed with switch ON but empty/invalid path (should show error)

### 6. Review Screen Test
Navigate to Step 4 (Review):
- [ ] SSH mode displayed correctly
- [ ] Always-mounted volumes shown:
  - Workspace mount
  - OpenCode config mount
- [ ] Optional mounts shown only when enabled:
  - Shows source path → destination
  - Shows read-only (ro) or read-write (rw) mode
  - Example: `../shared/config/.opencode → /home/dev/.opencode-shared (ro)`

### 7. Complete Wizard Flow
- [ ] Create a test environment with optional mounts enabled
- [ ] Verify environment is created successfully
- [ ] Check Docker Compose file has correct volume mounts

### 8. Edge Cases
- [ ] Navigate back from Step 4 to Step 3: state preserved
- [ ] Navigate back from Step 3 to Step 2: no errors
- [ ] Very small terminal (20 lines): still functional with scrolling
- [ ] Very wide terminal (200+ cols): layout doesn't break
- [ ] Toggle switches rapidly: no lag or UI glitches

## Expected Behavior Summary

### Working Correctly:
- ✅ All 4 switches visible and functional
- ✅ Scrolling works on small terminals
- ✅ Switch toggle enables/disables inputs with visual feedback
- ✅ Compact layout with clear section headers
- ✅ Validation prevents invalid configurations
- ✅ Review screen shows detailed mount information

### Known Issues:
- None expected (all fixed in iteration 2)

## Troubleshooting

If switches are not visible:
1. Check terminal size: `echo $LINES x $COLUMNS`
2. Try scrolling down with arrow keys
3. Check CSS: `#step-content-inner { height: auto; }` must be present

If scrolling doesn't work:
1. Verify ScrollableContainer is wrapping content
2. Check that `#step-content { height: 1fr; }` is set
3. Ensure no fixed heights on parent containers

If switches don't toggle inputs:
1. Check `on_switch_changed()` method is connected
2. Verify widget IDs match: `switch-global`, `input-global-path`, etc.
3. Check `_initialize_step_3_states()` is called on step mount

## Report Format

After testing, report:
```
✅ PASS - [Test name] - [Brief note]
❌ FAIL - [Test name] - [Describe issue]
```

Example:
```
✅ PASS - Visual Layout - All sections visible, compact spacing
✅ PASS - Scrolling (40 lines) - Smooth, all content reachable
✅ PASS - Switch Toggle - Inputs enable/disable correctly
❌ FAIL - Validation - Empty path accepted (should show error)
```
