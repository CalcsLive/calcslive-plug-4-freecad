# CalcsLive Plug for FreeCAD

**Auto-starting HTTP server plug for seamless CalcsLive integration with FreeCAD parametric models.**

## Overview

CalcsLivePlug provides a **plug interface** for CalcsLive calculation capability in FreeCAD. It automatically starts an HTTP server when FreeCAD loads, enabling **real-time bi-directional synchronization** between FreeCAD parametric models and CalcsLive's **composable, unit-aware engineering calculations**.

### 🔌 Plug Architecture

The "plug" concept means CalcsLive calculation capability is **plugged into** FreeCAD through a lightweight HTTP interface:

- **Auto-start**: HTTP server starts automatically when FreeCAD loads
- **Always available**: Web dashboards can connect instantly without manual setup
- **Background operation**: Runs silently in the background until needed
- **Manual controls**: Plug In/Unplug CalcsLive capability as needed

### 🧩 Composable Engineering Calculations

Connect your FreeCAD models to **multiple specialized calculations**, all unit-aware and live-connected:

```
Complex FreeCAD Model
    ├── Structural Analysis → stress, deflection, safety factors
    ├── Thermal Analysis → heat transfer, thermal expansion
    ├── Fluid Dynamics → pressure drop, flow rates
    ├── Materials Selection → properties, costs, availability
    └── Manufacturing → tolerances, machining parameters
```

Each calculation is **independently maintained**, **reusable across projects**, and **automatically unit-converted**.

## Features

### ✅ **Auto-Start HTTP Server**
- Automatically starts when FreeCAD loads
- No manual macro execution required
- Ready for web dashboard connections

### ✅ **Complete API Compatibility**
- **100% feature parity** with original FC_CL_Bridge.FCMacro
- All original endpoints: export, import, mapping, clean-units
- Enhanced with plug status monitoring

### ✅ **Manual Controls**
- **Plug In CalcsLive** - Start HTTP server manually
- **Unplug CalcsLive** - Stop HTTP server cleanly
- **Plug Status** - Check server status and functionality

### ✅ **Proper Server Management**
- Clean shutdown with socket cleanup
- Port availability checking
- Error handling and status reporting

## Installation

1. **Copy the entire `CalcsLivePlug` folder** to your FreeCAD Mod directory:
   - **Windows**: `C:\\Users\\[username]\\AppData\\Roaming\\FreeCAD\\Mod\\`
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
   - **Linux**: `~/.local/share/FreeCAD/Mod/`

2. **Restart FreeCAD**

3. **Verify auto-start**: Check FreeCAD Report View for:
   ```
   [CalcsLivePlug] ✓ CalcsLive plugged in successfully!
   [CalcsLivePlug] HTTP endpoints are now available
   ```

4. **Test the connection**: Visit `http://127.0.0.1:8787/calcslive/status`

## Usage

### Automatic Operation (Recommended)

The plug **auto-starts when FreeCAD loads** - no user action required!

1. **Open FreeCAD** with a model containing VarSet parameters labelled PQs
2. **HTTP server is automatically available** at `http://127.0.0.1:8787`
3. **Connect your CalcsLive dashboard** to the running server
4. **Parameters sync automatically** between FreeCAD and CalcsLive

### Manual Controls

Switch to the **"CalcsLive Plug"** workbench for manual control:

| Command | Description |
|---------|-------------|
| **Plug In CalcsLive** | Start HTTP server manually |
| **Unplug CalcsLive** | Stop HTTP server cleanly |
| **Plug Status** | Check server status and functionality |

## API Endpoints

The CalcsLivePlug HTTP server provides **6 endpoints** for complete CalcsLive integration:

### **Data Exchange**
- `GET /calcslive/export` - Export VarSet parameters with full metadata
- `POST /calcslive/import` - Update VarSet parameters from CalcsLive

### **Mapping Management**
- `GET /calcslive/mapping` - Get parameter mapping configuration
- `POST /calcslive/mapping` - Save parameter mapping configuration

### **System Information**
- `GET /calcslive/clean-units` - Get clean units data for validation
- `GET /calcslive/status` - Check plug status and available endpoints

### **Example Usage**

```bash
# Check if plug is running
curl http://127.0.0.1:8787/calcslive/status

# Export current model parameters
curl http://127.0.0.1:8787/calcslive/export

# Get available units for validation
curl http://127.0.0.1:8787/calcslive/clean-units
```

## Architecture

### **Plug Design Philosophy**
- **Minimal footprint**: Lightweight HTTP server with essential functionality
- **Auto-start capability**: No manual intervention required
- **Proper lifecycle**: Clean startup, shutdown, and error handling
- **Status monitoring**: Always know if the plug is working

### **Key Components**

- **`InitGui.py`**: Auto-start initialization and workbench registration
- **`calcslive-freecad-plug-server.py`**: Complete HTTP server with all endpoints
- **`package.xml`**: Addon metadata for FreeCAD addon manager
- **`__init__.py`**: Basic addon initialization

### **Differences from Original Workbench**

| Aspect | Original Workbench | New CalcsLivePlug |
|--------|-------------------|-------------------|
| **Startup** | Manual macro execution | Automatic server start |
| **UI** | Full workbench with commands | Minimal plug controls |
| **Focus** | User interface and workflows | Background HTTP API |
| **Scope** | Complete FreeCAD integration | Focused server functionality |

## Comprehensive Workbench Integration Examples

