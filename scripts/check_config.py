"""Check what FreeCAD sees in user.cfg."""
import sys
import FreeCAD

params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General")
addl = params.GetString("AdditionalModulePaths", "")
print(f"AdditionalModulePaths from user.cfg: '{addl}'", flush=True)

# Also check Application level
try:
    addl2 = params.GetString("AdditionalModulePaths")
    print(f"Same: '{addl2}'", flush=True)
except Exception as e:
    print(f"Err: {e}", flush=True)

# Look at all general preferences
print("\nAll General prefs:", flush=True)
for name in ["FileOpenSavePath", "AutoloadModule", "LastModule", "AdditionalModulePaths"]:
    val = params.GetString(name, "<NOT SET>")
    print(f"  {name} = '{val}'", flush=True)

print("DONE", flush=True)