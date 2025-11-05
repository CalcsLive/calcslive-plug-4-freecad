# -*- coding: utf-8 -*-
"""
CalcsLive FreeCAD Plug Server
HTTP server that provides a plug interface for CalcsLive calculation capability in FreeCAD
Exposes VarSet data through REST API for web-based CalcsLive integration
"""

from __future__ import annotations
import json
import threading
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    from FreeCAD import Units
except Exception as e:
    raise RuntimeError("This module must be run inside FreeCAD.") from e

HOST = "127.0.0.1"
PORT = 8787

# Global server thread reference
_server_thread = None
_httpd = None

# -----------------------------
# VarSet Helper Functions (CalcsLive Plug Interface)
# -----------------------------

def get_varset_object(doc=None):
    """Get the VarSet object from the document (CalcsLive interface)."""
    doc = doc or App.ActiveDocument
    if doc is None:
        raise RuntimeError("No active document. Create/open a document first.")

    target_label = "PQs"
    varset = None
    for obj in doc.Objects:
        if obj.TypeId == 'App::VarSet' and obj.Label == target_label:
            varset = obj
            break

    if varset is None:
        varsets_found = []
        for obj in doc.Objects:
            if obj.TypeId == 'App::VarSet':
                varsets_found.append(f"Name='{obj.Name}', Label='{obj.Label}'")

        error_msg = f"No VarSet found with Label='{target_label}'"
        if varsets_found:
            error_msg += f". Found VarSets: {', '.join(varsets_found)}"
        raise RuntimeError(error_msg)

    return varset

