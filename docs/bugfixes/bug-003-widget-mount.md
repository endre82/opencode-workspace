# Bug #003: Widget Mount Lifecycle Error

**Date:** 2026-03-16  
**Status:** ✅ FIXED  
**Severity:** Critical  
**Files Modified:** `envman/screens/creation/wizard.py`

## Bug Summary

After fixing Bug #002 (wizard compose query issue), the wizard still crashed when attempting to launch with a new error:

```
MountError: Can't mount widget(s) before Vertical() is mounted
```

### Root Cause

The `_render_step_N()` methods were creating `Vertical()` containers and calling `.mount()` to add child widgets. However, in Textual, you cannot call `.mount()` on a container that hasn't been mounted to the DOM yet.

**Broken Code Pattern:**
```python
def _render_step_1(self) -> Container:
    container = Vertical()
    container.mount(Label("Environment Name:"))  # ❌ Can't mount to unmounted container!
    container.mount(Input(...))
    return container
```

**Why This Fails:**
- Creates a new `Vertical()` container
- Tries to mount widgets to it using `.mount()`
- The container itself isn't mounted to the DOM yet
- Textual throws `MountError`

## Solution

Used **Textual's Constructor Pattern** where widgets are passed as constructor arguments and become children at construction time:

**Fixed Code Pattern:**
```python
def _render_step_1(self) -> Container:
    return Vertical(
        Label("Environment Name (required):"),
        Input(
            value=self.config.get('name', ''),
            placeholder="e.g., dev3, my-project",
            id="input-name"
        ),
        Static("", id="error-name"),
        # ... more widgets
    )
```

**Why This Works:**
- Widgets are passed as constructor arguments to `Vertical()`
- Textual adds them as children internally during construction
- No `.mount()` calls needed
- No lifecycle issues - children exist from creation

## Changes Made

### File: `envman/screens/creation/wizard.py`

**Methods Refactored (5 total):**

1. **`_render_step_1()`** (lines 125-147)
   - Changed from container + `.mount()` calls to single `return Vertical(...)`
   - 9 widgets as constructor arguments

2. **`_render_step_2()`** (lines 149-165)
   - Same pattern applied
   - Special case: `RadioSet()` also uses constructor pattern for `RadioButton` children

3. **`_render_step_3()`** (lines 167-198)
   - Same pattern applied
   - Special case: `Horizontal()` containers also built with constructor pattern

4. **`_render_step_4()`** (lines 200-223)
   - Same pattern applied

5. **`_render_summary()`** (lines 225-233)
   - Same pattern applied

### Code Comparison

**Before (Broken):**
```python
def _render_step_3(self) -> Container:
    container = Vertical()
    container.mount(Static("Configure which configurations to mount:\n"))
    
    global_switch = Switch(value=self.config['mount_global_config'], id="switch-global")
    container.mount(Horizontal(
        Label("Mount GLOBAL_CONFIG (shared OpenCode config):"),
        global_switch
    ))
    container.mount(Input(...))
    
    return container
```

**After (Fixed):**
```python
def _render_step_3(self) -> Container:
    return Vertical(
        Static("Configure which configurations to mount:\n"),
        Horizontal(
            Label("Mount GLOBAL_CONFIG (shared OpenCode config):"),
            Switch(value=self.config['mount_global_config'], id="switch-global"),
        ),
        Input(...),
    )
```

## Validation

### Testing
- ✅ Wizard launches without errors (press 'n' from dashboard)
- ✅ Step 1 renders with all inputs
- ✅ Forward navigation through all 4 steps works
- ✅ Back button navigation works
- ✅ Summary screen displays
- ✅ Environment creation succeeds

### Deployment
- ✅ Fixed file deployed to `~/.local/share/opencode-workspace/`
- ✅ Source and installed versions verified identical

## Impact

### Fixed
✅ Wizard now launches and navigates correctly  
✅ All 4 steps render properly  
✅ Summary screen displays  
✅ Environment creation works end-to-end

### No Regressions
✅ All widget IDs preserved  
✅ All input values preserved  
✅ All validation logic intact  
✅ All event handlers unchanged

## Key Learnings

### Textual Widget Construction Best Practices

**✅ DO:** Use constructor pattern for static widget hierarchies
```python
return Vertical(
    Label("Title"),
    Input(id="my-input"),
    Button("Submit"),
)
```

**❌ DON'T:** Use `.mount()` on unmounted containers
```python
container = Vertical()
container.mount(Label("Title"))  # Fails if container not mounted
```

### When to Use Each Pattern

1. **Constructor Pattern** (what we used):
   - Creating widgets programmatically to return
   - Building static widget hierarchies
   - Widgets known at creation time

2. **`.mount()` Method** (when to use):
   - Adding widgets to already-mounted containers
   - Dynamic widget addition after initial composition
   - In `on_mount()` or later lifecycle hooks

## Timeline

**2026-03-16:**
- 🔍 Discovered bug after fixing Bug #002
- 📋 Analyzed error and Textual documentation
- 🎯 Chose constructor pattern as solution
- ⚡ Fixed 5 methods in wizard.py (~60 lines)
- ✅ Deployed and verified fix
- 📝 Created documentation

**Total Time:** ~30 minutes

## Related Bugs

This bug was discovered immediately after fixing:
- **Bug #002:** Wizard Compose Query Issue

Both bugs prevented the wizard from functioning. With both fixes applied, the wizard now works completely.

## References

- **Textual Documentation:** https://textual.textualize.io/guide/widgets/
- **Constructor Pattern:** https://textual.textualize.io/api/containers/#textual.containers.Vertical
- **Bug #001:** `docs/bugfixes/bug-001-asyncio-to-thread.md`
- **Bug #002:** `docs/bugfixes/bug-002-wizard-compose.md`
- **Phase 4 Docs:** `docs/features/phase4-creation-wizard.md`

---

**Fixed by:** OpenCode AI Assistant  
**Date:** March 16, 2026  
**Status:** Production-Ready ✅
