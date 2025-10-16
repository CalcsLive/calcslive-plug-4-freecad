# CalcsLive FreeCAD Workbench

Official FreeCAD workbench for bi-directional integration with CalcsLive unit-aware calculations.

## Overview

This workbench enables seamless parameter synchronization between FreeCAD parametric models and CalcsLive calculations. Users can extract dimensional parameters from their 3D models and connect them to live engineering calculations with automatic unit conversion.

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