def export_payload(doc=None):
    """Export VarSet parameters using complete original macro pattern."""
    doc = doc or App.ActiveDocument

    try:
        varset = get_varset_object(doc)
    except RuntimeError as e:
        return {
            "docName": doc.Label if doc else None,
            "filePath": getattr(doc, "FileName", None),
            "params": [],
            "error": str(e)
        }

    # Extract file name without path for dashboard display
    file_name = None
    file_path = getattr(doc, "FileName", None)
    if file_path:
        # Extract filename from full path (cross-platform)
        file_name = file_path.replace('\\', '/').split('/')[-1]

    result = {
        "docVersion": "0.2",
        "metadata": {
            "docName": doc.Label if doc else None,  # Document label, no ext.
            "fileName": file_name or "Untitled",    # File name with ext. without path
            "filePath": file_path                   # Full path if needed
        },
        "params": []
    }

    # Properties to skip (from working varset_data_extractor.py)
    skip_props = {
        'Label', 'Label2', 'Name', 'Visibility', 'Content', 'ExpressionEngine',
        'Document', 'Module', 'TypeId', 'ID', 'State', 'ViewObject', 'FullName',
        'InList', 'OutList', 'Parents', 'MemSize', 'MustExecute', 'Removing',
        'NoTouch', 'OldLabel', 'ExportVars'
    }

    # Build expression map once
    expr_map = dict(varset.ExpressionEngine)

    # Get all VarSet properties (using working pattern)
    for prop_name in getattr(varset, "PropertiesList", []):
        if prop_name in skip_props:
            continue

        try:
            # Get the property value (working pattern)
            prop_str = getattr(varset, prop_name)

            # Get expression if any
            expr = expr_map.get(prop_name, "")

            # Determine readonly: if it has an expression, it's likely read-only
            readonly = bool(expr)

            # Get property label (enhanced from varset_data_extractor.py)
            prop_label = prop_name.split("_", 1)[-1]  # Splits on first underscore

            # Extract SI value and display units (working pattern)
            if hasattr(prop_str, 'Value'):  # Quantity
                value_si = prop_str.Value  # Base SI value

                # Extract SI unit (enhanced from varset_data_extractor.py)
                unit_si = str(prop_str.Unit).split()[1] if hasattr(prop_str, 'Unit') and str(prop_str.Unit).count(' ') >= 1 else "?"

                # Get display value using FreeCAD's schema (working pattern)
                try:
                    result_tuple = App.Units.schemaTranslate(prop_str, App.Units.getSchema())
                    display_str = result_tuple[0].strip()  # e.g., "10.00 in"

                    parts = display_str.split()
                    if len(parts) >= 2:
                        # Last token is unit, rest is number
                        unit_part = parts[-1]
                        number_part = " ".join(parts[:-1])
                        display_value = float(number_part)
                        display_unit = unit_part
                    elif len(parts) == 1:
                        # No unit
                        display_value = float(display_str)
                        display_unit = "?"
                    else:
                        raise ValueError("No parts in formatted string")

                except Exception as e:
                    # Fallback to raw unit symbol if possible
                    display_value = value_si
                    if hasattr(prop_str, 'Unit'):
                        try:
                            display_unit = str(prop_str.Unit).split()[0]
                        except:
                            display_unit = "?"
                    else:
                        display_unit = "?"

                # Get FreeCAD property type (e.g., "App::PropertyLength")
                try:
                    prop_type = varset.getTypeIdOfProperty(prop_name)
                except Exception as e:
                    prop_type = None

                # Extract kind from property type (App::PropertyLength → Length)
                kind = None
                if prop_type and "::" in prop_type and "Property" in prop_type:
                    kind = prop_type.split("Property")[1]

                # Enhanced data structure matching varset_data_extractor.py
                # Note: "label" is the clean parameter name (e.g., "L", "W", "H") used for dashboard and mappings
                #       "name" is the full FreeCAD property name (e.g., "Base_L", "Base_W") used internally
                result["params"].append({
                    "path": f"{varset.Name}:{varset.Label}/{prop_name}",  # Enhanced path format (internal name)
                    "label": prop_label,                                 # Clean label (e.g., "L", "W", "H") - USE FOR MAPPINGS
                    "name": prop_name,                                   # Full property name (e.g., "Base_L") - FreeCAD internal
                    "expr": expr,                                        # Expression if calculated
                    "readonly": readonly,                                # Based on expression
                    "value_si": value_si,                               # SI base value
                    "unit_si": unit_si,                                 # SI unit
                    "kind": kind,                                       # FreeCAD category kind
                    "display": {                                        # Display object
                        "value": display_value,                         # User's display value
                        "unit": display_unit                            # User's display unit
                    }
                })

            elif isinstance(prop_str, str):
                # String properties (ArticleId, etc.) - enhanced format
                result["params"].append({
                    "path": f"{varset.Name}:{varset.Label}/{prop_name}",
                    "label": prop_name.split("_", 1)[-1],  # Clean label
                    "name": prop_name,
                    "value": prop_str,
                    "type": "string"
                })
            else:
                # Plain numbers - enhanced format matching varset_data_extractor.py
                result["params"].append({
                    "path": f"{varset.Name}:{varset.Label}/{prop_name}",  # Enhanced path format (internal name)
                    "label": prop_label,                                 # Clean label (e.g., "L", "W", "H") - USE FOR MAPPINGS
                    "name": prop_name,                                   # Full property name (e.g., "Base_L") - FreeCAD internal
                    "expr": expr,                                        # Expression if calculated
                    "readonly": readonly,                                # Based on expression
                    "value_si": float(prop_str),                        # SI base value
                    "unit_si": "?",                                     # No unit for plain numbers
                    "display": {                                        # Display object
                        "value": float(prop_str),                       # Same as SI for plain numbers
                        "unit": "?"                                     # No unit
                    }
                })

        except Exception as e:
            # Error handling - enhanced format matching varset_data_extractor.py
            result["params"].append({
                "path": f"{varset.Name}:{varset.Label}/{prop_name}",
                "label": prop_name.split("_", 1)[-1],
                "name": prop_name,
                "error": str(e)
            })

    return result

def get_pq_mappings(doc=None):
    """Get PQ mapping data stored in VarSet properties."""
    varset = get_varset_object(doc)

    # Get mapping data from VarSet property (JSON string)
    mapping_json = getattr(varset, 'CalcsLiveMappings', None)

    if mapping_json:
        try:
            mapping_data = json.loads(mapping_json)
            return mapping_data
        except (json.JSONDecodeError, TypeError):
            print("[CalcsLivePlug] Warning: Invalid mapping JSON in VarSet, returning default structure")

    # Return default structure (simplified - no articles array)
    return {
        "docVersion": "0.2",
        "unitsSchema": "UserPreferred",
        "articleId": None,
        "articleTitle": None,
        "lastUpdated": None,
        "pqMappings": {}
    }

