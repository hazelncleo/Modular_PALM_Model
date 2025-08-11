import numpy as np
import matplotlib.pyplot as plt
import os
import json
import glob
from shutil import copy2 as copy_input_file
from shutil import rmtree
import inquirer
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Global File Paths
modelfile_fpath = 'Model_Files'

analysis_fpath = os.path.join(modelfile_fpath, 'ANALYSIS')
geometry_fpath = os.path.join(modelfile_fpath, 'GEOMETRY')
material_fpath = os.path.join(modelfile_fpath, 'MATERIALS')

analysis_data_fpath = 'Analysis_Data.json'
geometry_data_fpath = 'Geometry_Data.json'
material_data_fpath = 'Material_Data.json'

# Lists for inquirer dialogs
all_object_types = ['analysis','geometry','material']
object_mods = ['create', 'modify', 'duplicate', 'delete', 'help', 'back']
all_commands = ['alter_objects', 'build_model', 'save_database', 'help', 'exit', 'force_exit']

def main():

    model = Model()

    model.main_loop()

    
'''
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------
- add more information for the objects (requirements, input files in folder, brief description, editable parameters) will need to edit create, modify, duplicate and delete at the very least
- make single dictionary not .materials, .analyses, .geometries. 
- build model
- add cancel option
- run model (maybe?) will be pog
- make way to display objects during main loop maybe?


NICE TO HAVE STUFF
-------------------------------
- __repr__
- __str__
- main help message
- object help message
- check inputted strings to make sure they are lowercase, numbers and underscores
- make tkinter dialog box open in directory with nice icon
- show objects?
- select object message
- run model progress?? :o

'''



