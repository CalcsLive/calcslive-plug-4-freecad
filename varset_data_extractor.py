# Macro: Extract VarSet Variables (Compatible with FreeCAD builds lacking getVariableNames)
import FreeCAD
import json

def extract_varset_data(varset_obj):
    var_data = []
    props = varset_obj.PropertiesList

    # Candidate variable properties: skip internal ones
    skip_props = {
        'Label', 'Label2', 'Name', 'Visibility', 'Content', 'ExpressionEngine',
        'Document', 'Module', 'TypeId', 'ID', 'State', 'ViewObject', 'FullName',
        'InList', 'OutList', 'Parents', 'MemSize', 'MustExecute', 'Removing',
        'NoTouch', 'OldLabel', 'ArticleID', 'ArticleTitle', 'ArticleURL',
        'Base__ArticleID', 'Base__ArticleTitle', 'ExportVars'
    }
    
    # Build expression map once
    expr_map = dict(varset_obj.ExpressionEngine)

    for prop_name in props:
        if prop_name in skip_props:
            continue

        try:
            # Get property type
            prop_type = varset_obj.getTypeIdOfProperty(prop_name)
            # [DEBUG@extract_varset_data] prop_name = Base_Density, prop_type = App::PropertyDensity
            FreeCAD.Console.PrintMessage(f"[DEBUG@extract_varset_data] prop_name = {prop_name}, prop_type = {prop_type}\n")
            
            # Get property label (1st column in VarSet table)
            prop_label = prop_name.split("_", 1)[-1]  # Splits on first underscore
            FreeCAD.Console.PrintMessage(f"prop_label = {prop_label}\n")  # prop_label = Density
            
            # Get property expr

            # Get the property value
            prop_str = getattr(varset_obj, prop_name)
            FreeCAD.Console.PrintMessage(f"prop_str = {prop_str}\n")  # prop_str = 762.0 mm

            # Get expression if any
            expr = ""
            # Get expression (or user input string)
            expr = expr_map.get(prop_name, "")
            """ if hasattr(varset_obj, 'getExpression'):
                expr = varset_obj.getExpression(prop_name) or "" """
            FreeCAD.Console.PrintMessage(f"expr = {expr}\n")  # expr = ??            

            # Determine readonly: if it has an expression, it's likely read-only
            readonly = bool(expr)

            # Extract SI value
            if hasattr(prop_str, 'Value'):  # Quantity
                value_si = prop_str.Value
                unit_obj_si = prop_str.Unit
                FreeCAD.Console.PrintMessage(f"unit_obj_si = {unit_obj_si}\n")  # unit_obj_si = Unit: mm (1,0,0,0,0,0,0,0) [Length]
                unit_si = str(prop_str.Unit).split()[1] if hasattr(prop_str, 'Unit') and str(prop_str.Unit).count(' ') >= 1 else "?"
                FreeCAD.Console.PrintMessage(f"unit_si = {unit_si}\n")  # unit_si = mm  
                
            else:  # Plain number
                value_si = float(prop_str)

            # Parse display value from formatted string (as shown in VarSet GUI)
            display_value = value_si
            display_unit = "?"

            try:
                if hasattr(prop_str, 'Value') and hasattr(prop_str, 'Unit'):
                    FreeCAD.Console.PrintMessage(f"pause1\n")
                    
                    result = FreeCAD.Units.schemaTranslate(prop_str, FreeCAD.Units.getSchema())
                    schema = FreeCAD.Units.getSchema()
                    FreeCAD.Console.PrintMessage(f"schema = {schema}\n")
                    display_str = result[0].strip()  # e.g., "10.00 in"
                    FreeCAD.Console.PrintMessage(f"display_str = {display_str}\n")    # 30.00 in
                    
                    parts = display_str.split()
                    if len(parts) >= 2:
                        # Assume last token is unit, rest is number
                        unit_part = parts[-1]
                        number_part = " ".join(parts[:-1])
                        display_value = float(number_part)
                        display_unit = unit_part
                    elif len(parts) == 1:
                        # No unit? (unlikely)
                        display_value = float(display_str)
                        display_unit = "?"
                    else:
                        raise ValueError("No parts in formatted string")
                    
                    # Format using current user unit schema (e.g., Imperial)
                    FreeCAD.Console.PrintMessage(f"pause2\n")                    
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Failed to parse display for {prop_name}: {e}\n")
                # Fallback to raw unit symbol if possible
                if hasattr(prop_str, 'Unit'):
                    try:
                        display_unit = str(prop_str.Unit).split()[0]
                    except:
                        display_unit = "?"
                else:
                    display_unit = "?"                 

            var_info = {
                "path": f"{varset_obj.Name}:{varset_obj.Label}/{prop_name}",
                "label": prop_label,
                "name": prop_name,
                "expr": expr,
                "readonly": readonly,
                "value_si": value_si,
                "unit_si": unit_si,
                "display": {
                    "value": display_value,
                    "unit": display_unit
                }
            }
            """    example output:     
            {
                "path": "VarSet:PQs/Base_Radius",
                "label": "Radius",
                "name": "Base_Radius",
                "expr": "Base_Dia / 2",
                "readonly": true,
                "value_si": 381.0,
                "unit_si": "mm",
                "display": {
                    "value": 15.0,
                    "unit": "in"
                }
            },
            """
            var_data.append(var_info)

        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Skipping property '{prop_name}': {e}\n")

    return var_data

# ===== MAIN =====
doc = FreeCAD.ActiveDocument
if not doc:
    FreeCAD.Console.PrintError("No active document!\n")
    exit()

# Find VarSet by Label = "PQs"
target_label = "PQs"
varset_obj = None
for obj in doc.Objects:
    if obj.TypeId == 'App::VarSet' and obj.Label == target_label:
        varset_obj = obj
        break

if not varset_obj:
    FreeCAD.Console.PrintError(f"No VarSet found with Label='{target_label}'\n")
    # List all VarSets
    for obj in doc.Objects:
        if obj.TypeId == 'App::VarSet':
            FreeCAD.Console.PrintMessage(f"  Found: Name='{obj.Name}', Label='{obj.Label}'\n")
else:
    FreeCAD.Console.PrintMessage(f"Processing VarSet: '{varset_obj.Name}' (Label: '{varset_obj.Label}')\n")
    try:
        data = extract_varset_data(varset_obj)
        print(json.dumps(data, indent=4))
    except Exception as e:
        import traceback
        FreeCAD.Console.PrintError(f"Extraction failed: {e}\n")
        FreeCAD.Console.PrintError(traceback.format_exc())