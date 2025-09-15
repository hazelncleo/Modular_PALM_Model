import os
import json
import glob
from shutil import copy2 as copy_input_file
from shutil import rmtree
import inquirer
from tkinter import Tk
from tkinter.filedialog import askdirectory
import string
  
'''
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------
- add more information for the objects (input files in folder, editable parameters) will need to edit create, modify, duplicate and delete at the very least
- set requirements (basic implementation atm, might need to be made more complex)
- validate
- modify model
- duplicate model
- delete model
- postprocess model
- alter model loop
- add cancel option (?)
- run model
- clean up main loops


NICE TO HAVE STUFF
-------------------------------
- __repr__
- __str__
- main help message
- object help message
- model help message
- make tkinter dialog box not lose cmd priority
- run model progress?? :o
'''



'''
**************************************************************************************************
*************************CLASSIFYING OBJECTS AND MODELS AND MORE FUNCTIONS YIPPEE*****************
**************************************************************************************************
'''

class Abaqus_Object:
    def __init__(self, object_name, object_type, source_file_path, description, requirements, fluid_required):
        '''
        ---------------------------------------------------
        Creates a new object class from the listed variables below
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_name : str
            The name of the object to be added. This will be used in the database, and as the file path that the input files will be stored in.
            
        object_type : str, [analysis/geometry/material]
            The type of object to be created. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        source_file_path : str
            The file path which contains the input files associated with this object. The names of these files will be used in the database, so must be set correctly.

        description : str
            A description of what the object to be created is.

        requirements : list
            A list of all the requirements/dependencies for this object to work in a model.

        fluid_required : boolean
            variable only relevant for analysis objects, True if fluid representation required, otherwise False.
        ---------------------------------------------------
        '''
        
        print('-----------------------------------------------')
        print('Create object operation started.')
        print('-----------------------------------------------')
        
        self.name = object_name.lower()
        self.object_type = object_type
        self.file_path = ''
        self.description = ''
        self.requirements = {}
        


        # Get destination filepath of analysis
        dest_file_path = os.path.join(self.fpaths[object_type], object_name.upper())

        # Check file path does not already exist
        if os.path.exists(dest_file_path):
            print('-----------------------------------------------')
            print('ERROR: The fpath: "{}", already exists.')
            print('Returning to main loop.')
            print('-----------------------------------------------')
            return

        # Create object in the database
        self.data[object_type][object_name.lower()] = {'Name': object_name.lower(),
                                                       'File_Path': dest_file_path,
                                                       'Description': description,
                                                       'Requirements' : requirements,
                                                       'Fluid_Required' : fluid_required}
        
        print('The {}: "{}" has been successfully added to the local dictionary.'.format(object_type, object_name))
        

        # Copy *.inp files from source file path to the destination file path
        files_to_copy = glob.glob(os.path.join(source_file_path,'*.inp'))
        
        # Create destination folder
        os.makedirs(dest_file_path, exist_ok=True)
        print('The Destination folder: "{}" has been successfully created.'.format(dest_file_path))

        # Copy material file to new folder with new name
        for file in files_to_copy:
            file_name = file.split('\\')[-1]

            # Try to copy the input file
            try:
                copy_input_file(file, os.path.join(dest_file_path, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully added to the destination filepath: "{}".'.format(file_name[:-4].upper()+'.inp',dest_file_path))
            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath. The database may now be corrupted.'.format(file_name[:-4].upper()+'.inp'))
            
        print('-----------------------------------------------')
        print('Create object operation successful.')
        print('-----------------------------------------------')
    
        

def get_file_path():
    root = Tk()
    root.iconbitmap('cade.ico')
    root.overrideredirect(1)  # Remove window border
    root.geometry('0x0+0+0')  # Place offscreen
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    file_path = askdirectory(title = 'Select folder to read *.inp files: ', initialdir=os.path.abspath(os.getcwd()))
    root.destroy()
    return file_path


class Modular_Abaqus_Builder:
    def __init__(self):
        '''
        ---------------------------------------------------
        Initialise the class and load the data from the *.json files.
        ---------------------------------------------------
        '''

        # Set filepaths
        modelfile_fpath = 'Model_Files'
        self.fpaths = {'model_files' : modelfile_fpath,
                       'analysis' : os.path.join(modelfile_fpath, 'ANALYSIS'),
                       'geometry' : os.path.join(modelfile_fpath, 'GEOMETRY'),
                       'material': os.path.join(modelfile_fpath, 'MATERIALS'),
                       'simulation': 'Simulations',
                       'data': 'Data.json'}
        
        # Set allowed characters
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'),
                                   'Model' : set(string.ascii_letters + string.digits + '_-!()[]'),
                                   'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"')}
        
        # Set inquirer dialog lists
        self.inquirer_dialogs = {'Object_Types' : ['analysis','geometry','material'],
                                 'Main_Loop' : ['alter_objects', 'build_model', 'save_database', 'help', 'exit', 'force_exit'],
                                 'Object_Loop' : ['create', 'modify', 'duplicate', 'delete', 'help', 'back'],
                                 'Model_Loop' : ['build', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']}
        
        # Load data from Data.json
        try:
            with open(self.fpaths['data'], 'r') as df:
                self.data = json.load(df)
                print('-----------------------------------------------')
                print('Loading from: "{}" was successful.'.format(self.fpaths['data']))
                print('-----------------------------------------------')
        
        # If it doesnt exist load an empty dictionary
        except:
            self.data = {'analysis': {}, 'geometry': {}, 'material': {}, 'simulation': {}}
            print('The Data .json file: "{}" does not exist. A default dictionary has been loaded.\nUpon save a Data.json file will be made.'.format(self.fpaths['data']))
            

    def save_database(self):
            '''
            ---------------------------------------------------
            Saves the database to .json files
            ---------------------------------------------------
            '''

            print('-----------------------------------------------')
            print('Saving the Database')
            print('-----------------------------------------------')
            # Save data
            with open(self.fpaths['data'], 'w') as df:
                json.dump(self.data, df)
                print('-----------------------------------------------')
                print('Save to: "{}" was successful.'.format(self.fpaths['data']))
                print('-----------------------------------------------')


    def main_loop(self):
        '''
        ---------------------------------------------------
        The main functioning loop
        ---------------------------------------------------
        '''

        while True:
            
            # Commands = ['alter_objects', 'build_model', 'save_database', 'help', 'exit', 'force_exit']
            command = inquirer.list_input('Pick Command: ', choices=self.inquirer_dialogs['Main_Loop'])

            if command == 'exit':
                if self.yes_no_question('Are you sure you would like to exit?'):
                    self.save_database()
                    break

            elif command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'])

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_main_help_message()

            elif command == 'save_database':
                self.save_database()

            elif command == 'build_model':

                # Get new model name
                model_name = self.new_model_name()

                # Get model description
                description = self.provide_description()

                # Build model
                self.build_model(model_name, description)

                self.save_database()
                

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
        Main loop for altering objects in the database
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Entering alter objects interface')
        print('-----------------------------------------------')

        command = ''

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'help', 'back']
            command = inquirer.list_input('Pick Object Alteration Command: ', choices=self.inquirer_dialogs['Object_Loop'])


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

                # Get description for object to be added
                description = self.provide_description()

                # Get requirements of analysis
                if object_type == 'analysis':
                    fluid_required, requirements = self.set_requirements()
                else:
                    requirements = []
                    fluid_required = False

                # Get filepath of *.inp files to add to the new object filepath
                fpath = askdirectory(title = 'Select folder to read *.inp files: ', initialdir=os.path.abspath(os.getcwd()))

                # Check if cancel button was pushed
                if fpath:

                    # Check if directory contains any .inp files
                    if any(file.endswith('.inp') for file in os.listdir(fpath)):
                        self.create_object(object_type, object_name, fpath, description, requirements, fluid_required)

                        self.save_database()

                    else:
                        print('-----------------------------------------------')
                        print('ERROR: The directory: "{}", does not contain any .inp files.'.format(fpath))
                        print('Returning to main loop.')
                        print('-----------------------------------------------')

                else:
                    print('-----------------------------------------------')
                    print('ERROR: The cancel button was pushed and no directory was chosen.')
                    print('Returning to main loop.')
                    print('-----------------------------------------------')


            elif command == 'modify':
                
                # Select object to be modified
                object_name, object_type = self.select_object()
                
                # Check if object was available
                if object_name:
                    
                    # Get objects to be changed
                    change_list = inquirer.checkbox('What would you like to change about the object: "{}", of type: "{}"'.format(object_name,object_type),
                                                    choices = ['name', 'description', 'requirements', 'fluid_required'])

                    # Create change dictionary
                    change_dict = {'name': {'change' : False, 'new_name' : ''},
                                   'description' : {'change' : False, 'new_description' : ''},
                                   'requirements' : {'change' : False, 'new_requirement' : []},
                                   'fluid_required' : {'change' : False, 'new_fluid_required' : False}}
                    
                    # If no changes picked return to main loop
                    if not change_list:
                        print('-----------------------------------------------')
                        print('No changes picked.')
                        print('Returning to main loop.')
                        print('-----------------------------------------------')
                        continue

                    if 'name' in change_list:

                        # Select new name
                        change_dict['name']['new_name'] = self.new_object_name(object_type)
                        change_dict['name']['change'] = True

                    if 'description' in change_list:

                        # Select new description
                        change_dict['description']['new_description'] = self.provide_description()
                        change_dict['description']['change'] = True

                    if 'requirements' in change_list:
                        
                        # Select new requirements
                        change_dict['requirements']['new_requirement'] = []
                        change_dict['requirements']['change'] = True

                    if ('fluid_required' in change_list) and (object_type == 'analysis'):

                        # Select new fluid required state
                        change_dict['fluid_required']['change'] = True
                        change_dict['fluid_required']['new_fluid_required'] = self.yes_no_question('Should the modified object require an acoustic fluid representation?')

                    # Modify the object
                    self.modify_object(object_type, object_name, change_dict)

                    self.save_database()

                else: 
                    print('Returning to main loop.')
                    print('-----------------------------------------------')

            elif command == 'duplicate':

                # Select object to be duplicated
                object_name, object_type = self.select_object()

                # Check if object was available
                if object_name:
                
                    # Select new name
                    new_name = self.new_object_name(object_type)

                    # Duplicate the object to the new name
                    self.duplicate_object(object_type, object_name, new_name)

                    self.save_database()

                else: 
                    print('Returning to main loop.')
                    print('-----------------------------------------------')


            elif command == 'delete':
                
                # Select object to be deleted
                object_name, object_type = self.select_object()

                # Check if object was available
                if object_name:

                    # Delete the object
                    self.delete_object(object_type, object_name)

                    self.save_database()

                else: 
                    print('Returning to main loop.')
                    print('-----------------------------------------------')


        print('-----------------------------------------------')
        print('Returning to the main loop')
        print('-----------------------------------------------')


    def alter_models(self):
        '''
        ---------------------------------------------------
        Main loop for altering models in the database
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Entering alter models interface')
        print('-----------------------------------------------')
        
        command = ''

        while command != 'back':
            
            # Commands = ['build', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']
            command = inquirer.list_input('Pick Model Alteration Command: ', choices=self.inquirer_dialogs['Model_Loop'])


    def new_model_name(self):
        '''
        ---------------------------------------------------
        Returns a new model name
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        new_name : str
            The name for the new model
        ---------------------------------------------------
        '''
        # Get current models
        current_models = [x for x in self.data['simulation'].keys()]

        new_name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the model to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers and the following symbols (not including single quotes): \'_-!()[]\'')
            print('- It must be unique.')
            print('---------------------------------------------------')
            print('The model names currently in use are listed below: ')
            print(current_models)
            print('---------------------------------------------------')
            
            new_name = input('Please enter a new name for the model to be created: ')

            if not new_name:
                print('---------------------------------------------------')
                print('ERROR: The name provided was an empty string')
                print('---------------------------------------------------')

            elif not (set(new_name) <= self.allowed_characters['Model']):
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", is not entirely lowercase, numbers or underscores.'.format(new_name))
                print('---------------------------------------------------')
            
            elif new_name not in current_models:
                print('---------------------------------------------------')
                print('The name: "{}", for the new model has been selected.'.format(new_name))
                print('---------------------------------------------------')
                return new_name
            
            else: 
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(new_name))
                print('---------------------------------------------------')


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
        # Get current objects
        current_objects = [x for x in self.data[object_type].keys()]

        new_name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, underscores and hyphens.')
            print('- It must be lowercase.')
            print('- It must be unique.')
            print('---------------------------------------------------')
            print('The object names currently in use for the object type: "{}", are listed below: '.format(object_type))
            print(current_objects)
            print('---------------------------------------------------')
            
            new_name = input('Please enter a new name for the object to be created: ')

            if not new_name:
                print('---------------------------------------------------')
                print('ERROR: The name provided was an empty string')
                print('---------------------------------------------------')

            elif not (set(new_name) <= self.allowed_characters['Name']):
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", is not entirely lowercase, numbers or underscores.'.format(new_name))
                print('---------------------------------------------------')
            
            elif new_name not in current_objects:
                print('---------------------------------------------------')
                print('The name: "{}", for the new object has been selected.'.format(new_name))
                print('---------------------------------------------------')
                return new_name
            
            else: 
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(new_name))
                print('---------------------------------------------------')

        
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

        object_type = inquirer.list_input('Pick Object Type: ', choices=self.inquirer_dialogs['Object_Types'])

        print('-----------------------------------------------')
        print('Object Type: "{}" was selected.'.format(object_type))
        print('-----------------------------------------------')

        return object_type
    

    def select_object(self, object_type = '', message = ''):
        '''
        ---------------------------------------------------
        Select an object from all the objects of a specific type currently in the database.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        selected_object : str
            The object of the specified type that was chosen by the user. If no objects of a specified type are available an empty string will be returned.
        object_type : str, [analysis/geometry/material]
            The object type of the object that was chosen by the user. This is always returned.
        message : str
            An optional message to add to the inquirer list input message
        ---------------------------------------------------
        '''
        if not object_type:
            object_type = self.select_object_type()

        # Get available choices
        choices = [x for x in self.data[object_type].keys()]

        # Check there are choices available
        if len(choices):
            selected_object = inquirer.list_input('Pick the {} object{}: '.format(object_type,message), choices=choices)

        else:
            print('-----------------------------------------------')
            print('ERROR: no objects of type: "{}" to select.'.format(object_type))
            return '', object_type
        
        print('-----------------------------------------------')
        print('Object: "{}" of object type: "{}" was selected.'.format(selected_object,object_type))
        print('-----------------------------------------------')
        
        return selected_object, object_type


    def provide_description(self):
        '''
        ---------------------------------------------------
        Provide a description for the object added to the database.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        description : str
            A string typed by the user that describes the new object that only has characters from "allowed_characters_description".
        ---------------------------------------------------
        '''

        description = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a description for the object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.?! ()[]"\'')
            print('---------------------------------------------------')
            
            description = input('Please enter a description for the object to be created: ')

            if not description:
                print('---------------------------------------------------')
                print('ERROR: The description provided was an empty string')
                print('---------------------------------------------------')

            elif not (set(description) <= self.allowed_characters['Description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(description))
                print('---------------------------------------------------')
            
            else:
                print('---------------------------------------------------')
                print('The description: "{}", for the new object has been selected.'.format(description))
                print('---------------------------------------------------')
                return description


    def set_requirements(self):
        '''
        
        '''

        requirements = ['MAIN.inp', 'SOLID_GEOMETRY.inp', 'SOLID_MATERIAL.inp', 'ANALYSIS.inp']

        # if requires acoustic fluid add , FLUID_MATERIAL.inp, ASSEMBLY.inp
        fluid = self.yes_no_question('Does the analysis require an acoustic fluid representation? ')

        if fluid:
            requirements.append('FLUID_GEOMETRY.inp') 
            requirements.append('FLUID_MATERIAL.inp') 
            requirements.append('ASSEMBLY.inp') 


        return fluid, requirements


    def create_object(self, object_type, object_name, source_file_path, description, requirements, fluid_required):
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

        description : str
            A description of what the object to be created is.

        requirements : list
            A list of all the requirements/dependencies for this object to work in a model.

        fluid_required : boolean
            variable only relevant for analysis objects, True if fluid representation required else, False.
        ---------------------------------------------------
        '''
        print('-----------------------------------------------')
        print('Create object operation started.')
        print('-----------------------------------------------')

        # Get destination filepath of analysis
        dest_file_path = os.path.join(self.fpaths[object_type], object_name.upper())

        # Check file path does not already exist
        if os.path.exists(dest_file_path):
            print('-----------------------------------------------')
            print('ERROR: The fpath: "{}", already exists.')
            print('Returning to main loop.')
            print('-----------------------------------------------')
            return

        # Create object in the database
        self.data[object_type][object_name.lower()] = {'Name': object_name.lower(),
                                                       'File_Path': dest_file_path,
                                                       'Description': description,
                                                       'Requirements' : requirements,
                                                       'Fluid_Required' : fluid_required}
        
        print('The {}: "{}" has been successfully added to the local dictionary.'.format(object_type, object_name))
        

        # Copy *.inp files from source file path to the destination file path
        files_to_copy = glob.glob(os.path.join(source_file_path,'*.inp'))
        
        # Create destination folder
        os.makedirs(dest_file_path, exist_ok=True)
        print('The Destination folder: "{}" has been successfully created.'.format(dest_file_path))

        # Copy material file to new folder with new name
        for file in files_to_copy:
            file_name = file.split('\\')[-1]

            # Try to copy the input file
            try:
                copy_input_file(file, os.path.join(dest_file_path, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully added to the destination filepath: "{}".'.format(file_name[:-4].upper()+'.inp',dest_file_path))
            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath. The database may now be corrupted.'.format(file_name[:-4].upper()+'.inp'))
            
        print('-----------------------------------------------')
        print('Create object operation successful.')
        print('-----------------------------------------------')
            
    
    def modify_object(self, object_type, object_name, change_dict):
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
        
        change_dict : dict
            A dictionary containing the values to be modified
        ---------------------------------------------------
        '''
        # Check the user would like to delete the object
        if not self.yes_no_question('Would you like to modify object: "{}" of type: "{}"? \nNOTE: The database will be saved automatically afterwards and the previous name will be LOST'.format(object_name, object_type)):
            return

        print('-----------------------------------------------')
        print('Modify object operation begun.')
        print('-----------------------------------------------')
        
        # Change name/file directory
        if change_dict['name']['change']:

            # Change folder name
            try:
                fpath = os.path.join(self.fpaths[object_type], object_name.upper())
                new_fpath = os.path.join(self.fpaths[object_type], change_dict['name']['new_name'].upper())
                os.rename(fpath, new_fpath)
                print('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath))

            except:
                raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath))
            
            # Change name
            self.data[object_type][object_name]['Name'] = change_dict['name']['new_name'].lower()
            self.data[object_type][change_dict['name']['new_name']] = self.data[object_type].pop(object_name)
            print('The {} name has been changed successfully from: "{}" to "{}".'.format(object_type,object_name,change_dict['name']['new_name']))

            # Update object name if reused
            object_name = change_dict['name']['new_name']

            # Change fpath
            self.data[object_type][change_dict['name']['new_name']]['File_Path'] = new_fpath
            print('The filepath for {} "{}" was successfully changed to "{}" in the local dictionary.'.format(object_type,change_dict['name']['new_name'],new_fpath))
            
            print('Name change was successful.')

        # Change description
        if change_dict['description']['change']:
            self.data[object_type][object_name]['Description'] = change_dict['description']['new_description']
            print('Description change was successful.')

        # Change requirements
        if change_dict['requirements']['change']:
            self.data[object_type][object_name]['Requirements'] = change_dict['requirements']['new_requirement']
            print('Requirements change was successful.')

        # Change fluid_required
        if change_dict['fluid_required']['change']:
            self.data[object_type][object_name]['Fluid_Required'] = change_dict['fluid_required']['new_fluid_required']
            print('Fluid_Required change was successful.')

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

        # Get File paths
        fpath = os.path.join(self.fpaths[object_type], object_name.upper())
        new_fpath = os.path.join(self.fpaths[object_type], new_name.upper())

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
        self.data[object_type][new_name.lower()] = self.data[object_type][object_name.lower()]
        self.data[object_type][new_name.lower()]['Name'] = new_name.lower()
        self.data[object_type][new_name.lower()]['File_Path'] = new_fpath

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

        # Get file path of files
        fpath = os.path.join(self.fpaths[object_type], object_name.upper())

        # Delete files from filepath
        rmtree(fpath)
        print('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type))
            
        
        # Then delete from local dictionary
        self.data[object_type].pop(object_name)
        print('The {}: "{}" has been successfully removed from the local dictionary.'.format(object_type,object_name))     
        
        print('-----------------------------------------------')
        print('Delete object operation successful.')
        print('-----------------------------------------------')
        

    def build_model(self, model_name, description):
        '''
        Build model
        '''
        
        # Add to local dictionary
        self.data['simulation'][model_name] = {'Name' : model_name,
                                               'File_Path' : os.path.join(self.fpaths['simulation'],model_name),
                                               'Description' : description,
                                               'Main_File' : '',
                                               'Input_Files' : [],
                                               'Requirements' : [],
                                               'Objects' : []}

        # Make folder
        new_fpath = self.data['simulation'][model_name]['File_Path']
        os.makedirs(new_fpath, exist_ok=True)


        # Copy main.inp with new name
        new_main_name = model_name.upper()+'.inp'
        copy_input_file(os.path.join(self.fpaths['model_files'], 'MAIN.inp'), os.path.join(new_fpath, new_main_name), follow_symlinks=True)
        self.data['simulation'][model_name]['Main_File'] = new_main_name
        self.data['simulation'][model_name]['Input_Files'].append(new_main_name)
        print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(new_main_name, new_fpath, self.fpaths['model_files']))
        print('-----------------------------------------------')



        # Select Analysis
        analysis_name,_ = self.select_object('analysis', message=' for the model: "{}" to be built'.format(model_name))

        # Get old file path of analysis
        fpath = self.data['analysis'][analysis_name]['File_Path']

        # Update local dictionary to add analysis information
        self.data['simulation'][model_name]['Objects'].append(analysis_name)
        self.data['simulation'][model_name]['Requirements'] = self.data['analysis'][analysis_name]['Requirements']

        # Get *.inp files as list from analysis filepath
        files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

        # Copy *.inp files to new file path
        for file in files_to_copy:

            file_name = file.split('\\')[-1]

            self.data['simulation'][model_name]['Input_Files'].append(file_name[:-4].upper()+'.inp')

            try:
                copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))

            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))



        # Select Geometry
        geometry_name,_ = self.select_object('geometry', message=' for the model: "{}" to be built'.format(model_name))

        # Get old file path
        fpath = self.data['geometry'][geometry_name]['File_Path']

        # Update local dictionary to add analysis information
        self.data['simulation'][model_name]['Objects'].append(geometry_name)

        # Get *.inp files as list from analysis filepath
        files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

        # Copy *.inp files to new file path
        for file in files_to_copy:

            file_name = file.split('\\')[-1]

            self.data['simulation'][model_name]['Input_Files'].append(file_name[:-4].upper()+'.inp')

            try:
                copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))

            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))



        # Select solid material
        material_name,_ = self.select_object('material', message=' for the model: "{}" to be built. (Note: this is the solid material)'.format(model_name))

        # Get old file path
        fpath = self.data['material'][material_name]['File_Path']

        # Update local dictionary to add analysis information
        self.data['simulation'][model_name]['Objects'].append(material_name)

        # Get *.inp files as list from analysis filepath
        files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

        # Copy *.inp files to new file path
        for file in files_to_copy:

            file_name = file.split('\\')[-1]

            self.data['simulation'][model_name]['Input_Files'].append(file_name[:-4].upper()+'.inp')

            try:
                copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))

            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))



        fluid_required = True

        # Select fluid material
        if fluid_required:
            material_name,_ = self.select_object('material', message=' for the model: "{}" to be built. (Note: this is the fluid material)'.format(model_name))

            # Get old file path
            fpath = self.data['material'][material_name]['File_Path']

            # Update local dictionary to add analysis information
            self.data['simulation'][model_name]['Objects'].append(material_name)

            # Get *.inp files as list from analysis filepath
            files_to_copy = glob.glob(os.path.join(fpath,'*.inp'))

            # Copy *.inp files to new file path
            for file in files_to_copy:

                file_name = file.split('\\')[-1]

                self.data['simulation'][model_name]['Input_Files'].append(file_name[:-4].upper()+'.inp')

                try:
                    copy_input_file(file, os.path.join(new_fpath, file_name[:-4].upper()+'.inp'), follow_symlinks=True)
                    print('The file: "{}" has been successfully duplicated to the filepath: "{}" from "{}".'.format(file_name[:-4].upper()+'.inp',new_fpath, fpath))

                except:
                    raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name[:-4].upper()+'.inp'))


    def modify_model(self):
        '''
        
        '''
        pass
    

    def duplicate_model(self):
        '''
        
        '''
        pass
    

    def delete_model(self):
        '''
        
        '''
        pass

        '''
        
        '''
        pass
    

    def postprocess_model(self, model_name):
        '''
        
        '''
        pass


    def run_model(self, model_name):
        '''
        
        '''
        pass 


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


    def validate(self):
        '''
        
        '''
        pass


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
        for analysis in self.data['analysis'].values():

            # Get input files
            fpath = os.path.join(analysis['File_Path'],'*.inp')
            input_files = [x.split('\\')[-1] for x in glob.glob(fpath)]

            print('Analysis Name: "{}'.format(analysis['Name']))
            print('\tPath: "{}"'.format(analysis['File_Path']))
            print('\tDescription: "{}"'.format(analysis['Description']))
            print('\tRequirements: "{}"'.format(analysis['Requirements']))
            print('\tInput Files: "{}"'.format(input_files))
            print('\tFluid Required: "{}"'.format(analysis['Fluid_Required']))
            print('-----------------------------------------------')

        print('The Geometries currently loaded are: ')
        print('-----------------------------------------------')
        for geometry in self.data['geometry'].values():

            # Get input files
            fpath = os.path.join(geometry['File_Path'],'*.inp')
            input_files = [x.split('\\')[-1] for x in glob.glob(fpath)]

            print('Geometry Name: "{}'.format(geometry['Name']))
            print('\tPath: "{}"'.format(geometry['File_Path']))
            print('\tDescription: "{}"'.format(geometry['Description']))
            print('\tRequirements: "{}"'.format(geometry['Requirements']))
            print('\tInput Files: "{}"'.format(input_files))
            print('-----------------------------------------------')


        print('The Materials currently loaded are: ')
        print('-----------------------------------------------')
        for material in self.data['material'].values():

            # Get input files
            fpath = os.path.join(material['File_Path'],'*.inp')
            input_files = [x.split('\\')[-1] for x in glob.glob(fpath)]

            print('Material Name: "{}'.format(material['Name']))
            print('\tPath: "{}"'.format(material['File_Path']))
            print('\tDescription: "{}"'.format(material['Description']))
            print('\tRequirements: "{}"'.format(material['Requirements']))
            print('\tInput Files: "{}"'.format(input_files))
            print('-----------------------------------------------')

        for model in self.data['simulation'].values():
            print('Model Name: "{}'.format(model['Name']))
            print('\tPath: "{}"'.format(model['File_Path']))
            print('\tDescription: "{}"'.format(model['Description']))
            print('\tMain File: "{}"'.format(model['Main_File']))
            print('\tRequirements: "{}"'.format(model['Requirements']))
            print('\tInput Files: "{}"'.format(model['Input_Files']))
            print('\tObjects : "{}"'.format(model['Objects']))
            print('-----------------------------------------------')


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


    def print_model_help_message(self):
        '''
        
        '''
        pass