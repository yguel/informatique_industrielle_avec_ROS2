# View geometric data of a selected cylindrical face in FreeCAD
# Select a cylindrical face in the 3D view before running this script.
# Open a python console while opening View → Panels → Python console

import FreeCAD as App
import Part

doc = App.ActiveDocument
face = App.Gui.Selection.getSelectionEx()[0].SubObjects[0]
surf = face.Surface

print(type(face.Surface))
# Expect something like: <class 'Part.Cylinder'>

# Display the cylinder geometric data
# ===================================
axis_dir = surf.Axis     # <-- this is the direction you want
axis_pt  = surf.Center   # <-- this is the point you want
radius   = surf.Radius

print("Axis direction:", axis_dir)
# Expect something like: Axis direction: Vector (0.0, 0.0, 1.0)
print("Axis point:", axis_pt)
# Expect something like: Axis point: Vector (0.0, 0.0, 21.0)
print("Radius:", radius)
# Expect something like: Radius: 2.9


# Visualize the cylinder axis
# ============================
line = Part.Line(surf.Center, surf.Axis)   # point + direction
obj = doc.addObject("Part::Feature", "CylinderAxis")
obj.Shape = line.toShape()
doc.recompute()
# Expect something like: 39