### 🛩️ Aircraft Wing Design (Part Design + FEA + CAM)
```
FreeCAD Wing Model (wing-section.FCStd) + CalcsLivePlug
    ├── Aerodynamics Calc → lift, drag, pressure distribution
    ├── Structural FEA → stress analysis, deflection, safety factors
    ├── Weight & Balance → mass properties, CG location
    └── Manufacturing CAM → tooling requirements, machining strategies
```

### 🏗️ Building Design (Arch + Draft + Structure)
```
FreeCAD Building Model (office-building.FCStd) + CalcsLivePlug
    ├── Energy Analysis → thermal loads, HVAC sizing
    ├── Structural Design → beam sizing, foundation loads
    ├── Building Physics → daylighting, acoustics, fire safety
    └── Construction Sequencing → scheduling, material takeoffs
```

### ⚙️ Mechanical Assembly (Assembly + Motion + FEA)
```
FreeCAD Robot Assembly (6-axis-robot.FCStd) + CalcsLivePlug
    ├── Kinematic Analysis → workspace, singularities
    ├── Dynamic Simulation → torque requirements, acceleration limits
    ├── Structural FEA → deflection under load, resonance analysis
    └── Servo Sizing → motor selection, gear ratios, power consumption
```

## Benefits of the Plug Architecture

### 🚀 **Always Ready**
- HTTP server starts with FreeCAD automatically
- Web dashboards can connect instantly
- No workflow interruption for manual setup

### 🔧 **Lightweight Integration**
- Minimal impact on FreeCAD startup time
- Background operation until needed
- Clean resource management

### 🌐 **Web-First Design**
- Optimized for modern web dashboard integration
- RESTful API following web standards
- CORS support for browser applications

### 🔄 **Reliable Operation**
- Proper server lifecycle management
- Error handling and status reporting
- Clean shutdown with port cleanup

## Revolutionary Impact on FreeCAD Ecosystem

### Transforming Every Workbench
CalcsLivePlug **amplifies every FreeCAD workbench** with unit-aware calculation capability:

| FreeCAD Workbench | CalcsLive Enhancement | Impact |
|-------------------|----------------------|---------|
| **Part Design** | Live stress/thermal analysis | Design optimization during modeling |
| **Assembly** | Motion dynamics, interference | Real-time kinematic validation |
| **Arch** | Building physics, energy | Integrated architectural engineering |
| **CAM** | Cutting forces, tool life | Optimized manufacturing strategies |
| **Ship** | Naval architecture calcs | Professional vessel design |
| **FEA** | Parametric studies | Mesh-independent optimization |

### Cross-Workbench Workflows
**Unprecedented integration** between traditionally separate domains:
- **CAD → CAE → CAM**: Design → Analysis → Manufacturing in one environment
- **Architecture → Structure → MEP**: Building design with integrated systems
- **Naval → Structural → Manufacturing**: Ship design through production
- **Robotics → Controls → Manufacturing**: Mechatronic system development

## Troubleshooting

### Common Issues

**Server not starting:**
```bash
# Check FreeCAD Report View for error messages
# Look for [CalcsLivePlug] messages

# Verify port is available
curl http://127.0.0.1:8787/calcslive/status
```

**Port already in use:**
```bash
# Check what's using port 8787
netstat -an | findstr 8787

# Use "Unplug CalcsLive" then "Plug In CalcsLive" to restart
```

**Can't connect from browser:**
- Verify FreeCAD is running with a document open
- Check Windows Firewall settings for port 8787
- Try `http://localhost:8787/calcslive/status` instead

## Development

### Server Customization
The server implementation in `calcslive-freecad-plug-server.py` can be customized:

```python
# Change default port
PORT = 8788  # Change from 8787

# Add custom endpoints
def do_GET(self):
    elif self.path == "/custom/endpoint":
        # Your custom functionality
        pass
```

### Testing API Endpoints
```bash
# Test all endpoints
curl http://127.0.0.1:8787/calcslive/status
curl http://127.0.0.1:8787/calcslive/export
curl http://127.0.0.1:8787/calcslive/mapping
curl http://127.0.0.1:8787/calcslive/clean-units

# Test POST endpoints
curl -X POST http://127.0.0.1:8787/calcslive/import \
  -H "Content-Type: application/json" \
  -d '{"updates": []}'
```

## Requirements

- **FreeCAD 1.0+**: Tested with FreeCAD 1.0.2
- **Python 3.8+**: Standard FreeCAD Python environment
- **Network Access**: HTTP server uses localhost:8787
- **VarSet Objects**: FreeCAD models with VarSet parameters with label PQs.

## Related Projects

- **Original CalcsLive Workbench**: Full-featured FreeCAD workbench with UI
- **CalcsLive Platform**: Main calculation platform and web interface
- **FC_CL_Bridge.FCMacro**: Original macro implementation (legacy)

## Migration from Original Workbench

If you're upgrading from the original CalcsLiveWorkbench:

1. **API Compatibility**: All endpoints work identically
2. **Auto-start**: No more manual macro execution needed
3. **Enhanced Status**: Better monitoring and error reporting
4. **Clean Shutdown**: Proper server lifecycle management

## License

This addon is part of the CalcsLive ecosystem and follows the same licensing terms as the main CalcsLive project.

## Support

For issues and support:
1. Check FreeCAD Report View for `[CalcsLivePlug]` messages
2. Test endpoint availability: `http://127.0.0.1:8787/calcslive/status`
3. Open issues on the CalcsLive repository
4. Join the CalcsLive community discussions

---

**Status**: ✅ **Production Ready** - Auto-start HTTP server with complete API compatibility, ready for web dashboard integration.