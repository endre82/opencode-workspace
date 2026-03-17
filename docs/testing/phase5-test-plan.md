# Phase 5 Test Plan - Environment Management Features

## Test Environment
- **Date:** March 17, 2026
- **Phase:** Phase 5 - Environment Management
- **Deployment Location:** `~/.local/share/opencode-workspace/`

## Features to Test

### 1. Logs Viewer Screen (`l` key)
**Access:** Dashboard → Select environment → Press `l`

**Test Cases:**
- [ ] **Launch Screen**
  - Select a running environment
  - Press `l` to open logs viewer
  - Verify logs display in real-time
  - Verify toolbar shows filter and search options

- [ ] **Follow Mode**
  - Press `f` to enable follow mode
  - Verify new logs auto-scroll
  - Press `f` again to disable
  - Verify scrolling is manual again

- [ ] **Search Functionality**
  - Press `/` to focus search box
  - Type search term (e.g., "error")
  - Verify matching lines are highlighted
  - Clear search, verify highlighting removed

- [ ] **Filter by Level**
  - Use dropdown to filter by INFO
  - Verify only INFO logs shown
  - Try WARN, ERROR, DEBUG filters
  - Return to ALL to see everything

- [ ] **Export Logs**
  - Press `e` to export
  - Verify file created with timestamp
  - Check file contents match displayed logs

- [ ] **Clear Logs**
  - Press `c` to clear
  - Verify log display is cleared

- [ ] **Exit Screen**
  - Press `Esc` to return to dashboard
  - Verify dashboard is active

**Error Cases:**
- [ ] Try on stopped environment (should show warning)
- [ ] Try with no environment selected (should show warning)

---

### 2. Inspect Environment Screen (`i` key)
**Access:** Dashboard → Select environment → Press `i`

**Test Cases:**
- [ ] **Launch Screen**
  - Select any environment (running or stopped)
  - Press `i` to open inspect screen
  - Verify tree view displays container data

- [ ] **Tree Navigation**
  - Expand/collapse tree nodes with Enter/Space
  - Navigate with arrow keys
  - Verify all sections present:
    - Container Details
    - Configuration
    - Network Settings
    - Volume Mounts
    - Resource Usage
    - State Information

- [ ] **Container Details**
  - Verify ID, name, image shown
  - Check created/started timestamps
  - Verify platform information

- [ ] **Network Settings**
  - Verify ports mapping displayed
  - Check IP addresses
  - Verify network mode/gateway

- [ ] **Volume Mounts**
  - Verify all mounted volumes listed
  - Check source and destination paths
  - Verify mount permissions (rw/ro)

- [ ] **Resource Usage** (running containers only)
  - Verify CPU usage percentage
  - Check memory usage (used/limit)
  - Verify disk I/O stats
  - Check network I/O stats

- [ ] **Refresh Data**
  - Press `r` to refresh
  - Verify data updates
  - Check resource stats change (if running)

- [ ] **Exit Screen**
  - Press `Esc` to return to dashboard

**Error Cases:**
- [ ] Try with no environment selected (should show warning)
- [ ] Try on non-existent container (should show warning)

---

### 3. Configure Environment Screen (`c` key)
**Access:** Dashboard → Select environment → Press `c`

**Test Cases:**
- [ ] **Launch Screen**
  - Select any environment
  - Press `c` to open config editor
  - Verify form displays with all sections

- [ ] **Load Existing Configuration**
  - Verify form fields populated from .env file
  - Check all sections: Server, User, Container, Volumes
  - Verify switch and checkbox states

- [ ] **Edit Server Configuration**
  - Toggle "Server Enabled" switch
  - Change server port (e.g., 8080 → 9000)
  - Modify username/password
  - Update CORS origins

- [ ] **Edit User Configuration**
  - Change USER_ID (e.g., 1000)
  - Change GROUP_ID (e.g., 1000)
  - Update TIMEZONE (e.g., "America/New_York")

- [ ] **Edit Container Configuration**
  - Update container name
  - Change hostname

- [ ] **Edit Volume Configuration**
  - Update workspace directory path
  - Modify global/project config paths
  - Toggle mount control checkboxes

- [ ] **Resource Limits Section**
  - Verify warning message displayed
  - Verify fields are commented out/disabled
  - Read note about experimental status

- [ ] **Validation**
  - Enter invalid port (e.g., 70000) → should show error
  - Enter invalid user ID (e.g., -1) → should show error
  - Enter invalid container name (e.g., "test@123") → should show error
  - Enter valid values → should save successfully

- [ ] **Save Configuration**
  - Click "Save" button (or press Ctrl+S)
  - Verify backup created in `/backups/` directory
  - Verify .env file updated
  - Verify success notification shown
  - Verify rebuild warning displayed

- [ ] **Reset Form**
  - Make changes but don't save
  - Click "Reset" button (or press Ctrl+R)
  - Verify form returns to original values