def set_pq_mappings(mapping_data, doc=None):
    """Store PQ mapping data in VarSet properties."""
    varset = get_varset_object(doc)

    # Convert mapping data to JSON and store in VarSet property
    mapping_json = json.dumps(mapping_data, indent=2)

    # Create or update the CalcsLiveMappings property
    if not hasattr(varset, 'CalcsLiveMappings'):
        # Add new string property for mapping storage
        varset.addProperty("App::PropertyString", "CalcsLiveMappings", "CalcsLive", "PQ mapping relations (JSON)")

    varset.CalcsLiveMappings = mapping_json

    # Force document recompute to ensure property is saved
    if doc:
        doc.recompute()

    print(f"[CalcsLivePlug] Saved PQ mappings to VarSet: {len(mapping_data.get('articles', []))} articles")
    return {"success": True, "articlesCount": len(mapping_data.get('articles', []))}

# -----------------------------
# Quantity Helpers (from original macro)
# -----------------------------

def _kind_to_units_kind(kind: str):
    # Map PQ kind string to Units.* enum-like objects (FreeCAD 1.0 compatible)
    table = {
        "Length": Units.Length,
        "Angle": Units.Angle,
        "Area": Units.Area,
        "Volume": Units.Volume,
        "Mass": Units.Mass,
        "Velocity": Units.Velocity,
        "Acceleration": Units.Acceleration,
        "Pressure": Units.Pressure,
        "Force": Units.Force,
        "Power": Units.Power,
        "Density": getattr(Units, 'Density', Units.Length)  # Fallback if not available
    }
    return table.get(kind, Units.Length)

def to_quantity(value, kind="Length"):
    """Wrap value (float or Quantity or string '10 mm') into Units.Quantity of given kind."""
    if hasattr(value, "Value") and hasattr(value, "getUnit"):
        return value  # already a Quantity
    if isinstance(value, (float, int)):
        return Units.Quantity(float(value), _kind_to_units_kind(kind))
    # string like "10 mm"
    return Units.Quantity(str(value))

def has_expression(obj, prop):
    try:
        # API varies between versions; guard
        if hasattr(obj, "ExpressionEngine"):
            expr = obj.getExpression(prop)
            return expr is not None
        if hasattr(obj, "getExpression"):
            return obj.getExpression(prop) is not None
    except Exception:
        pass
    return False

def q_display(q):
    # FreeCAD 1.0 compatibility fix
    try:
        # Try modern API first
        unit = q.getUserPreferredUnit()
        val = q.getValueAs(unit)
        return float(val), unit
    except (AttributeError, TypeError):
        try:
            # FreeCAD 1.0 fallback - parse string representation
            qstr = str(q)
            # Example: "90.0 in" -> val=90.0, unit="in"
            if " " in qstr:
                parts = qstr.rsplit(" ", 1)  # Split from right to handle negative numbers
                val = float(parts[0])
                unit = parts[1] if len(parts) > 1 else ""
                return val, unit
            else:
                # Just a number, try to get unit separately
                try:
                    unit = str(q.getUnit()) if hasattr(q, 'getUnit') else ""
                except:
                    unit = ""
                return float(q.Value), unit
        except Exception as e:
            # Ultimate fallback - just the value with no unit
            return float(q.Value), ""

def write_path(doc, path, value, unit=None, kind="Length", allow_override_expression=False):
    # Handle enhanced path format: "VarSet:PQs/Base_H" -> obj_name="VarSet", prop="Base_H"
    if ":" in path:
        obj_name_part, prop = path.split("/", 1)
        obj_name = obj_name_part.split(":")[0]  # Extract "VarSet" from "VarSet:PQs"
    else:
        # Fallback to simple format: "VarSet/Base_H"
        obj_name, prop = path.split("/", 1)

    obj = doc.getObject(obj_name)
    if obj is None:
        raise ValueError(f"Object not found: {obj_name}")

    if has_expression(obj, prop) and not allow_override_expression:
        raise RuntimeError(f"{path} is expression-driven; refusing to overwrite.")

    q = Units.Quantity(f"{value} {unit}") if unit else to_quantity(value, kind)

    if obj.TypeId == "Spreadsheet::Sheet":
        # Store in user's display units to keep sheet readable
        disp_val, disp_unit = q_display(q)
        obj.set(prop, str(disp_val))
    else:
        # Try to set Quantity; fallback to SI float
        try:
            setattr(obj, prop, q)  # Direct attribute assignment for FreeCAD objects
        except Exception:
            setattr(obj, prop, float(q.Value))