class Model:
    def __init__(self):
        '''
        ---------------------------------------------------
        Initialise the class and load the data from the *.json files.
        ---------------------------------------------------
        '''
        # Initialise dictionaries
        self.materials = {}
        self.analyses  = {}
        self.geometries = {}
        
        # Load data from *.json files
        try:
            with open(analysis_data_fpath, 'r') as af:
                self.analyses = json.load(af)
                print('-----------------------------------------------')
                print('Loading from: "{}" was successful.'.format(analysis_data_fpath))
                print('-----------------------------------------------')
        
        except:
            raise FileNotFoundError('The Analysis .json file: "{}" does not exist. No Analyses have been loaded.'.format(analysis_data_fpath))
        

        try: 
            with open(geometry_data_fpath, 'r') as gf:
                self.geometries = json.load(gf)
                print('-----------------------------------------------')
                print('Loading from: "{}" was successful.'.format(geometry_data_fpath))
                print('-----------------------------------------------')

        except:
            raise FileNotFoundError('The Geometry .json file: "{}" does not exist. No Geometries have been loaded.'.format(geometry_data_fpath))


        try:
            with open(material_data_fpath, 'r') as mf:
                self.materials = json.load(mf)
                print('-----------------------------------------------')
                print('Loading from: "{}" was successful.'.format(material_data_fpath))
                print('-----------------------------------------------')

        except:
            raise FileNotFoundError('The Material .json file: "{}" does not exist. No Materials have been loaded.'.format(material_data_fpath))


    def __repr__(self):
        '''
        **********************TODO*******************************
        '''
        pass


    def __str__(self):

        return ':3'

    
    def print_database(self):
        '''
        ---------------------------------------------------
        Print Database in a cooler way than __str__. Hate that shit.
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('The Analyses currently loaded are: ')
        print('-----------------------------------------------')
        for analysis in self.analyses.values():
            fpath = os.path.join(analysis['File_Path'],'*.inp')
            print('Analysis Name: "{}", Path: "{}", Input files stored: "{}".'.format(analysis['Name'],analysis['File_Path'],str(glob.glob(fpath))))

        print('-----------------------------------------------')
        print('The Geometries currently loaded are: ')
        print('-----------------------------------------------')
        for geometry in self.geometries.values():
            fpath = os.path.join(geometry['File_Path'],'*.inp')
            print('Geometry Name: "{}", Path: "{}", Input files stored: "{}".'.format(geometry['Name'],geometry['File_Path'],str(glob.glob(fpath))))

        print('-----------------------------------------------')
        print('The Materials currently loaded are: ')
        print('-----------------------------------------------')
        for material in self.materials.values():
            fpath = os.path.join(material['File_Path'],'*.inp')
            print('Material Name: "{}", Path: "{}", Input files stored: "{}".'.format(material['Name'],material['File_Path'],str(glob.glob(fpath))))

        print('-----------------------------------------------')


    def main_loop(self):
        '''
        ---------------------------------------------------
        The main functioning loop
        ---------------------------------------------------
        '''

        while True:
            
            # Commands = ['alter_objects', 'build_model', 'save_database', 'help', 'exit', 'force_exit']
            command = inquirer.list_input('Pick Command: ', choices=all_commands)

            if command == 'exit':
                if self.yes_no_question('Are you sure you would like to exit?'):
                    self.save_database()
                    break

            elif command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'])

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_main_help_message(help_message)

            elif command == 'save_database':
                self.save_database()

            elif command == 'build_model':
                pass

            elif command == 'alter_objects':
                self.alter_objects()

            elif command == 'force_exit':
                if self.yes_no_question('Are you sure you would like to force exit without saving?'):
                    break


        print('-----------------------------------------------')
        print('Exiting the interface :3')
        print('-----------------------------------------------')


    def alter_objects(self):
        '''
        ---------------------------------------------------
        Saves the database to .json files
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Entering alter objects interface')
        print('-----------------------------------------------')

        command = ''

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'help', 'back']
            command = inquirer.list_input('Pick Object Alteration Command: ', choices=object_mods)


            if command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'])

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_object_help_message()


            elif command == 'create':

                # Get object type to be created
                object_type = self.select_object_type()

                # Get name of the object to be created
                object_name = self.new_object_name(object_type)

                # Get filepath of *.inp files to add to the new object filepath
                fpath = askdirectory(title = 'Select folder to read *.inp files: ')

                self.create_object(object_type, object_name, fpath)

                self.save_database()


            elif command == 'modify':
                
                # Select object to be modified
                object_name, object_type = self.select_object()
                
                # Select new name
                new_name = self.new_object_name(object_type)

                # Modify the object
                self.modify_object(object_type, object_name, new_name)

                self.save_database()


            elif command == 'duplicate':

                # Select object to be duplicated
                object_name, object_type = self.select_object()

                # Select new name
                new_name = self.new_object_name(object_type)

                # Duplicate the object to the new name
                self.duplicate_object(object_type, object_name, new_name)

                self.save_database()


            elif command == 'delete':
                
                # Select object to be deleted
                object_name, object_type = self.select_object()

                # Delete the object
                self.delete_object(object_type, object_name)

                self.save_database()


        print('-----------------------------------------------')
        print('Returning to the main loop')
        print('-----------------------------------------------')


    def yes_no_question(self, message):
        '''
        -----------------------------------------------
        Ask a yes/no question, "yes" returns True and "no" returns False
        -----------------------------------------------
        '''
        # Splits the message into lines
        strings = message.split('\n')

        # prints all except the final line
        for smaller_string in strings[:-1]:
            print(smaller_string)

        # Enquire the yes and no question using the final line as the message
        command = inquirer.list_input(strings[-1], choices=['yes','no'])

        if command == 'yes':
            return True 
        elif command == 'no':
            return False


    def new_object_name(self, object_type):
        '''
        ---------------------------------------------------
        Gets a new object name of a specific type, ensures that no object already exists of that type
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of object to be added. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        new_name : str
            The name for the new object
        ---------------------------------------------------
        '''

        # Get the current objects of a specific type
        if object_type == 'analysis':
            current_objects = [x for x in self.analyses.keys()]

        elif object_type == 'geometry':
            current_objects = [x for x in self.geometries.keys()]

        elif object_type == 'material':
            current_objects = [x for x in self.materials.keys()]

        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        new_name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers and underscores.')
            print('- It must be lowercase.')
            print('- It must be unique.')
            print('- These rules are not handled by the code and so if broken may break the program.')
            print('---------------------------------------------------')
            print('The object names currently in use for the object type: "{}", are listed below: '.format(object_type))
            print(current_objects)
            print('---------------------------------------------------')
            
            new_name = input('Please enter a new name for the object to be created: ')

            if new_name not in current_objects:
                print('---------------------------------------------------')
                print('The name: "{}", for the new object has been selected.'.format(new_name))
                print('---------------------------------------------------')
                return new_name
            
            else: 
                print('---------------------------------------------------')
                print('ERROR: The name: {}, already exists in the database.'.format(new_name))
                print('---------------------------------------------------')


    def print_main_help_message(self):
        '''
        ---------------------------------------------------
        Prints a help message for using the text interface

        **********************************TODO***********************************
        ---------------------------------------------------
        '''

        pass


    def print_object_help_message(self):
        '''
        ---------------------------------------------------
        Prints a help message for using the alter object text interface

        **********************************TODO***********************************
        ---------------------------------------------------
        '''


    def save_database(self):
        '''
        ---------------------------------------------------
        Saves the database to .json files
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Saving the Database')
        print('-----------------------------------------------')
        # Save analysis data
        with open(analysis_data_fpath, 'w') as af:
            json.dump(self.analyses, af)
            print('-----------------------------------------------')
            print('Saving to: "{}" was successful.'.format(analysis_data_fpath))
            print('-----------------------------------------------')

        # Save geometry data
        with open(geometry_data_fpath, 'w') as gf:
            json.dump(self.geometries, gf)
            print('-----------------------------------------------')
            print('Saving to: "{}" was successful.'.format(geometry_data_fpath))
            print('-----------------------------------------------')

        # Save material data
        with open(material_data_fpath, 'w') as mf:
            json.dump(self.materials, mf)
            print('-----------------------------------------------')
            print('Saving to: "{}" was successful.'.format(geometry_data_fpath))
            print('-----------------------------------------------')

        
    def select_object_type(self):
        '''
        ---------------------------------------------------
        Pick an object type from the list of three object types: "analysis", "geometry", "material".
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            One of the three object types, chosen by the user.
        ---------------------------------------------------
        '''
        object_type = inquirer.list_input('Pick Object Type: ', choices=all_object_types)

        print('-----------------------------------------------')
        print('Object Type: "{}" was selected.'.format(object_type))
        print('-----------------------------------------------')

        return object_type
    

    def select_object(self):
        '''
        ---------------------------------------------------
        Select an object from all the objects of a specific type currently in the database.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        selected_object : str
            The object of the specified type that was chosen by the user.
        object_type : str, [analysis/geometry/material]
            The object type of the object that was chosen by the user.
        ---------------------------------------------------
        '''
        object_type = self.select_object_type()

        if object_type == 'analysis':
            selected_object = inquirer.list_input('Pick the Analysis object: ', choices=[x for x in self.analyses.keys()])

        elif object_type == 'geometry':
            selected_object = inquirer.list_input('Pick the Geometry object: ', choices=[x for x in self.geometries.keys()])

        elif object_type == 'material':
            selected_object = inquirer.list_input('Pick the Material object: ', choices=[x for x in self.materials.keys()])

        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        
        print('-----------------------------------------------')
        print('Object: "{}" of object type: "{}" was selected.'.format(selected_object,object_type))
        print('-----------------------------------------------')
        
        return selected_object, object_type


    def create_object(self, object_type, object_name, source_file_path):
        '''
        ---------------------------------------------------
        Creates a new object in the database with an object type  from a specified file path. All input files from this file path will be copied to a new destination folder
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of object to be added to the database. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be added. This will be used in the database, and as the file path that the input files will be stored in.

        source_file_path : str
            The file path which contains the input files to be added to the database. The names of these files will be used in the database, so must be set correctly.
        ---------------------------------------------------
        '''
        print('-----------------------------------------------')
        print('Create object operation started.')
        print('-----------------------------------------------')

        
        # Create material object in the database and move the .inp files to the destination folder
        if object_type == 'material':

            # Get file path
            dest_file_path = os.path.join(material_fpath, object_name.upper())

            # Check file path does not already exist
            if os.path.exists(dest_file_path):
                raise FileExistsError('The file path: "{}" already exists.'.format(dest_file_path))

            # Create object in the database
            self.materials[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The material: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # Create analysis object in the database and move the .inp files to the destination folder
        elif object_type == 'analysis':

            # Get destination filepath of analysis
            dest_file_path = os.path.join(analysis_fpath, object_name.upper())

            # Check file path does not already exist
            if os.path.exists(dest_file_path):
                raise FileExistsError('The file path: "{}" already exists.'.format(dest_file_path))

            # Create object in the database
            self.analyses[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The analysis: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # Create geometry object in the database and move the .inp files to the destination folder
        elif object_type == 'geometry':

            # Get destination filepath of analysis
            dest_file_path = os.path.join(geometry_fpath, object_name.upper())

            # Check file path does not already exist
            if os.path.exists(dest_file_path):
                raise FileExistsError('The file path: "{}" already exists.'.format(dest_file_path))

            # Create object in the database
            self.geometries[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The geometry: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # raise error if the object is not a valid type
        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        # Copy *.inp files from source file path to the destination file path
        files_to_copy = glob.glob(os.path.join(source_file_path,'*.inp'))
        
        # Create destination folder
        os.makedirs(dest_file_path, exist_ok=True)
        print('The Destination folder: "{}" has been successfully created.'.format(dest_file_path))

        # Copy material file to new folder with new name
        for file in files_to_copy:
            file_name = file.split('\\')[-1]

            try:
                copy_input_file(file, os.path.join(dest_file_path, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully added to the destination filepath: "{}".'.format(file_name[:-4].upper()+'.inp',dest_file_path))
            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))
            
        print('-----------------------------------------------')
        print('Create object operation successful.')
        print('-----------------------------------------------')
            
    
    def modify_object(self, object_type, object_name, new_name):
        '''
        ---------------------------------------------------
        Modifies either an objects name or its fpath
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of the object to be modified. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be modified. If this does not match an object in the object type dictionary then an error will be thrown.
        
        new_name : str
            The new name of the object.
        ---------------------------------------------------
        '''
        # Check the user would like to delete the object
        if not self.yes_no_question('Would you like to modify object: "{}" of type: "{}"? \nNOTE: The database will be saved automatically afterwards and the previous name will be LOST'.format(object_name, object_type)):
            return

        print('-----------------------------------------------')
        print('Modify object operation begun.')
        print('-----------------------------------------------')

        if object_type == 'material':

            # Change folder name
            try:
                fpath = os.path.join(material_fpath, object_name.upper())
                new_fpath = os.path.join(material_fpath, new_name.upper())
                os.rename(fpath, new_fpath)
                print('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath))

            except:
                raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath))
            
            # Change name
            self.materials[object_name]['Name'] = new_name.lower()
            self.materials[new_name] = self.materials.pop(object_name)
            print('The material name has been changed successfully from: "{}" to "{}".'.format(object_name,new_name))

            # Change fpath
            self.materials[new_name]['File_Path'] = new_fpath
            print('The filepath for material "{}" was successfully changed to "{}" in the local dictionary.'.format(new_name,new_fpath))


        elif object_type == 'analysis':
            
            # Change folder name
            try:
                fpath = os.path.join(analysis_fpath, object_name.upper())
                new_fpath = os.path.join(analysis_fpath, new_name.upper())
                os.rename(fpath, new_fpath)
                print('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath))

            except:
                raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath))
            
            # Change name
            self.analyses[object_name]['Name'] = new_name.lower()
            self.analyses[new_name] = self.analyses.pop(object_name)
            print('The analysis name has been changed successfully from: "{}" to "{}".'.format(object_name,new_name))

            # Change fpath
            self.analyses[new_name]['File_Path'] = new_fpath
            print('The filepath for analysis "{}" was successfully changed to "{}" in the local dictionary.'.format(new_name,new_fpath))


        elif object_type == 'geometry':

            # Change folder name
            try:
                fpath = os.path.join(geometry_fpath, object_name.upper())
                new_fpath = os.path.join(geometry_fpath, new_name.upper())
                os.rename(fpath, new_fpath)
                print('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath))

            except:
                raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath))
            
            # Change name
            self.geometries[object_name]['Name'] = new_name.lower()
            self.geometries[new_name] = self.geometries.pop(object_name)
            print('The geometry name has been changed successfully from: "{}" to "{}".'.format(object_name,new_name))

            # Change fpath
            self.geometries[new_name]['File_Path'] = new_fpath
            print('The filepath for geometry "{}" was successfully changed to "{}" in the local dictionary.'.format(new_name,new_fpath))


        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        print('-----------------------------------------------')
        print('Modify object operation successful.')
        print('-----------------------------------------------')


    def duplicate_object(self, object_type, object_name, new_name):
        '''
        ---------------------------------------------------
        Duplicates an object, both in the local dictionary and into a new filepath. 
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of the object to be duplicated. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be duplicated, all of this *.inp files will be duplicated from the file path. If this does not match an object in the object type dictionary then an error will be thrown.
        
        new_name : str
            The new name of the object, this will be the name of the new file path.
        ---------------------------------------------------
        '''
        print('-----------------------------------------------')
        print('Duplicate object operation begun.')
        print('-----------------------------------------------')

        if object_type == 'material':
            
            # Get File paths
            fpath = os.path.join(material_fpath, object_name.upper())
            new_fpath = os.path.join(material_fpath, new_name.upper())

            # Check file path does not already exist
            if os.path.exists(new_fpath):
                raise FileExistsError('The file path: "{}" already exists.'.format(new_fpath))

            # Make new folder
            try:
                os.makedirs(new_fpath, exist_ok=True)
                print('The filepath: "{}" was created successfully.'.format(new_fpath))

            except:
                raise FileExistsError('Creating the filepath: "{}" has failed.'.format(new_fpath))
            
            # Duplicate dictionary object
            self.materials[new_name.lower()] = {'Name': new_name.lower(), 'File_Path': new_fpath}

            # Get *.inp files as list
            files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

            # Copy *.inp files to new file path
            for file in files_to_copy:

                file_name = file.split('\\')[-1]

                try:
                    copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                    print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))

                except:
                    raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))


        elif object_type == 'analysis':

            # Get File paths
            fpath = os.path.join(analysis_fpath, object_name.upper())
            new_fpath = os.path.join(analysis_fpath, new_name.upper())

            # Check file path does not already exist
            if os.path.exists(new_fpath):
                raise FileExistsError('The file path: "{}" already exists.'.format(new_fpath))

            # Make new folder
            try:
                os.makedirs(new_fpath, exist_ok=True)
                print('The filepath: "{}" was created successfully.'.format(new_fpath))

            except:
                raise FileExistsError('Creating the filepath: "{}" has failed.'.format(new_fpath))
            
            # Duplicate dictionary object
            self.analyses[new_name.lower()] = {'Name': new_name.lower(), 'File_Path': new_fpath}

            # Get *.inp files as list
            files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

            # Copy *.inp files to new file path
            for file in files_to_copy:

                file_name = file.split('\\')[-1]

                try:
                    copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                    print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))
                    
                except:
                    raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))

        elif object_type == 'geometry':

            # Get File paths
            fpath = os.path.join(geometry_fpath, object_name.upper())
            new_fpath = os.path.join(geometry_fpath, new_name.upper())

            # Check file path does not already exist
            if os.path.exists(new_fpath):
                raise FileExistsError('The file path: "{}" already exists.'.format(new_fpath))

            # Make new folder
            try:
                os.makedirs(new_fpath, exist_ok=True)
                print('The filepath: "{}" was created successfully.'.format(new_fpath))

            except:
                raise FileExistsError('Creating the filepath: "{}" has failed.'.format(new_fpath))
            
            # Duplicate dictionary object
            self.geometries[new_name.lower()] = {'Name': new_name.lower(), 'File_Path': new_fpath}

            # Get *.inp files as list
            files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

            # Copy *.inp files to new file path
            for file in files_to_copy:

                file_name = file.split('\\')[-1]

                try:
                    copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                    print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))
                    
                except:
                    raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))

        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        print('-----------------------------------------------')
        print('Duplicate object operation successful.')
        print('-----------------------------------------------')


    def delete_object(self, object_type, object_name):    
        '''
        ---------------------------------------------------
        Deletes an object from the local database and the folder of *.inp files.
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of the object to be deleted from the database. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be deleted. If this does not match an object in the object type dictionary then an error will be thrown.
        ---------------------------------------------------
        '''

        # Check the user would like to delete the object
        if not self.yes_no_question('Would you like to delete object: "{}" of type: "{}"? \nNOTE: The database will be saved automatically afterwards and all related data will be LOST'.format(object_name, object_type)):
            return
        
        print('-----------------------------------------------')
        print('Delete object operation begun.')
        print('-----------------------------------------------')

        # Make object name lower case
        object_name = object_name.lower()


        if object_type == 'analysis':
   
            # Get file path of files
            fpath = os.path.join(analysis_fpath, object_name.upper())

            # Delete files from filepath
            try:
                rmtree(fpath)
                print('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type))
                
            except:
                raise FileNotFoundError('The fpath: "{}" does not exist. The database may be corrupted.'.format(fpath))
            
            # Then delete from local dictionary
            try:
                self.analyses.pop(object_name)
                print('The analysis: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Analysis Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.analyses.keys()]))


        elif object_type == 'geometry':

            # Get file path of files
            fpath = os.path.join(geometry_fpath, object_name.upper())

            # Delete files from filepath
            try:
                rmtree(fpath)
                print('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type))
                
            except:
                raise FileNotFoundError('The fpath: "{}" does not exist. The database may be corrupted.'.format(fpath))
            
            # Then delete from local dictionary
            try:
                self.geometries.pop(object_name)
                print('The geometry: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Geometry Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.geometries.keys()]))
            

        elif object_type == 'material':

            # Get file path of files
            fpath = os.path.join(material_fpath, object_name.upper())

            # Delete files from filepath
            try:
                rmtree(fpath)
                print('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type))
                
            except:
                raise FileNotFoundError('The fpath: "{}" does not exist. The database may be corrupted.'.format(fpath))

            # then delete from local dictionary
            try:
                self.materials.pop(object_name)
                print('The material: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Material Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.materials.keys()]))
            

        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        


        
        print('-----------------------------------------------')
        print('Delete object operation successful.')
        print('-----------------------------------------------')
        

    def build_model(self, Model_Name):

        pass

    # *** STILL NOT SURE IF SHOULD RUN MODEL THROUGH THIS ***
    # def run_model(self, Model_Name): 

if __name__ == '__main__':
    main()