- [ ] **Manual Backup**
  - Click "Backup" button (or press Ctrl+B)
  - Verify backup created without saving changes
  - Check `/backups/` directory for timestamped file

- [ ] **Cancel Changes**
  - Make changes
  - Click "Cancel" button (or press Esc)
  - Return to dashboard
  - Reopen config → verify changes weren't saved

**Error Cases:**
- [ ] Try with no environment selected (should show warning)
- [ ] Try on non-existent .env file (should create new)

---

### 4. Delete Environment Screen (`d` key)
**Access:** Dashboard → Select environment → Press `d`

**Test Cases:**
- [ ] **Launch Screen**
  - Select any environment
  - Press `d` to open delete screen
  - Verify warning message displayed
  - Verify name verification input shown

- [ ] **Name Verification**
  - Try clicking Delete without typing name → should be disabled/fail
  - Type incorrect name → should show error
  - Type correct environment name → delete button enables

- [ ] **Deletion Options**
  - Check "Delete workspace files" checkbox
  - Check "Delete configuration files" checkbox
  - Check "Delete all (entire directory)" checkbox
  - Verify mutual exclusivity (if applicable)

- [ ] **Container Stop & Remove**
  - Select running environment
  - Proceed with deletion
  - Verify container stops first
  - Verify container removed
  - Verify volumes removed (if checked)

- [ ] **Backup Creation**
  - Proceed with deletion
  - Verify backup archive created in `/backups/`
  - Verify backup contains .env file
  - Verify backup contains docker-compose.yml (if present)

- [ ] **File Deletion**
  - Select "Delete workspace files" only
  - Verify workspace directory deleted
  - Verify config files remain

  - Select "Delete configuration files" only
  - Verify .env and docker-compose.yml deleted
  - Verify workspace remains

  - Select "Delete all"
  - Verify entire environment directory deleted

- [ ] **Dashboard Refresh**
  - After successful deletion
  - Verify environment removed from list
  - Verify environment count updated
  - Verify no environment selected

- [ ] **Cancel Deletion**
  - Click Cancel button (or press Esc)
  - Verify no deletion occurred
  - Return to dashboard

**Error Cases:**
- [ ] Try with no environment selected (should show warning)
- [ ] Try on non-existent environment (should handle gracefully)
- [ ] Simulate Docker error (if possible)

---

## Integration Tests

### Cross-Feature Tests
- [ ] **Config → Rebuild → Logs**
  1. Configure environment (change port)
  2. Save configuration
  3. Rebuild container
  4. View logs to verify rebuild
  5. Check new port is active

- [ ] **Inspect → Config → Inspect**
  1. Inspect environment, note current config
  2. Open config editor, make changes
  3. Save and rebuild
  4. Inspect again, verify changes reflected

- [ ] **Create → Configure → Delete**
  1. Create new environment
  2. Configure custom settings
  3. Start environment
  4. View logs to verify startup
  5. Inspect to see configuration
  6. Delete environment completely

---

## Performance Tests

- [ ] **Large Log Files**
  - Generate large log file (>10MB)
  - Open logs viewer
  - Verify log rotation triggered
  - Verify performance remains acceptable

- [ ] **Multiple Operations**
  - Rapidly switch between screens
  - Verify no memory leaks
  - Verify UI remains responsive

- [ ] **Concurrent Access**
  - Open multiple TUI instances (if possible)
  - Verify state consistency

---

## Regression Tests

### Phase 1-4 Features (Verify Still Working)
- [ ] Environment discovery on startup
- [ ] Create new environment wizard
- [ ] Start/stop/restart containers
- [ ] Build containers
- [ ] Dashboard refresh
- [ ] Status updates

---

## Known Issues / Limitations

### Expected Behavior
1. **Resource Limits:** Fields commented out, not editable (by design)
2. **Logs Viewer:** Only works on running containers (expected)
3. **Inspect:** Some data may be unavailable for stopped containers (expected)
4. **Delete:** Irreversible after confirmation (by design)

### To Document
- Backup directory location: `<env_path>/backups/`
- Log rotation: 10MB max, 5 files retained
- Log cleanup: 30 days retention
- Config validation rules
- Rebuild requirement after config changes

---

## Test Results

### Test Session 1: [Date]
**Tester:** [Name]
**Duration:** [Time]
**Results:** 
- Passed: [ ]
- Failed: [ ]
- Blocked: [ ]

**Notes:**
[Add test notes here]

---

## Sign-off

### Development
- [ ] All features implemented
- [ ] Code reviewed
- [ ] Deployed to test environment

### Testing
- [ ] All test cases executed
- [ ] Bugs filed and tracked
- [ ] Regression tests passed

### Documentation
- [ ] User guide created
- [ ] Technical docs updated
- [ ] Release notes prepared

### Approval
- [ ] Ready for production deployment
- [ ] User acceptance complete

**Approved by:** _______________  
**Date:** _______________