def apply_updates(updates: list, doc=None, allow_override_expression=False):
    doc = doc or App.ActiveDocument
    applied = []
    errors = []
    for upd in updates:
        path = upd.get("name") or upd.get("path")
        value = upd.get("value")
        unit = upd.get("unit")
        kind = upd.get("pqKind", "Length")
        try:
            write_path(doc, path, value, unit, kind, allow_override_expression=allow_override_expression)
            applied.append({"name": path, "value": value, "unit": unit})
        except Exception as e:
            errors.append({"name": path, "error": str(e)})
    if doc:
        try:
            doc.recompute()
        except Exception:
            pass
    return {"applied": applied, "errors": errors}

# -----------------------------
# Clean Units Data Extraction (from original macro)
# -----------------------------

def get_clean_units_data():
    """
    Generate clean units data for CalcsLive integration.
    Self-contained analysis without relying on external macros.

    Returns structured data with:
    - clean_units_list: All displayable units for conversion validation
    - unit_si_to_kind: Base units to categories mapping for pqKind detection
    """
    from datetime import datetime

    try:
        # Embedded property analysis - simplified version
        clean_data = analyze_clean_property_types()

        return {
            "timestamp": datetime.now().isoformat(),
            "freecad_version": App.Version(),
            "total_clean_types": len(clean_data["unit_si_to_kind"]),
            "clean_units_list": clean_data["clean_units_list"],
            "unit_si_to_kind": clean_data["unit_si_to_kind"],
            "generation_method": "embedded_analysis",
            "source": "CalcsLivePlug_live"
        }

    except Exception as e:
        print(f"[CalcsLivePlug] Clean units extraction failed: {e}")
        # Return static fallback data
        return get_static_clean_units_fallback()

def analyze_clean_property_types():
    """
    Embedded analysis of FreeCAD clean property types.
    Based on ExtractQuantityTypes.FCMacro but simplified for API use.
    """

    # Known clean property types from analysis (static for reliability)
    clean_property_data = {
        "App::PropertyLength": {"category": "Length", "base_unit": "mm", "example_units": ["mm", "cm", "m", "in", "ft"]},
        "App::PropertyDistance": {"category": "Length", "base_unit": "mm", "example_units": ["mm", "cm", "m", "in", "ft"]},
        "App::PropertyArea": {"category": "Area", "base_unit": "mm²", "example_units": ["mm²", "cm²", "m²", "in²", "ft²"]},
        "App::PropertyVolume": {"category": "Volume", "base_unit": "mm³", "example_units": ["mm³", "cm³", "m³", "in³", "ft³", "l"]},
        "App::PropertyMass": {"category": "Mass", "base_unit": "kg", "example_units": ["g", "kg", "lb", "oz"]},
        
        "App::PropertyAngle": {"category": "Angle", "base_unit": "rad", "example_units": ["rad", "deg", "°"]},
        "App::PropertySpeed": {"category": "Velocity", "base_unit": "mm/s", "example_units": ["mm/s", "m/s", "km/h", "mph", "ft/s"]},
        "App::PropertyAcceleration": {"category": "Acceleration", "base_unit": "mm/s²", "example_units": ["mm/s²", "m/s²", "ft/s²"]},
        "App::PropertyForce": {"category": "Force", "base_unit": "N", "example_units": ["N", "kN", "lbf", "kgf"]},
        "App::PropertyPressure": {"category": "Pressure", "base_unit": "Pa", "example_units": ["Pa", "kPa", "MPa", "bar", "psi"]},
        
        "App::PropertyDensity": {"category": "Density", "base_unit": "kg/mm³", "example_units": ["kg/m³", "g/cm³", "kg/mm³", "lb/ft³"]},
        "App::PropertyTemperature": {"category": "Temperature", "base_unit": "K", "example_units": ["K", "°C", "°F"]},
        "App::PropertyTime": {"category": "Time", "base_unit": "s", "example_units": ["s"]},
        "App::PropertyFrequency": {"category": "Frequency", "base_unit": "Hz", "example_units": ["Hz"]},
        "App::PropertyPower": {"category": "Power", "base_unit": "W", "example_units": ["W"]}
    }

    # Build unit_si_to_kind mapping
    unit_si_to_kind = {}
    clean_units_set = set()

    for property_type, data in clean_property_data.items():
        category = data["category"]
        base_unit = data["base_unit"]
        example_units = data.get("example_units", [])

        # Add base unit to mapping
        if base_unit:
            unit_si_to_kind[base_unit] = category

        # Add all example units to clean units list
        clean_units_set.update(example_units)

    return {
        "unit_si_to_kind": unit_si_to_kind,
        "clean_units_list": sorted(list(clean_units_set))
    }

