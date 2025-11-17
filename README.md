# CalcsLive-FreeCAD Bridge

**HTTP server bridge enabling Engineering-Driven Modeling (EDM) for FreeCAD through unit-aware calculations.**

> **Repository**: `calcslive-plug-4-freecad`
> **Component**: CalcsLive-FreeCAD Bridge (server component)
> **Main Product**: [CalcsLive Plug for FreeCAD](https://www.calcs.live/help/freecad-integration)

## 🎯 What is Engineering-Driven Modeling?

Engineering-Driven Modeling (EDM) is a **bidirectional workflow** where engineering calculations and CAD geometry work together iteratively.

**Traditional CAD**: Draw → Calculate → Redraw (one-way, manual)

**EDM Bidirectional Flow**:
- **Engineering → Geometry**: Calculations drive optimal design parameters
- **Geometry → Engineering**: Model changes validate against requirements
- **Iterative Loop**: Refine both until design converges

CalcsLive-FreeCAD Bridge enables EDM by connecting FreeCAD with unit-aware cloud calculations - like Autodesk Inventor's Parameters Manager (fx), but with **true unit awareness and versatile calculation capabilities** that enable bidirectional engineering validation.

## 🌉 What is the Bridge?

CalcsLive-FreeCAD Bridge is the **server component** of CalcsLive Plug for FreeCAD. It runs an HTTP server inside FreeCAD, exposing your model parameters via REST API for seamless integration with the CalcsLive Plug dashboard.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CalcsLive Plug for FreeCAD                           │
│                                                                         │
│  FreeCAD Model   CalcsLive-FreeCAD    CalcsLive Plug       CalcsLive    │
│  with VarSet  ⟷       Bridge     ⟷   Dashboard      ⟷  Calculation   │
│  Parameters       (This Component)    (Web Interface)      Articles     |
│                  HTTP Server @ :8787                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**The Bridge serves as**:
- 🔌 Connection layer between FreeCAD and the web-based dashboard
- 📡 HTTP server exposing VarSet data via REST API
- 🔄 Bidirectional data synchronization endpoint
- 🎯 Single source of truth: FreeCAD model parameters

**For the complete system**, see:
- 📚 **[CalcsLive Plug for FreeCAD Integration Guide](https://www.calcs.live/help/freecad-integration)** - Full product documentation
- 🌐 **[CalcsLive Plug Dashboard](https://www.calcs.live/freecad/dashboard)** - Web interface (requires Bridge installed)

---

## Features

### ✅ **Auto-Start HTTP Server**
- Automatically starts when FreeCAD loads
- No manual macro execution required
- Ready for dashboard connections immediately

### ✅ **Complete REST API**
- Export VarSet parameters with full metadata
- Import updated values from CalcsLive calculations
- Manage parameter mappings
- Unit validation and conversion support

### ✅ **Smart Parameter Detection**
- Handles VarSet parameters with and without group prefixes
- Works with names containing underscores (`outer_dia`, `material_density`)
- Supports both legacy (prefix ON) and modern (prefix OFF) workflows

### ✅ **Manual Controls**
- **Plug In CalcsLive** - Start HTTP server manually
- **Unplug CalcsLive** - Stop HTTP server cleanly
- **Plug Status** - Check server status and functionality

### ✅ **Proper Server Management**
- Clean shutdown with socket cleanup
- Port availability checking
- Error handling and status reporting

### ✅ **Zero Vendor Lock-in**

**Your FreeCAD models remain pure FreeCAD files. Always.**

**With CalcsLive Plug**:
- ✨ Unit-aware calculations across 64+ unit categories
- ✨ Cloud calculation library (reusable engineering logic)
- ✨ Real-time design exploration (drag sliders, watch model adapt)
- ✨ Engineering validation (ASME, AISC codes)
- ✨ Bidirectional sync (requirements ⟷ geometry)

**Without CalcsLive Plug**:
- ✅ Models open normally in FreeCAD
- ✅ VarSet parameters work (native FreeCAD feature)
- ✅ Geometry updates when you change values
- ✅ Expressions evaluate correctly
- ✅ Share with users who don't have the Plug
- ✅ No data loss, no vendor lock-in

**How It Works**:
- CalcsLive Plug stores only lightweight metadata in a VarSet property
- If the Plug is removed, this metadata is harmlessly ignored
- Your model continues to work perfectly with native FreeCAD VarSet functionality
- **You are NEVER locked in**

**Stop paying? Uninstall? Change your mind?**
**Your models are ALWAYS yours.** 🛡️

---

## Installation

### Option 1: FreeCAD Addon Manager (Coming Soon)

1. Open FreeCAD
2. Go to **Tools → Addon Manager**
3. Search for "CalcsLive"
4. Click **Install**
5. Restart FreeCAD

### Option 2: Manual Installation

1. **Download or clone this repository**:
   ```bash
   cd "C:\Users\[username]\AppData\Roaming\FreeCAD\Mod"
   # Or on macOS: ~/Library/Application Support/FreeCAD/Mod/
   # Or on Linux: ~/.local/share/FreeCAD/Mod/

   git clone https://github.com/CalcsLive/calcslive-plug-4-freecad.git CalcsLivePlug
   ```

2. **Restart FreeCAD**

3. **Verify auto-start** - Check FreeCAD Report View for:
   ```
   [CalcsLivePlug] ✓ CalcsLive plugged in successfully!
   [CalcsLivePlug] HTTP endpoints are now available
   ```

4. **Test the connection**:
   ```bash
   curl http://127.0.0.1:8787/calcslive/status
   ```

---

## Quick Start

### 1. Prepare Your FreeCAD Model

Create a VarSet object labeled **"PQs"** (case-sensitive):

```
1. Switch to Spreadsheet workbench
2. Create new VarSet: Insert → VarSet
3. Set Label to "PQs"
4. Add properties with prefix OFF for clean expressions:
   - Group: Base
   - Name: L, W, H, etc.
   - ☐ Uncheck "Prefix group name" ← Recommended!
```

**Why prefix OFF?** Clean expressions like `PQs.L` instead of `PQs.Base_L`

### 2. Verify Bridge is Running

The bridge starts automatically when FreeCAD loads. Verify:

```bash
curl http://127.0.0.1:8787/calcslive/status
```

Expected response:
```json
{
  "status": "CalcsLive Plug is running",
  "version": "0.2",
  "endpoints": ["/export", "/import", "/mapping", "/clean-units", "/status"]
}
```

### 3. Open CalcsLive Plug Dashboard

Visit: **[https://www.calcs.live/freecad/dashboard](https://www.calcs.live/freecad/dashboard)**

The dashboard will automatically detect your running Bridge and load your VarSet parameters!

---

## API Endpoints

The Bridge provides **6 REST endpoints** for complete CalcsLive integration:

### **Data Exchange**

**GET `/calcslive/export`** - Export VarSet parameters with full metadata
```bash
curl http://127.0.0.1:8787/calcslive/export
```

Response includes:
- All VarSet "PQs" parameters
- SI base values and units
- Display values and user-preferred units
- Parameter roles (input/output)
- Quantity kinds (Length, Mass, Volume, etc.)
- Existing CalcsLive mappings

**POST `/calcslive/import`** - Update VarSet parameters from CalcsLive
```bash
curl -X POST http://127.0.0.1:8787/calcslive/import \
  -H "Content-Type: application/json" \
  -d '{"updates": [{"path": "VarSet:PQs/L", "value": 1500, "unit": "mm"}]}'
```

### **Mapping Management**

**GET `/calcslive/mapping`** - Get parameter mapping configuration
```bash
curl http://127.0.0.1:8787/calcslive/mapping
```

**POST `/calcslive/mapping`** - Save parameter mapping configuration
```bash
curl -X POST http://127.0.0.1:8787/calcslive/mapping \
  -H "Content-Type: application/json" \
  -d '{"articleId": "abc123", "mappings": {...}}'
```

### **System Information**

**GET `/calcslive/clean-units`** - Get clean units data for validation

**GET `/calcslive/status`** - Check Bridge status and available endpoints

---

## Usage

### Automatic Operation (Recommended)

The Bridge **auto-starts when FreeCAD loads** - no user action required!

**Workflow**:
1. Open FreeCAD with a model containing VarSet labeled "PQs"
2. HTTP server is automatically available at `http://127.0.0.1:8787`
3. Open [CalcsLive Plug Dashboard](https://www.calcs.live/freecad/dashboard)
4. Map VarSet parameters to CalcsLive calculations
5. Synchronize data bidirectionally

### Manual Controls

Switch to **"CalcsLive Plug"** workbench for manual control:

| Command | Description | When to Use |
|---------|-------------|-------------|
| **Plug In CalcsLive** | Start HTTP server | If auto-start failed |
| **Unplug CalcsLive** | Stop HTTP server | Before closing FreeCAD |
| **Plug Status** | Check server status | Troubleshooting connection |

---

## Opinionated Workflow: Prefix OFF

**Recommended**: Create VarSet parameters with **prefix OFF** for the cleanest workflow.

### Why Prefix OFF?

```
✅ Consistent Naming: param.name === param.label everywhere
✅ Clean Expressions: PQs.L instead of PQs.Base_L
✅ Professional UX: Matches CalcsLive symbol naming
✅ Robust: Works correctly with underscores (outer_dia, material_density)
```

### VarSet Parameter Creation

**When adding properties to VarSet "PQs"**:
```
Type: App::PropertyLength (or appropriate)
Group: Base
Name: L (or outer_dia, MaterialDensity, etc.)
☐ Prefix group name ← UNCHECK THIS BOX
```

**Result**:
- Internal name: `L` (no prefix)
- Dashboard shows: `L`
- Expression: `PQs.L` or `<<PQs>>.L` (clean!)

**FreeCAD Expression Usage**:
```python
# In your model features, reference VarSet parameters:
Box.Length = PQs.L
Cylinder.Radius = PQs.outer_dia / 2
Pad.Length = PQs.MaterialDensity * PQs.Volume
```

### Backward Compatibility

The Bridge **still works** with prefix ON parameters (legacy models):
- `Base_L` → Dashboard shows `L` (label)
- Expression: `PQs.Base_L` (with prefix)

But **new parameters should use prefix OFF** for best experience.

---

## Architecture Details

### Component Roles

**CalcsLive-FreeCAD Bridge** (This Repository):
- FreeCAD addon (installed in Mod folder)
- HTTP server on localhost:8787
- Exposes VarSet data via REST API
- Manages bidirectional data sync

**CalcsLive Plug Dashboard** (Web Interface):
- Browser-based at calcs.live/freecad/dashboard
- Maps VarSet parameters to CalcsLive calculations
- Provides drag-and-drop mapping interface
- Handles unit conversion and synchronization

### Data Flow

```
1. Export: FreeCAD VarSet → Bridge API → Dashboard → CalcsLive Calculations
2. Calculate: CalcsLive performs unit-aware calculations
3. Sync: CalcsLive Results → Dashboard → Bridge API → FreeCAD VarSet
4. Update: FreeCAD model recomputes with new values
```

**Key Principle**: FreeCAD VarSet remains the **single source of truth** for live parameter values.

### Key Components

- **`InitGui.py`**: Auto-start initialization and workbench registration
- **`calcslive-freecad-plug-server.py`**: HTTP server with all REST endpoints
- **`package.xml`**: Addon metadata for FreeCAD addon manager

---

## Troubleshooting

### Bridge Not Starting

**Check FreeCAD Report View** for `[CalcsLivePlug]` messages:
```
[CalcsLivePlug] ✓ CalcsLive plugged in successfully!  ← Good
[CalcsLivePlug] ✗ Failed to start server: ...          ← Error
```

**Verify port availability**:
```bash
# Check if port 8787 is in use
netstat -an | findstr 8787

# If in use, restart Bridge:
# Use "Unplug CalcsLive" then "Plug In CalcsLive"
```

### Dashboard Can't Connect

**Checklist**:
- [ ] FreeCAD is running
- [ ] A document is open (active document required)
- [ ] VarSet labeled "PQs" exists in model
- [ ] Bridge status shows running: `curl http://127.0.0.1:8787/calcslive/status`
- [ ] Windows Firewall allows localhost:8787

**Test connection**:
```bash
curl http://127.0.0.1:8787/calcslive/export
# Should return JSON with VarSet parameters
```

### No VarSet "PQs" Detected

**Error**: Dashboard shows "VarSet 'PQs' Not Found"

**Solution**:
1. Create VarSet object in FreeCAD
2. Set Label to "PQs" (case-sensitive!)
3. Add at least one parameter with prefix OFF
4. Refresh dashboard (click "Reload 3D Model Data")

---

## Requirements

- **FreeCAD 1.0+**: Tested with FreeCAD 1.0.2
- **Python 3.8+**: Standard FreeCAD Python environment
- **Network Access**: HTTP server uses localhost:8787
- **VarSet Objects**: FreeCAD models with VarSet labeled "PQs"

---

## Related Documentation

### CalcsLive Plug for FreeCAD (Main Product)
- 📚 **[Integration Guide](https://www.calcs.live/help/freecad-integration)** - Complete documentation
- 🌐 **[Dashboard](https://www.calcs.live/freecad/dashboard)** - Web interface
- 🎓 **Tutorials** - Step-by-step guides
- 🔧 **Troubleshooting** - Common issues and solutions

### CalcsLive Platform
- 🧮 **[CalcsLive](https://www.calcs.live)** - Main calculation platform
- 📖 **[Documentation](https://www.calcs.live/help)** - Platform guides
- 🔌 **CalcsLive Plug Series** - Google Sheets, n8n, FreeCAD

---

## Recent Changes

### v0.2 (2025-11-05)

**Enhanced Parameter Detection**:
- ✅ Smart group-aware prefix detection using `getGroupOfProperty()`
- ✅ Handles parameter names with underscores correctly (`outer_dia`, `material_density`)
- ✅ Supports both prefix ON (legacy) and prefix OFF (recommended) workflows
- ✅ Backward compatible with existing models

**Command Simplification**:
- ✅ Disabled unreliable commands (InitializePQs, RenameVarSetParam)
- ✅ Toolbar reduced to 3 core commands (Plug In, Unplug, Status)
- ✅ Manual VarSet creation provides better control

**Bug Fixes**:
- 🐛 Fixed parameter names with underscores being incorrectly split
- 🐛 Example: `outer_dia` now correctly returns `outer_dia`, not `dia`

---

## Contributing

Contributions welcome! Please:
1. Test with FreeCAD 1.0.2+
2. Ensure backward compatibility
3. Update documentation
4. Include test cases

---

## License

See [License](./LICENSE)

---

## Support

**Need help?**
1. Check FreeCAD Report View for `[CalcsLivePlug]` messages
2. Test endpoint: `http://127.0.0.1:8787/calcslive/status`
3. Read the [Integration Guide](https://www.calcs.live/help/freecad-integration)
4. Open issues on [GitHub](https://github.com/CalcsLive/calcslive-plug-4-freecad/issues)

---

**Status**: ✅ **Production Ready**
**Version**: 1.0.1  
**Role**: Server component of CalcsLive Plug for FreeCAD  
**Dashboard**: [calcs.live/freecad/dashboard](https://www.calcs.live/freecad/dashboard)
