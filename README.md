# CalcsLive FreeCAD Workbench

Official FreeCAD workbench for bi-directional integration with CalcsLive unit-aware calculations.

## Overview

This workbench enables seamless parameter synchronization between FreeCAD parametric models and CalcsLive calculations. Users can extract dimensional parameters from their 3D models and connect them to **composable, unit-aware engineering calculations** with automatic unit conversion.

### 🧩 Composable Engineering Calculations

The true power of CalcsLive integration lies in **composable calculations** - a single complex FreeCAD model can be served by multiple specialized calculations, all unit-aware and live-connected:

```
Complex FreeCAD Model
    ├── Structural Analysis → stress, deflection, safety factors
    ├── Thermal Analysis → heat transfer, thermal expansion
    ├── Fluid Dynamics → pressure drop, flow rates
    ├── Materials Selection → properties, costs, availability
    └── Manufacturing → tolerances, machining parameters
```

Each calculation is **independently maintained**, **reusable across projects**, and **automatically unit-converted** - enabling true collaborative engineering workflows.

### 🚀 Massive Impact Potential

**FreeCAD's comprehensive workbench ecosystem** (CAD, CAE, CAM, FEA, Arch, Ship, etc.) combined with CalcsLive's composable calculations creates **unprecedented engineering integration**:

- **Part Design + Structural Calcs** → Live stress analysis during modeling
- **Assembly + Motion Calcs** → Kinematic analysis with real-time updates
- **Arch + Building Physics** → Energy analysis integrated with architectural design
- **CAM + Machining Calcs** → Toolpath optimization with cutting force calculations
- **Ship + Naval Architecture** → Hull design with stability and hydrodynamic calculations
- **FEA + Advanced Analysis** → Mesh-independent parametric studies
- **Sketcher + Constraint Solving** → Mathematical relationships between geometric constraints

**Every FreeCAD workbench** becomes a potential **calculation-enhanced design environment**.

## Features

- **🔗 Connect to CalcsLive**: Open CalcsLive development server in browser
- **📊 Parameter Dashboard**: Web-based parameter mapping interface
- **📋 Extract Parameters**: Discover all dimensional parameters from active FreeCAD model
- **ℹ️ Status Information**: Show workbench status and available commands

## Installation

1. Copy this entire `CalcsLiveWorkbench` folder to your FreeCAD Mod directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\FreeCAD\Mod\`
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
   - **Linux**: `~/.local/share/FreeCAD/Mod/`

2. Restart FreeCAD

3. Select "CalcsLive" from the workbench dropdown

## Usage

### Quick Start
1. **Open or create a FreeCAD model** with dimensional parameters
2. **Switch to CalcsLive workbench** from dropdown menu
3. **Click "Connect to CalcsLive"** to open the web interface
4. **Click "Extract Parameters"** to discover model parameters
5. **Click "Open Dashboard"** to map parameters to calculations

### Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| Connect to CalcsLive | `Ctrl+Shift+C` | Open CalcsLive connection page |
| Open Dashboard | `Ctrl+Shift+D` | Open parameter mapping interface |
| Extract Parameters | `Ctrl+Shift+E` | Show all dimensional parameters |
| Show Status | `Ctrl+Shift+I` | Display workbench information |

## Architecture

### CalcsLive-Centric Design (80/20 Distribution)
- **80%**: Modern web interface (Nuxt 3, Vue 3, TipTap, Tailwind CSS)
- **20%**: Minimal FreeCAD UI (toolbar commands + basic dialogs)

This approach leverages CalcsLive's sophisticated web infrastructure while keeping FreeCAD integration lightweight and maintainable.

### Key Components

- **`InitGui.py`**: Workbench registration following official FreeCAD pattern
- **`CalcsLiveTools.py`**: Command definitions with proven working patterns
- **`calcsliveutils/`**: Utility modules for toolbar and menu initialization
- **`core/`**: Core functionality modules for parameter extraction and sync
- **`commands/`**: Individual command implementations
- **`ui/`**: User interface components and dialogs

## Comprehensive Workbench Integration Examples

### 🛩️ Aircraft Wing Design (Part Design + FEA + CAM)
```
FreeCAD Wing Model (wing-section.FCStd)
    ├── Aerodynamics Calc (Part Design) → lift, drag, pressure distribution
    ├── Structural FEA (FEA Workbench) → stress analysis, deflection, safety factors
    ├── Weight & Balance (Assembly) → mass properties, CG location
    └── Manufacturing CAM → tooling requirements, machining strategies
```

### 🏗️ Building Design (Arch + Draft + Structure)
```
FreeCAD Building Model (office-building.FCStd)
    ├── Energy Analysis (Arch) → thermal loads, HVAC sizing
    ├── Structural Design (Draft/Part) → beam sizing, foundation loads
    ├── Building Physics → daylighting, acoustics, fire safety
    └── Construction Sequencing → scheduling, material takeoffs
```

### ⚙️ Mechanical Assembly (Assembly + Motion + FEA)
```
FreeCAD Robot Assembly (6-axis-robot.FCStd)
    ├── Kinematic Analysis (Assembly) → workspace, singularities
    ├── Dynamic Simulation → torque requirements, acceleration limits
    ├── Structural FEA → deflection under load, resonance analysis
    └── Servo Sizing → motor selection, gear ratios, power consumption