def get_static_clean_units_fallback():
    """
    Static fallback data when dynamic analysis fails.
    """
    from datetime import datetime

    return {
        "timestamp": datetime.now().isoformat(),
        "freecad_version": App.Version(),
        "total_clean_types": 15,
        "clean_units_list": [
            "deg", "ft", "g", "Hz", "in", "K", "kg", "kg/m³", "kg/mm³", "kN", "l",
            "lb", "lbf", "m", "mm", "mm/s", "mm/s²", "mm²", "mm³", "N", "Pa", "rad",
            "s", "W", "°", "°C", "°F"
        ],
        "unit_si_to_kind": {
            "mm": "Length", "mm²": "Area", "mm³": "Volume", "kg": "Mass",
            "rad": "Angle", "mm/s": "Velocity", "mm/s²": "Acceleration",
            "N": "Force", "Pa": "Pressure", "kg/mm³": "Density",
            "K": "Temperature", "s": "Time", "Hz": "Frequency", "W": "Power"
        },
        "generation_method": "static_fallback",
        "source": "hardcoded_backup"
    }

# -----------------------------
# HTTP Server Implementation (CalcsLive Plug Endpoints)
# -----------------------------

class CalcsLivePlugHandler(BaseHTTPRequestHandler):
    server_version = "CalcsLivePlug/1.0"

    def _send_json(self, code, payload):
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/calcslive/export":
            try:
                payload = export_payload(App.ActiveDocument)
                self._send_json(200, payload)
                print(f"[CalcsLivePlug] Served export request - {len(payload.get('params', []))} parameters")
            except Exception as e:
                print(f"[CalcsLivePlug] Export error: {e}")
                self._send_json(500, {"error": str(e)})

        elif self.path == "/calcslive/mapping":
            try:
                mapping_data = get_pq_mappings(App.ActiveDocument)
                self._send_json(200, mapping_data)
                print(f"[CalcsLivePlug] Served mapping request")
            except Exception as e:
                print(f"[CalcsLivePlug] Mapping error: {e}")
                self._send_json(500, {"error": str(e)})

        elif self.path == "/calcslive/clean-units":
            try:
                clean_units_data = get_clean_units_data()
                self._send_json(200, clean_units_data)
                print(f"[CalcsLivePlug] Served clean-units request")
            except Exception as e:
                print(f"[CalcsLivePlug] Clean-units error: {e}")
                self._send_json(500, {"error": str(e)})

        elif self.path == "/calcslive/status":
            # CalcsLive plug status endpoint
            try:
                doc = App.ActiveDocument
                self._send_json(200, {
                    "status": "plugged-in",
                    "plugin": "CalcsLivePlug",
                    "interface": "FreeCAD-CalcsLive",
                    "active_document": doc.Label if doc else None,
                    "server": f"http://{HOST}:{PORT}",
                    "endpoints": ["/calcslive/export", "/calcslive/import", "/calcslive/mapping", "/calcslive/clean-units", "/calcslive/status"]
                })
            except Exception as e:
                self._send_json(200, {
                    "status": "plugged-in",
                    "plugin": "CalcsLivePlug",
                    "error": str(e),
                    "server": f"http://{HOST}:{PORT}"
                })

        else:
            self._send_json(404, {
                "error": "Endpoint not found",
                "available_endpoints": ["/calcslive/export", "/calcslive/import", "/calcslive/mapping", "/calcslive/clean-units", "/calcslive/status"],
                "plugin": "CalcsLivePlug"
            })

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except Exception:
            data = {}

        if self.path == "/calcslive/import":
            try:
                updates = data.get("updates", [])
                allow = bool(data.get("allowOverrideExpression", False))
                res = apply_updates(updates, App.ActiveDocument, allow_override_expression=allow)
                self._send_json(200, res)
                print(f"[CalcsLivePlug] Processed import request - {len(res.get('applied', []))} applied, {len(res.get('errors', []))} errors")
            except Exception as e:
                print(f"[CalcsLivePlug] Import error: {e}")
                self._send_json(500, {"error": str(e)})

        elif self.path == "/calcslive/mapping":
            try:
                # Save mapping data to VarSet
                result = set_pq_mappings(data, App.ActiveDocument)
                self._send_json(200, result)
                print(f"[CalcsLivePlug] Saved mapping data")
            except Exception as e:
                print(f"[CalcsLivePlug] Save mapping error: {e}")
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {
                "error": "Endpoint not found",
                "available_endpoints": ["/calcslive/import", "/calcslive/mapping"],
                "plugin": "CalcsLivePlug"
            })

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # Override to use FreeCAD console instead of stderr
        print(f"[CalcsLivePlug HTTP] {format % args}")

