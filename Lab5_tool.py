import arcpy
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

"""
You can change the `workspace` path as your wish.
"""
arcpy.env.workspace = BASE_DIR

"""
Here are some hints of what values the following variables should accept.
When running, the following code section will accept user input from terminal
Use `input()` method.

GDB_Folder = "***/Labs/Lab5"
GDB_Name = "Lab5.gdb"
Garage_CSV_File = "***/Labs/Lab5/garages.csv"
Garage_Layer_Name = "garages"
Campus_GDB = "***/Labs/Lab5/Campus.gdb"
Selected_Garage_Name = "Northside Parking Garage"
Buffer_Radius = "150 meter"
"""
### >>>>>> Add your code here
print("Please input the following parameters:\n")

GDB_Folder = input("GDB Folder: ")
GDB_Name = input("GDB Name: ")
Garage_CSV_File = input("Garage CSV File: ")
Garage_Layer_Name = input("Garge Layer Name: ")
Campus_GDB = input("Campus GDB: ")
Selected_Garage_Name = input("Selected Garage Name: ")
Buffer_Radius = int(input("Enter Buffer Radius: "))
### <<<<<< End of your code here

"""
In this section, you can re-use your codes from Lab4.

"""
### >>>>>> Add your code here

#create gdb
output_gdb_path = os.path.join(GDB_Folder, GDB_Name)
if arcpy.Exists(output_gdb_path):
    arcpy.Delete_management(output_gdb_path)
arcpy.management.CreateFileGDB(GDB_Folder, GDB_Name)
# GDB_Full_Path = 

#import garage csv

garages = arcpy.management.MakeXYEventLayer(Garage_CSV_File, "X", "Y", Garage_Layer_Name)
arcpy.FeatureClassToGeodatabase_conversion(garages,output_gdb_path)

### <<<<<< End of your code here

"""
Create a searchCursor.
Select the garage with `where` or `SQL` clause using `arcpy.analysis.Select` method.
Apply `Buffer` and `Clip` analysis on the selected feature.
Use `arcpy.analysis.Buffer()` and `arcpy.analysis.Clip()`.
"""
### >>>>>> Add your code here
#search surcor
structures = Campus_GDB + "/Structures"
where_clause = f"BldgName = '{Selected_Garage_Name}'"
cursor = arcpy.da.SearchCursor(structures, ["BldgName"], where_clause)

shouldProceed = False

for row in cursor:
    if Selected_Garage_Name in row:
        shouldProceed = True
        break

if shouldProceed == True:
    #select garage as feature layer
    selected_garage_layer_name=os.path.join(output_gdb_path, "selected_garage_layer")
    
    garage_feature = arcpy.analysis.Select(structures, selected_garage_layer_name, where_clause)

    # Buffer the selected building
    garage_buff_name = os.path.join(output_gdb_path, "building_buffered")
    arcpy.analysis.Buffer(garage_feature, garage_buff_name, f"{Buffer_Radius} meters")

    #clip
    clipped_output = os.path.join(output_gdb_path, "clipped_garage_buffer")
    arcpy.analysis.Clip(garage_buff_name, structures, clipped_output)
    print("success")
else:
    print("error")
### <<<<<< End of your code here