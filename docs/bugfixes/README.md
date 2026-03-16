# Bug Fix Documentation

Chronological documentation of all bugs discovered and fixed in the OpenCode Workspace TUI.

## Bug Timeline

| # | Date | Title | Severity | Status | Affected Components |
|---|------|-------|----------|--------|---------------------|
| 001 | 2026-03-16 | asyncio.to_thread Issue | Critical | ✅ Fixed | Phase 3 & 4 |
| 002 | 2026-03-16 | Wizard Compose Query | Critical | ✅ Fixed | Phase 4 |
| 003 | 2026-03-16 | Widget Mount Lifecycle | Critical | ✅ Fixed | Phase 4 |

## Bug Details

### [Bug #001: asyncio.to_thread Issue](bug-001-asyncio-to-thread.md)

**Discovered:** 2026-03-16  
**Fixed:** 2026-03-16

**Impact:** Container operations and environment creation crashed with `AttributeError: 'Dashboard' object has no attribute 'run_in_thread'`

**Root Cause:** Code used non-existent `self.run_in_thread()` method instead of standard Python `asyncio.to_thread()`

**Fix:** Replaced all 6 occurrences in 2 files:
- `envman/screens/dashboard.py` (5 occurrences)
- `envman/screens/creation/wizard.py` (1 occurrence)

**Result:** All Phase 3 container operations and Phase 4 environment creation now work correctly.

[📄 Read Full Documentation](bug-001-asyncio-to-thread.md)

---

### [Bug #002: Wizard Compose Query](bug-002-wizard-compose.md)

**Discovered:** 2026-03-16 (after fixing Bug #001)  
**Fixed:** 2026-03-16

**Impact:** Wizard crashed on launch with `NoMatches: No nodes match '#step-title' on CreationWizard()`

**Root Cause:** The `compose()` method called `_render_step_1()` which tried to query `#step-title` element before it was mounted to the DOM.

**Fix:** Applied Separation of Concerns pattern for Textual widget lifecycle:
- `compose()`: Create structure only, no queries
- `on_mount()`: Populate content after elements exist
- `_render_step_N()`: Return widgets only, don't query siblings
- `render_current_step()`: Update title + mount content

**Changes:** Modified 9 methods in `wizard.py` (~25 lines)

**Result:** Wizard now launches successfully.

[📄 Read Full Documentation](bug-002-wizard-compose.md)

---

### [Bug #003: Widget Mount Lifecycle](bug-003-widget-mount.md)

**Discovered:** 2026-03-16 (after fixing Bug #002)  
**Fixed:** 2026-03-16

**Impact:** Wizard crashed after Bug #002 fix with `MountError: Can't mount widget(s) before Vertical() is mounted`

**Root Cause:** `_render_step_N()` methods created `Vertical()` containers and called `.mount()` to add children. You cannot call `.mount()` on unmounted containers in Textual.

**Fix:** Used Textual's Constructor Pattern where widgets are passed as constructor arguments:

```python
# Before (broken)
container = Vertical()
container.mount(Label("..."))
return container

# After (fixed)
return Vertical(
    Label("..."),
    Input(...),
)
```

**Changes:** Refactored 5 methods in `wizard.py` (~60 lines):
- `_render_step_1()` to `_render_step_4()`
- `_render_summary()`

**Result:** Wizard now works completely from launch to environment creation.

[📄 Read Full Documentation](bug-003-widget-mount.md)

---

## Bug Fix Impact Summary

### What Was Broken

**Before Fixes:**
- ❌ Container operations crashed (start/stop/restart/build)
- ❌ Wizard could not launch
- ❌ Environment creation did not work

### What's Working Now

**After All Fixes:**
- ✅ All container operations work (Phase 3)
- ✅ Wizard launches and navigates correctly (Phase 4)
- ✅ All 4 wizard steps render and validate
- ✅ Environment creation works end-to-end (Phase 4)

## Development Timeline

**March 16, 2026:**
1. **Morning:** Discovered Bug #001 during Phase 3/4 review
2. **Morning:** Fixed Bug #001 in 2 files (6 occurrences)
3. **Afternoon:** Tested fix, discovered Bug #002
4. **Afternoon:** Fixed Bug #002 with lifecycle pattern changes
5. **Evening:** Tested fix, discovered Bug #003
6. **Evening:** Fixed Bug #003 with constructor pattern
7. **Evening:** All phases verified working

**Total Bugs Fixed:** 3  
**Total Time:** ~2.5 hours (including documentation)  
**Files Modified:** 2 (`dashboard.py`, `wizard.py`)

## Key Learnings

### Python & Textual Best Practices

1. **Use standard library functions:**
   - ✅ Use `asyncio.to_thread()` (standard Python)
   - ❌ Don't invent custom async methods

2. **Respect Textual widget lifecycle:**
   - ✅ Create structure in `compose()`
   - ✅ Populate content in `on_mount()` or later
   - ❌ Don't query widgets during `compose()`

3. **Use proper widget construction:**
   - ✅ Pass children as constructor arguments
   - ❌ Don't call `.mount()` on unmounted containers

## Quick Links

- [Feature Documentation](../features/) - What was implemented
- [Summaries](../summaries/) - Quick reference guides
- [Guides](../guides/) - User how-tos
- [Main Documentation](../README.md) - Documentation index

---

**All bugs fixed by:** OpenCode AI Assistant  
**Status:** Production-Ready ✅