def _run_server():
    """Run the CalcsLive plug HTTP server in a separate thread"""
    global _httpd
    try:
        _httpd = ThreadingHTTPServer((HOST, PORT), CalcsLivePlugHandler)
        print(f"[CalcsLivePlug] Plug server started on http://{HOST}:{PORT}")
        print(f"[CalcsLivePlug] CalcsLive plug endpoints available:")
        print(f"  GET  http://{HOST}:{PORT}/calcslive/export      (export VarSet data)")
        print(f"  POST http://{HOST}:{PORT}/calcslive/import      (update VarSet values)")
        print(f"  GET  http://{HOST}:{PORT}/calcslive/mapping     (get PQ mappings)")
        print(f"  POST http://{HOST}:{PORT}/calcslive/mapping     (save PQ mappings)")
        print(f"  GET  http://{HOST}:{PORT}/calcslive/clean-units (get clean units data)")
        print(f"  GET  http://{HOST}:{PORT}/calcslive/status      (plug status)")
        _httpd.serve_forever()
    except Exception as e:
        print(f"[CalcsLivePlug] Plug server error: {e}")

def plug_in():
    """Plug in CalcsLive capability (start HTTP server)"""
    global _server_thread

    if _server_thread and _server_thread.is_alive():
        print(f"[CalcsLivePlug] CalcsLive already plugged in at http://{HOST}:{PORT}")
        return True

    try:
        _server_thread = threading.Thread(target=_run_server, daemon=True)
        _server_thread.start()
        print(f"[CalcsLivePlug] Plugging in CalcsLive capability...")
        return True
    except Exception as e:
        print(f"[CalcsLivePlug] Failed to plug in CalcsLive: {e}")
        return False

def unplug():
    """Unplug CalcsLive capability (stop HTTP server)"""
    global _httpd, _server_thread

    try:
        if _httpd:
            print("[CalcsLivePlug] Unplugging CalcsLive capability...")

            # Proper shutdown sequence for ThreadingHTTPServer
            try:
                # 1. Stop accepting new connections
                _httpd.shutdown()

                # 2. Close the server socket to free the port
                _httpd.server_close()

                print("[CalcsLivePlug] Server socket closed")
            except Exception as e:
                print(f"[CalcsLivePlug] Warning during server shutdown: {e}")

            _httpd = None

        if _server_thread and _server_thread.is_alive():
            print("[CalcsLivePlug] Waiting for server thread to terminate...")
            _server_thread.join(timeout=3)
            _server_thread = None

        print("[CalcsLivePlug] CalcsLive unplugged - port 8787 should be free")
        return True
    except Exception as e:
        print(f"[CalcsLivePlug] Error unplugging CalcsLive: {e}")
        return False

def is_plugged_in():
    """Check if CalcsLive is currently plugged in"""
    global _server_thread, _httpd

    # Check if thread is alive and server object exists
    thread_alive = _server_thread and _server_thread.is_alive()
    server_exists = _httpd is not None

    return thread_alive and server_exists

def check_port_available(host=HOST, port=PORT):
    """Check if the port is available (not in use)"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return True  # Assume available if we can't check

def test_plug():
    """Test CalcsLive plug functionality"""
    try:
        doc = App.ActiveDocument
        if not doc:
            return {"status": "error", "message": "No active document"}

        payload = export_payload(doc)
        param_count = len(payload.get('params', []))

        plugged_in = is_plugged_in()
        port_available = check_port_available()

        return {
            "status": "ok",
            "message": f"CalcsLive plug working - found {param_count} parameters",
            "plugged_in": plugged_in,
            "port_available": port_available,
            "port_status": f"Port {PORT} is {'FREE' if port_available else 'IN USE'}",
            "plug_url": f"http://{HOST}:{PORT}" if plugged_in else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Legacy aliases for compatibility
start_server = plug_in
stop_server = unplug
is_server_running = is_plugged_in
test_bridge = test_plug