```

### 🚢 Ship Design (Ship + FEA + Mesh)
```
FreeCAD Vessel Design (cargo-ship.FCStd)
    ├── Hull Hydrostatics (Ship) → displacement, stability, seakeeping
    ├── Structural Analysis (FEA) → hull strength, fatigue life
    ├── Propulsion Design → engine sizing, propeller optimization
    └── Cargo Planning → loading sequences, trim optimization
```

### 🏭 Manufacturing Process (CAM + Part Design + Material)
```
FreeCAD Machined Part (turbine-blade.FCStd)
    ├── Machining Strategy (CAM) → toolpaths, cutting parameters
    ├── Tool Selection → cutting forces, surface finish, tool life
    ├── Fixture Design → clamping forces, deflection analysis
    └── Quality Control → tolerances, measurement strategies
```

## Benefits of Composable Engineering

### 🎯 **Specialization**
- Domain experts maintain their calculation areas
- Aerodynamics team owns lift/drag calculations
- Structures team owns stress/deflection calculations
- Independent development and validation

### 🔄 **Reusability**
- Structural calculations work across multiple aircraft models
- Heat exchanger calcs apply to various thermal systems
- Material properties shared across all projects
- Build calculation libraries over time

### 🤝 **Collaboration**
- Aerodynamics updates → instant structural team feedback
- Material changes → automatic cost and weight updates
- Manufacturing constraints → design optimization loops
- Real-time collaborative engineering

### 📈 **Evolution**
- Improve one calculation without breaking others
- Add new calculation types (fatigue, optimization)
- Upgrade calculation methods independently
- Maintain calculation version history

## 🌍 Revolutionary Impact on FreeCAD Ecosystem

### Transforming Every Workbench
CalcsLive integration **amplifies every FreeCAD workbench** with unit-aware intelligence:

| FreeCAD Workbench | CalcsLive Enhancement | Impact |
|-------------------|----------------------|---------|
| **Part Design** | Live stress/thermal analysis | Design optimization during modeling |
| **Assembly** | Motion dynamics, interference | Real-time kinematic validation |
| **Arch** | Building physics, energy | Integrated architectural engineering |
| **CAM** | Cutting forces, tool life | Optimized manufacturing strategies |
| **Ship** | Naval architecture calcs | Professional vessel design |
| **FEA** | Parametric studies | Mesh-independent optimization |
| **Draft** | Engineering calculations | Technical drawing validation |
| **Sketcher** | Constraint mathematics | Geometric relationship solving |

### Cross-Workbench Workflows
**Unprecedented integration** between traditionally separate domains:
- **CAD → CAE → CAM**: Design → Analysis → Manufacturing in one environment
- **Architecture → Structure → MEP**: Building design with integrated systems
- **Naval → Structural → Manufacturing**: Ship design through production
- **Robotics → Controls → Manufacturing**: Mechatronic system development

### Professional Engineering Transformation
- **Design-Analysis Loops**: Instant feedback during creative design process
- **Multi-Physics Integration**: Thermal-structural-fluid coupled analysis
- **Manufacturing-Aware Design**: DFM calculations integrated with geometry
- **Regulatory Compliance**: Built-in safety factors and engineering codes

## Development

### Architecture Pattern
Follows the exact same pattern as FreeCAD's Draft workbench:
- Uses `appendToolbar()` method for toolbar registration
- Commands defined at module scope for proper FreeCAD recognition
- Modular structure with separate utilities and core functionality

### Testing
1. Individual commands tested and proven working
2. Parameter extraction successfully discovers dimensional properties
3. Web interface integration confirmed functional
4. Bi-directional sync foundation established

## 🌟 Future Vision: Calculation Ecosystem

### Calculation Marketplace
- **Community Calculations**: Shared, verified engineering calculations
- **Domain Expertise**: Thermal, structural, fluid, electrical specialists
- **Plug-and-Play Engineering**: Compose solutions from proven calculations
- **Quality Assurance**: Peer-reviewed calculations with unit validation

### Professional Workflows
- **Design-Analysis Loops**: Geometry changes → instant analysis updates
- **Multi-Physics Integration**: Coupled thermal-structural-fluid analyses
- **Optimization Workflows**: Parameter sweeps with live geometry updates
- **Regulatory Compliance**: Calculations with built-in safety factors and codes

### Collaborative Engineering
- **Remote Team Integration**: Global teams work on same model + calculations
- **Version Control**: Track calculation evolution with model changes
- **Knowledge Preservation**: Company calculation libraries and best practices
- **Training & Education**: Learn engineering through interactive calculation examples

## Related Projects

- **Main CalcsLive**: [CalcsLive Platform](https://github.com/yourusername/calcslive) - Main calculation platform
- **Google Sheets Integration**: calcslive-plug-4-google-sheets - Predecessor integration project
- **n8n Integration**: Built-in n8n API support for workflow automation

## Requirements

- **FreeCAD 1.0+**: Tested with FreeCAD 1.0.2
- **Python 3.8+**: Standard FreeCAD Python environment
- **CalcsLive Server**: Local or remote CalcsLive instance
- **Web Browser**: For CalcsLive web interface access

## License

This workbench is part of the CalcsLive ecosystem and follows the same licensing terms as the main CalcsLive project.

## Support

For issues and support:
1. Check the CalcsLive documentation
2. Open issues on the main CalcsLive repository
3. Join the CalcsLive community discussions

---

**Status**: ✅ **Functional Milestone** - All 4 commands working, parameter extraction successful, ready for bi-directional sync development.