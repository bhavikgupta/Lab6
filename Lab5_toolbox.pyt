# -*- coding: utf-8 -*-

import arcpy
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Lab5_Toolbox"
        self.alias = "Lab5_Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Lab5_Tool]


class Lab5_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Lab5_Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Parameter 1 
        param_GDB_folder = arcpy.Parameter(
            displayName="GDB Folder",
            name="gdbfolder",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 2 
        param_GDB_Name = arcpy.Parameter(
            displayName="GDB Name",
            name="gdbname",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 3 
        param_Garage_CSV_File = arcpy.Parameter(
            displayName="Garage CSV File",
            name="garage_csv_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 4 
        param_Garage_Layer_Name = arcpy.Parameter(
            displayName="Garage Layer Name",
            name="garage_layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 5 
        param_Campus_GDB = arcpy.Parameter(
            displayName="Campus GDB",
            name="campus_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 6 
        param_Selected_Garage_Name = arcpy.Parameter(
            displayName="Selected Garage Name",
            name="selected_garage_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        # Parameter 7
        param_Buffer_Radius = arcpy.Parameter(
            displayName="Buffer Radius",
            name="buffer_radius",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        #Combine all params 
        params = [
            param_GDB_folder, 
            param_GDB_Name, 
            param_Garage_CSV_File,
            param_Garage_Layer_Name, 
            param_Campus_GDB, 
            param_Selected_Garage_Name, 
            param_Buffer_Radius
        ]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #query user input
        GDB_Folder = parameters[0].valueAsText
        GDB_Name = parameters[1].valueAsText
        Garage_CSV_File = parameters[2].valueAsText
        Garage_Layer_Name = parameters[3].valueAsText
        Campus_GDB = parameters[4].valueAsText
        Selected_Garage_Name = parameters[5].valueAsText
        Buffer_Radius = parameters[6].valueAsText

        # Print Messages
        arcpy.AddMessage("User Input:")
        arcpy.AddMessage(f"GDB Folder: {GDB_Folder}")
        arcpy.AddMessage(f"GDB Name: {GDB_Name}")
        arcpy.AddMessage(f"Garage CSV File: {Garage_CSV_File}")
        arcpy.AddMessage(f"Garage Layer Name: {Garage_Layer_Name}")
        arcpy.AddMessage(f"Campus GDB: {Campus_GDB}")
        arcpy.AddMessage(f"Selected Garage Name: {Selected_Garage_Name}")
        arcpy.AddMessage(f"Buffer Radius: {Buffer_Radius}")

        #create gdb
        output_gdb_path = os.path.join(GDB_Folder, GDB_Name)
        if arcpy.Exists(output_gdb_path):
            arcpy.Delete_management(output_gdb_path)
        arcpy.management.CreateFileGDB(GDB_Folder, GDB_Name)

        #import garage csv
        garages = arcpy.management.MakeXYEventLayer(Garage_CSV_File, "X", "Y", Garage_Layer_Name)
        arcpy.FeatureClassToGeodatabase_conversion(garages,output_gdb_path)

        #search surcor
        structures = Campus_GDB + "/Structures"
        where_clause = "BldgName = '%s'" % Selected_Garage_Name
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
            arcpy.AddMessage("Success")
        else:
            arcpy.AddError("Seems we couldn't find the building name you entered")

        return
