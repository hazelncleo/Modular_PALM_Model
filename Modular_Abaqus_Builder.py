import glob
import os
import string
import inquirer
from shutil import rmtree
import pickle as pkl
from copy import deepcopy
from sys import exit
import json
from shutil import copyfileobj

from Analysis_Object import Analysis_Object
from Geometry_Object import Geometry_Object
from Material_Object import Material_Object
from Model import Model

from HazelsAwesomeTheme import red_text,green_text,blue_text,yellow_text
from HazelsAwesomeTheme import HazelsAwesomeTheme as Theme




class Modular_Abaqus_Builder:
    def __init__(self, delete_database=False, delete_all_models=False):
        '''
        ---------------------------------------------------
        Initialise the class and load the data from the .pkl file.
        ---------------------------------------------------
        '''
        
        # Create base database
        self.instantiate_database()
        
        # If delete_database flag set to true, delete all files
        if delete_database:
            print(red_text('DELETE DATABASE FLAG SET TO TRUE'))
            print('-'*60)

            if self.yes_no_question('Are you sure you would like to delete the' + red_text(' entire ') + 'database'):
                self.delete_database()

            else:
                print('-'*60)
                print(yellow_text('The delete flag was set to true, but the delete was denied. Closing the database.'))
                print('-'*60)

                exit(0)

        # If delete_all_models flag set to true, delete all model files
        elif delete_all_models:
            print(red_text('DELETE MODELS FLAG SET TO TRUE'))
            print('-'*60)

            if self.yes_no_question('Are you sure you would like to delete ' + red_text('all models') + ' in the database?'):
                print('-'*60)

                try:
                    self.load_database()
                except:
                    print(yellow_text('The data.pkl file: "{}" does not exist. An empty Modular_Abaqus_Builder has been loaded.'.format(self.fpaths['data'])))
                    print('-'*60)

                self.delete_all_models()
                self.print_database(False)
                print('-'*60)
            
            else:
                print('-'*60)
                print(yellow_text('The delete models flag was set to true, but the delete was denied. Closing the database.'))
                print('-'*60)

                exit(0)

        # Otherwise load database as usual
        else:

            # Load data from data.pickle
            try:
                self.load_database()

                self.print_database(False)
                print('-'*60)

            # If it doesnt exist load an empty Modular_Abaqus_Builder
            except:
                
                print(yellow_text('The data.pkl file: "{}" does not exist. An empty Modular_Abaqus_Builder has been loaded.'.format(self.fpaths['data'])))
                print('-'*60)        

        self.save_database()
    

    def instantiate_database(self):
        '''
        ---------------------------------------------------
        Instantiate an empty database
        ---------------------------------------------------
        '''
        print('-'*60)
        print(green_text('Instantiating the Database'))
        print('-'*60)

        # Try to load the base_data .json
        try:
            with open('base_data.json') as f_load:
                base_data = json.load(f_load)

            self.fpaths = base_data['fpaths']

            self.requirements = base_data['requirements']

            self.allowed_characters = {key : set(value) for key, value in base_data['allowed_characters'].items()}

            self.inquirer_dialogs = base_data['inquirer_dialogs']

            self.data = base_data['data']

            print(green_text('Database Instantiated from "base_data.json".'))


        except:

            print(red_text('Loading the base database information failed, using base information in program instead'))
            print(red_text('Note, that preferably a "base_data.json" should be created by the user.'))

            # Set filepaths
            objectfiles_fpath = 'object_files'
            self.fpaths = {'object_files' : objectfiles_fpath,
                        'analysis' : os.path.join(objectfiles_fpath, 'analysis'),
                        'geometry' : os.path.join(objectfiles_fpath, 'geometry'),
                        'material': os.path.join(objectfiles_fpath, 'material'),
                        'model_files': 'model_files',
                        'data': 'data.pickle'}
            
            # Set requirements
            self.requirements = {"softwares": {
                                    "abaqus": False,
                                    "fluent": False,
                                    "mpcci": False
                                },
                                "geometries": {
                                    "assembly" : False,
                                    "abaqus_whole-chip_solid": False,
                                    "abaqus_whole-chip_acoustic": False,
                                    "abaqus_submodel_solid": False,
                                    "abaqus_submodel_acoustic": False,
                                    "fluent_whole-chip_fluid": False,
                                    "fluent_submodel_fluid": False
                                },
                                "materials": {
                                    "abaqus_solid": False,
                                    "abaqus_acoustic": False
                                },
                                "analysis": {
                                    "abaqus_global_odb": False,
                                    "abaqus_global_prt": False}}

            # Set allowed characters
            self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'),
                                       'Description' : set(string.ascii_letters + string.digits + '_-,.! ()[]')}
            
            # Set inquirer dialog lists
            self.inquirer_dialogs = {'Object_Types' : ['analysis','geometry','material'],
                                    'Main_Loop' : ['edit_objects', 'edit_models', 'save_database', 'validate_database', 'help', 'exit'],
                                    'Object_Loop' : ['create', 'modify', 'duplicate', 'delete', 'help', 'back'],
                                    'Model_Loop' : ['create', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']}
        
            self.data = {'analysis': {}, 'geometry': {}, 'material': {}, 'model': {}}


        # Make storage folders if they dont exist
        if not os.path.exists(self.fpaths['analysis']):
            os.makedirs(self.fpaths['analysis'], exist_ok=True)
            print(yellow_text('Analysis objects fpath did not exist, one has been created'))
        
        if not os.path.exists(self.fpaths['geometry']):
            os.makedirs(self.fpaths['geometry'], exist_ok=True)
            print(yellow_text('Geometry objects fpath did not exist, one has been created'))

        if not os.path.exists(self.fpaths['material']):
            os.makedirs(self.fpaths['material'], exist_ok=True)
            print(yellow_text('Material objects fpath did not exist, one has been created'))

        if not os.path.exists(self.fpaths['model_files']):
            os.makedirs(self.fpaths['model_files'], exist_ok=True)
            print(yellow_text('Model fpath did not exist, one has been created'))

        print(green_text('Instantiated the Database Successfully.'))
        print('-'*60)
        

    def delete_database(self):
        '''
        ---------------------------------------------------
        Delete all objects and models in the relevant filepaths
        ---------------------------------------------------
        '''
        print('-'*60)
        print(green_text('Deleting the Database'))
        print('-'*60)
        
        try:
            # Delete all analysis object files
            for analysis in glob.glob(os.path.join(self.fpaths['analysis'], '*', ''), recursive=False):
                rmtree(analysis)
                print(red_text('Deleted: "{}"'.format(analysis)))

            # Delete all geometry object files
            for geometry in glob.glob(os.path.join(self.fpaths['geometry'], '*', ''), recursive=False):
                rmtree(geometry)
                print(red_text('Deleted: "{}"'.format(geometry)))

            # Delete all material object files
            for material in glob.glob(os.path.join(self.fpaths['material'], '*', ''), recursive=False):
                rmtree(material)
                print(red_text('Deleted: "{}"'.format(material)))

            # Delete all model files
            for model in glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False):
                rmtree(model)
                print(red_text('Deleted: "{}"'.format(model)))

            if os.path.exists(self.fpaths['data']):
                # Delete pickle storage file
                os.remove(self.fpaths['data'])
                print(red_text('Deleted: "{}"'.format(self.fpaths['data'])))

            print('-'*60)
            print(green_text('The Database was successfully deleted.'))
            print('-'*60)

        except:
            print(red_text('ERROR: The program cannot delete a file due to another program using a directory.'))
            print(red_text('Closing the Database.'))
            print('-'*60)

            exit(0)


    def delete_all_models(self):
        '''
        ---------------------------------------------------
        Delete all models in the relevant filepaths and removes their entries from the database
        ---------------------------------------------------
        '''
        directories = glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False)
        model_names = self.data['model'].keys()

        print(green_text('Deleting all models in the database'))

        if not (len(directories) or len(model_names)):
            print(green_text('No Models to delete'))
            print('-'*60)
            return
        
        print('-'*60)

        try:
            for model in directories:
                rmtree(model)
                print(red_text('Deleted directory: "{}"'.format(model)))

            for model in model_names:
                print(red_text('Deleted Model: "{}", from the database.'.format(model)))

            self.data['model'] = {}

        except:
            print(red_text('ERROR: The program cannot delete a file due to another program using a directory.'))
            print(red_text('Closing the Database.'))
            print('-'*60)

            exit(0)


    def load_database(self):
        '''
        ---------------------------------------------------
        Load the database from the .pkl file
        ---------------------------------------------------
        '''
        with open(self.fpaths['data'], 'rb') as df:
            

            self.data = pkl.load(df).data

            print(green_text('Loading from: "{}" was successful.'.format(self.fpaths['data'])))
            print('-'*60)


    def save_database(self):
        '''
        ---------------------------------------------------
        Saves the database to a .pkl file
        ---------------------------------------------------
        '''

        if not os.path.exists(self.fpaths['data']):
            print(yellow_text('New "{}" file created'.format(self.fpaths['data'])))

        # Save data
        try:
            with open(self.fpaths['data'], 'wb') as df:
                pkl.dump(self, df)
                print(green_text('Save to: "{}" was successful.'.format(self.fpaths['data'])))

        except:
            print(red_text('ERROR: Save to: "{}" was unsuccessful.'.format(self.fpaths['data'])))
            print('-'*60)


    def main_loop(self):
        '''
        ---------------------------------------------------
        Main loop that controls the tui of the database
        ---------------------------------------------------
        '''
        command = 'edit_objects'

        while True:
            
            print('-'*60)
            # Commands = ['edit_objects', 'edit_models', 'save_database', 'validate_database', 'help', 'exit']
            main_loop_questions = [inquirer.List('command', 
                                       'Pick Command', 
                                       choices=self.inquirer_dialogs['Main_Loop'], 
                                       carousel=True, 
                                       default=command)]
            
            command = inquirer.prompt(main_loop_questions, theme=Theme())['command']

            if command == 'exit':
                print('-'*60)
                if self.yes_no_question('Are you sure you would like to exit?'):
                    print('-'*60)
                    self.save_database()
                    break

            elif command == 'help':
                help_questions = [inquirer.List('help_command', 
                                             'Select help option', 
                                             choices=['print','verbose_print','help','cancel'], 
                                             carousel = True)]
                
                print('-'*60)
                help_command = inquirer.prompt(help_questions, theme=Theme())['help_command']

                if help_command != 'cancel':
                    print('-'*60)
                    if help_command == 'print':
                        self.print_database()
                    elif help_command == 'verbose_print':
                        self.print_database(True)
                    elif help_command == 'help':
                        self.print_main_help_message()

            elif command == 'save_database':
                print('-'*60)
                self.save_database()

            elif command == 'edit_models':
                self.edit_models()
                
            elif command == 'edit_objects':
                self.edit_objects()

            elif command == 'validate_database':
                self.validate_database()


        print(green_text('Exiting the interface'))
        print('-'*60)


    def edit_objects(self):
        '''
        ---------------------------------------------------
        Main loop for editing objects in the database
        ---------------------------------------------------
        '''

        print('-'*60)
        print('Entering Edit Objects interface')
        print('-'*60)

        command = 'create'

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'help', 'back']
            object_questions = [inquirer.List('command',
                                       'Pick Edit Object Command', 
                                       choices=self.inquirer_dialogs['Object_Loop'], 
                                       carousel = True, 
                                       default = command)]
            
            command = inquirer.prompt(object_questions, theme=Theme())['command']

            if command == 'help':
                help_questions = [inquirer.List('help_command', 
                                             'Select help option', 
                                             choices=['print','verbose_print','help','cancel'], 
                                             carousel = True)]
                
                print('-'*60)
                help_command = inquirer.prompt(help_questions, theme=Theme())['help_command']

                if help_command != 'cancel':
                    print('-'*60)

                    if help_command == 'print':
                        self.print_database()
                        print('-'*60)

                    elif help_command == 'verbose_print':
                        self.print_database(True)
                        print('-'*60)

                    elif help_command == 'help':
                        self.print_main_help_message()


            elif command == 'create':
                
                print('-'*60)
                object_type = self.select_object_type()

                self.create_object(object_type)

                self.save_database()
                print('-'*60)


            elif command == 'modify':
                
                print('-'*60)
                object_name, object_type = self.select_object()
                
                # Check if object was available
                if object_name:

                    self.modify_object(object_name, object_type)
                    
                    self.save_database()
                    print('-'*60)

                else: 
                    print('Returning to object loop.')
                    print('-'*60)

            elif command == 'duplicate':

                print('-'*60)
                object_name, object_type = self.select_object()

                # Check if object was available
                if object_name:

                    # Duplicate the object to a new name
                    self.duplicate_object(object_type, object_name)

                    self.save_database()
                    print('-'*60)

                else: 
                    print('Returning to object loop.')
                    print('-'*60)


            elif command == 'delete':
                
                print('-'*60)
                object_name, object_type = self.select_object(message = ' you would like to delete')

                # Check if object was available
                if object_name:

                    # Delete the object
                    self.delete_object(object_type, object_name)

                    self.save_database()
                    print('-'*60)

                else: 
                    print('Returning to object loop.')
                    print('-'*60)

        print('-'*60)
        print('Returning to the main loop')
        

    def edit_models(self):
        '''
        ---------------------------------------------------
        Main loop for editing models in the database
        ---------------------------------------------------
        '''

        print('-'*60)
        print('Entering edit models interface')
        print('-'*60)
        
        command = 'create'

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']
            model_questions = [inquirer.List('command',
                                             'Pick Model Edit Command: ', 
                                             choices=self.inquirer_dialogs['Model_Loop'], 
                                             carousel = True, 
                                             default = command)]
            
            command = inquirer.prompt(model_questions, theme=Theme())['command']

            if command == 'help':
                help_questions = [inquirer.List('help_command', 
                                             'Select help option', 
                                             choices=['print','verbose_print','help','cancel'], 
                                             carousel = True)]
                
                print('-'*60)
                help_command = inquirer.prompt(help_questions, theme=Theme())['help_command']

                if help_command != 'cancel':
                    print('-'*60)
                    if help_command == 'print':
                        self.print_database()
                        print('-'*60)
                    elif help_command == 'verbose_print':
                        self.print_database(True)
                        print('-'*60)
                    elif help_command == 'help':
                        self.print_main_help_message()

            elif command == 'create':
                self.create_model()

                self.save_database()
                print('-'*60)

            elif command == 'modify':
                self.modify_model()

                self.save_database()
                print('-'*60)

            elif command == 'duplicate':
                self.duplicate_model()

                self.save_database()
                print('-'*60)

            elif command == 'delete':
                self.delete_model()

                self.save_database()
                print('-'*60)

            elif command == 'post_process':
                self.postprocess_model()
                
                self.save_database()
                print('-'*60)

            elif command == 'run':
                self.run_model()

                self.save_database()
                print('-'*60)

        print('-'*60)
        print('Returning to the main loop')

        
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
        questions = [inquirer.List('object_type','Pick Object Type: ', choices=self.inquirer_dialogs['Object_Types'], carousel = True)]
        object_type = inquirer.prompt(questions, theme=Theme())['object_type']

        print('-'*60)
        print('Object Type: "{}" was selected.'.format(blue_text(object_type)))

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
            print('-'*60)

        # Get available choices
        choices = list(self.data[object_type].keys())

        # Check there are choices available
        if choices:
            
            questions = [inquirer.List('object','Pick the {} object{}'.format(object_type,message), choices=choices, carousel = True)]
            selected_object = inquirer.prompt(questions, theme=Theme())['object']
            
            print('-'*60)
            print('Object: "{}" of object type: "{}" was selected.'.format(blue_text(selected_object),blue_text(object_type)))
            print('-'*60)
            
            return selected_object, object_type

        else:

            print(red_text('ERROR: no objects of type: "{}" to select.'.format(object_type)))
            print('-'*60)
            return '', object_type


    def get_object_modifications(self, object_name, object_type):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_name : str


        object_type : str, [analysis/geometry/material]
            
        ---------------------------------------------------
        '''
        possible_changes = ['name', 'description', 'parameters', 'requirements', 'cancel']
        
        # Get objects to be changed
        questions = [inquirer.Checkbox('modifications','What would you like to change about the object: "{}", of type: "{}"'.format(object_name,object_type), choices = possible_changes)]
        modifications = inquirer.prompt(questions, theme=Theme())['modifications']

        # Create change dictionary
        object_modifications = {'name': False,
                                'description' : False,
                                'parameters' : False,
                                'requirements' : False}
        
        # If no changes picked or cancelled return to main loop
        if (not modifications) or ('cancel' in modifications):
            print('-'*60)
            print(yellow_text('No changes picked or cancel command picked'))
            print('-'*60)
            return object_modifications

        for modification_key in object_modifications.keys():
            object_modifications[modification_key] = modification_key in modifications

        return object_modifications
        

    def create_object(self, object_type):
        '''
        ---------------------------------------------------
        Creates a new object in the database with a specified object type
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of object to be added to the database. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.
        ---------------------------------------------------
        '''

        try:
            if object_type == 'analysis':
                
                temp_object = Analysis_Object(self)
                if not temp_object.name:
                    return
                
                self.data['analysis'][temp_object.name] = temp_object

            elif object_type == 'geometry':

                temp_object = Geometry_Object(self)
                if not temp_object.name:
                    return

                self.data['geometry'][temp_object.name] = temp_object

            elif object_type == 'material':

                temp_object = Material_Object(self)
                if not temp_object.name:
                    return
                
                self.data['material'][temp_object.name] = temp_object

            print(green_text('Object: "{}" successfully added to the database.'.format(temp_object.name)))
            print('-'*60)

        except:

            print(red_text('An error occurred while adding the object to the Database.'))
            for object_fpath in glob.glob(os.path.join(self.fpaths[object_type],'*',''), recursive=False):
                if object_fpath not in [os.path.join(object.fpath,'') for object in self.data[object_type].values()]:
                    rmtree(object_fpath)
                    print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(object_fpath)))

            print('-'*60)
            
    
    def modify_object(self, object_name, object_type):
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
        ---------------------------------------------------
        '''
        # Check the user would like to delete the object
        if not self.yes_no_question('Would you like to modify object: "{}" of type: "{}"'.format(object_name, object_type)):
            return

        print('Modify object operation begun.')
        print('-'*60)

        object_modifications = self.get_object_modifications(object_name, object_type)
        
        # Change name/file directory
        if object_modifications['name']:

            # Pick new name
            self.data[object_type][object_name].new_object_name()
            new_name = self.data[object_type][object_name].name

            self.data[object_type][new_name] = self.data[object_type].pop(object_name)

            print(green_text('Object name successfully changed from: "{}" to "{}".'.format(object_name, new_name)))

            # Change folder name
            try:
                fpath = os.path.join(self.fpaths[object_type], object_name)
                new_fpath = os.path.join(self.fpaths[object_type], new_name)
                os.rename(fpath, new_fpath)
                print(green_text('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath)))

            except:
                print('-'*60)
                print(red_text('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath)))

                self.validate_database()
            
            # Change fpath
            self.data[object_type][new_name].fpath = new_fpath
            print(green_text('The filepath for {} "{}" was successfully changed to "{}" in the database.'.format(object_type,new_name,new_fpath)))
            
            object_name = new_name

            print(green_text('Name modification was successful.'))


        # Change description
        if object_modifications['description']:
            self.data[object_type][object_name].new_description()
            print(green_text('Description modification was successful.'))


        # Change parameters
        if object_modifications['parameters']:
            self.data[object_type][object_name].define_parameters()
            print(green_text('Parameters modification was successful.'))
            
        # Change requirements
        if object_modifications['requirements']:
            self.data[object_type][object_name].set_requirements()
            print(green_text('Requirements modification was successful.'))


        print(green_text('Modify object operation successful.'))
        print('-'*60)


    def duplicate_object(self, object_type, object_name):
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
        ---------------------------------------------------
        '''
        print(green_text('Duplicate object operation begun.'))
        print('-'*60)

        # Copy object and change its name
        duplicated_object = deepcopy(self.data[object_type][object_name])
        duplicated_object.builder = self
        duplicated_object.new_object_name()
        
        new_name = duplicated_object.name

        # Get new and old fpaths
        fpath = duplicated_object.fpath
        new_fpath = os.path.join(self.fpaths[object_type], new_name)
        duplicated_object.fpath = new_fpath

        # Check file path does not already exist
        if os.path.exists(new_fpath):
            print(red_text('ERROR: The filepath: "{}" already exists.'.format(new_fpath)))
            self.validate_database()
        else:
            self.data[object_type][new_name] = duplicated_object
            self.data[object_type][new_name].move_folder(fpath, new_fpath)  

            print(green_text('Duplicate object operation successful.'))
            print('-'*60)


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
        if not self.yes_no_question('Would you like to delete object: "{}" of type: "{}"'.format(object_name, object_type)):
            return
        
        print('-'*60)
        print(green_text('Attempting to Delete {} object: "{}"'.format(object_type, object_name)))

        # Get file path of files
        fpath = os.path.join(self.fpaths[object_type], object_name)
        
        # Delete files from filepath
        try:
            rmtree(fpath)
            print(green_text('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type)))

            # Then delete from local dictionary
            self.data[object_type].pop(object_name)
            print(green_text('The {}: "{}" has been successfully removed from the local dictionary.'.format(object_type,object_name)))     
            
            print(green_text('Delete object operation successful.'))
            print('-'*60)
        except:
            print(red_text('ERROR: The object could not be deleted.'))
            print('-'*60)
            self.validate_database()
            
        
    def print_database(self, verbose = False):
        '''
        ---------------------------------------------------
        Print Database in a cooler way than __str__. Hate that shit.
        ---------------------------------------------------
        '''

        print(blue_text('The Analyses currently loaded are: '))
        print('-'*60)
        for analysis in self.data['analysis'].values():

            print('Analysis Name: "{}"'.format(blue_text(analysis.name)))
            verbose and print('\tPath: "{}"'.format(analysis.fpath))
            print('\tDescription: "{}"'.format(analysis.description))
            
            if verbose:
                print('\tFiles: ')
                for file in analysis.files:
                    print('\t\t"{}"'.format(file))

            if len(analysis.parameters):
                print('\tParameters: ')
                for parameter in analysis.parameters.keys():
                    print('\t\tName: "{}"'.format(analysis.parameters[parameter]['name']))
                    verbose and print('\t\t\tDescription: "{}"'.format(analysis.parameters[parameter]['description']))
                    print('\t\t\tDefault Value: "{}"'.format(analysis.parameters[parameter]['default_value']))
                    verbose and print('\t\t\tData-type: "{}"'.format(analysis.parameters[parameter]['dtype']))

                    if verbose:
                        print('\t\t\tSolvers parameter modifies: ')
                        for solver in analysis.parameters[parameter]['solvers']:
                                print('\t\t\t\t"{}"'.format(solver))

            if verbose:
                print('\tRequirements: ')
                for requirement_type in analysis.requirements.keys():
                    print('\t\t"{}"'.format(requirement_type))
                    for requirement,requirement_value in analysis.requirements[requirement_type].items():
                        print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-'*60)

        
        print(blue_text('The Geometries currently loaded are: '))
        print('-'*60)
        for geometry in self.data['geometry'].values():

            print('Geometry Name: "{}"'.format(blue_text(geometry.name)))
            verbose and print('\tPath: "{}"'.format(geometry.fpath))
            print('\tDescription: "{}"'.format(geometry.description))

            if verbose:
                print('\tFiles: ')
                for file in geometry.files:
                    print('\t\t"{}"'.format(file))

            if len(geometry.parameters):
                print('\tParameters: ')
                for parameter in geometry.parameters.keys():
                    print('\t\tName: "{}"'.format(geometry.parameters[parameter]['name']))
                    verbose and print('\t\t\tDescription: "{}"'.format(geometry.parameters[parameter]['description']))
                    print('\t\t\tDefault Value: "{}"'.format(geometry.parameters[parameter]['default_value']))
                    verbose and print('\t\t\tData-type: "{}"'.format(geometry.parameters[parameter]['dtype']))
                    
                    if verbose:
                        print('\t\t\tSolvers parameter modifies: ')
                        for solver in geometry.parameters[parameter]['solvers']:
                                print('\t\t\t\t"{}"'.format(solver))

            if verbose:
                print('\tRequirements: ')
                for requirement_type in geometry.requirements.keys():
                    print('\t\t"{}"'.format(requirement_type))
                    for requirement,requirement_value in geometry.requirements[requirement_type].items():
                        print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-'*60)


        print(blue_text('The Materials currently loaded are: '))
        print('-'*60)
        for material in self.data['material'].values():

            print('Material Name: "{}"'.format(blue_text(material.name)))
            verbose and print('\tPath: "{}"'.format(material.fpath))
            print('\tDescription: "{}"'.format(material.description))

            if verbose:
                print('\tFiles: ')
                for file in material.files:
                    print('\t\t"{}"'.format(file))

            if len(material.parameters):
                print('\tParameters: ')
                for parameter in material.parameters.keys():

                    print('\t\tName: "{}"'.format(material.parameters[parameter]['name']))
                    verbose and print('\t\t\tDescription: "{}"'.format(material.parameters[parameter]['description']))
                    print('\t\t\tDefault Value: "{}"'.format(material.parameters[parameter]['default_value']))
                    verbose and print('\t\t\tData-type: "{}"'.format(material.parameters[parameter]['dtype']))
                    
                    if verbose:
                        print('\t\t\tSolvers parameter modifies: ')
                        for solver in material.parameters[parameter]['solvers']:
                                print('\t\t\t\t"{}"'.format(solver))

            if verbose:
                print('\tRequirements: ')
                for requirement_type in material.requirements.keys():
                    print('\t\t"{}"'.format(requirement_type))
                    for requirement,requirement_value in material.requirements[requirement_type].items():
                        print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-'*60)


        # ******************* TODO WILL NEED TO BE UPDATED UPON ADDING MODEL CLASS *************************

        print(blue_text('The Models currently loaded are: '))
        print('-'*60)
        for model in self.data['model'].values():

            print('Model Name: "{}"'.format(blue_text(model.name)))
            print('\tDescription: "{}"'.format(model.description))
            verbose and print('\tPath: "{}"'.format(model.fpath))

            if verbose:
                print('\tSolver Fpaths: ')
                for solver,fpath in model.solver_fpaths.items():
                    if fpath is not None:
                        print('\t\t "{}": "{}"'.format(solver,fpath))

            print('\tAnalysis used: "{}"'.format(model.analysis.name))

            if verbose:
                print('\tWhich has requirements: ')
                for requirement_type in model.requirements.keys():
                    print('\t\t"{}"'.format(requirement_type))
                    for requirement,requirement_value in model.requirements[requirement_type].items():
                        print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('\tGeometry used: "{}"'.format(model.geometry.name))

            if len(model.materials) > 1:
                print('\tMaterials used: ')
                for material in model.materials.keys():
                    print('\t\t"{}"'.format(model.materials[material].name))

            elif len(model.materials) == 1:
                for material in model.materials.keys():
                    print('\tMaterial used: "{}"'.format(model.materials[material].name))

            if len(model.parameters):
                print('\tParameters: ')
                for parameter in model.parameters.keys():

                    print('\t\tName: "{}"'.format(model.parameters[parameter]['name']))
                    verbose and print('\t\t\tDescription: "{}"'.format(model.parameters[parameter]['description']))
                    print('\t\t\tDefault Value: "{}"'.format(model.parameters[parameter]['default_value']))
                    verbose and print('\t\t\tData-type: "{}"'.format(model.parameters[parameter]['dtype']))
                    

                    if verbose:
                        print('\t\t\tSolvers parameter modifies: ')
                        for solver in model.parameters[parameter]['solvers']:
                                print('\t\t\t\t"{}"'.format(solver))


        print('Database contains:')
        print('\t{} Analysis Objects'.format(blue_text(len(self.data['analysis']))))
        print('\t{} Geometry Objects'.format(blue_text(len(self.data['geometry']))))
        print('\t{} Material Objects'.format(blue_text(len(self.data['material']))))
        print('\t{} Models'.format(blue_text(len(self.data['model']))))


    def validate_database(self):
        '''
        
        '''
        print('-'*60)
        print('Validating the Database to ensure no corruption has occured.')
        print('-'*60)

        # Validate Analyses
        print('Validating Analyses...')
        print('-'*60)
        for analysis_name in list(self.data['analysis'].keys()):
            
            print('\tValidating Analysis: "{}"'.format(analysis_name))

            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['analysis'],analysis_name) == self.data['analysis'][analysis_name].fpath


            # Check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['analysis'],analysis_name))


            # Check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['analysis'],analysis_name,file_to_check)) for file_to_check in self.data['analysis'][analysis_name].files])


            # Check requirements match database requirements
            if (self.requirements.keys() != self.data['analysis'][analysis_name].requirements.keys()) or any([self.requirements[key].keys() != self.data['analysis'][analysis_name].requirements[key].keys() for key in self.requirements.keys()]):

                print(yellow_text('\tThe requirements for the Analysis object: "{}" do not match the default requirements of the database. Please select new requirements.'.format(analysis_name)))
                self.data['analysis'][analysis_name].set_requirements(reset_requirements = True)


            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print(green_text('\tAnalysis: "{}", validated successfully'.format(analysis_name)))

            else:
                self.data['analysis'].pop(analysis_name)
                print(red_text('\tAnalysis: "{}", was found to be not valid. Deleting from database'.format(analysis_name)))

        bool(len(self.data['analysis'])) and print('-'*60)
        print(green_text('Analyses Validated.'))
        print('-'*60)


        # Validate Geometries
        print('Validating Geometries...')
        print('-'*60)
        for geometry_name in list(self.data['geometry'].keys()):
            
            print('\tValidating Geometry: "{}"'.format(geometry_name))

            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['geometry'],geometry_name) == self.data['geometry'][geometry_name].fpath


            # Check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['geometry'],geometry_name))


            # Check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['geometry'],geometry_name,file_to_check)) for file_to_check in self.data['geometry'][geometry_name].files])


            # Check requirements match database requirements
            if self.requirements['geometries'].keys() != self.data['geometry'][geometry_name].requirements['geometries'].keys():

                print(yellow_text('\tThe requirements for the Geometry object: "{}" do not match the default requirements of the database.'.format(geometry_name)))
                self.data['geometry'][geometry_name].set_requirements(reset_requirements = True)


            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print(green_text('\tGeometry: "{}", validated successfully'.format(geometry_name)))

            else:
                self.data['geometry'].pop(geometry_name)
                print(red_text('\tGeometry: "{}", was found to be not valid. Deleting from database'.format(geometry_name)))

        bool(len(self.data['geometry'])) and print('-'*60)
        print(green_text('Geometries Validated.'))
        print('-'*60)


        # Validate Materials
        print('Validating Materials...')
        print('-'*60)
        for material_name in list(self.data['material'].keys()):
            
            print('\tValidating Material: "{}"'.format(material_name))


            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['material'],material_name) == self.data['material'][material_name].fpath


            # check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['material'],material_name))


            # check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['material'],material_name,file_to_check)) for file_to_check in self.data['material'][material_name].files])


            # check requirements match database requirements
            if self.requirements['materials'].keys() != self.data['material'][material_name].requirements['materials'].keys():

                print(yellow_text('\tThe requirements for the Material object: "{}" do not match the default requirements of the database.'.format(material_name)))
                self.data['material'][material_name].set_requirements(reset_requirements = True)

            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print(green_text('\tMaterial: "{}", validated successfully'.format(material_name)))

            else:
                self.data['material'].pop(material_name)
                print(red_text('\tMaterial: "{}", was found to be not valid. Deleting from database'.format(material_name)))

        bool(len(self.data['material'])) and print('-'*60)
        print(green_text('Materials Validated.'))
        print('-'*60)


        # Validate Models
        print('Validating Models...')
        print('-'*60)
        for model_name in list(self.data['model'].keys()):

            print('\tValidating Model: "{}"'.format(model_name))

            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['model_files'],model_name) == self.data['model'][model_name].fpath


            # check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['model_files'],model_name))


            # Check objects exist
            analysis_exists = self.data['model'][model_name].analysis.name in self.data['analysis']
            geometry_exists = self.data['model'][model_name].geometry.name in self.data['geometry'] 
            materials_exists = all([material_name in self.data['material'] for material_name in self.data['model'][model_name].materials.keys()])
            objects_exist = analysis_exists and geometry_exists and materials_exists
            
            if not objects_exist:
                objects_exist = not self.yes_no_question('One or more objects used in the model: "{}", no longer exist, Delete the model? (Note: keeping the model may cause an error in the future)'.format(model_name))


            # Check requirements match database requirements
            if (self.requirements.keys() != self.data['model'][model_name].requirements.keys()) or any([self.requirements[key].keys() != self.data['model'][model_name].requirements[key].keys() for key in self.requirements.keys()]):

                print(yellow_text('\tThe requirements for the Model: "{}" do not match the default requirements of the database.'.format(model_name)))

                if analysis_exists:
                    self.data['model'][model_name].requirements = self.data['model'][model_name].analysis.requirements
                    requirements_valid = True
                else:
                    requirements_valid = False
            else:
                requirements_valid = True


            # Check all validations passed
            if fpath_matches and directory_exists and objects_exist and requirements_valid:
                print(green_text('\tModel: "{}", validated successfully'.format(model_name)))

            else:
                self.data['model'].pop(model_name)
                print(red_text('\tModel: "{}", was found to be not valid. Deleting from database'.format(model_name)))

        bool(len(self.data['model'])) and print('-'*60)
        print(green_text('Models Validated.'))
        print('-'*60)


        print('Validating File Paths...')
        print('-'*60)
        check_deleted = False
        # Delete any folders not connected to objects in the database
        for analysis_fpath in glob.glob(os.path.join(self.fpaths['analysis'],'*',''), recursive=False):
            if analysis_fpath not in [os.path.join(analysis.fpath,'') for analysis in self.data['analysis'].values()]:
                rmtree(analysis_fpath)
                print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(analysis_fpath)))
                check_deleted = True
                
        
        for geometry_fpath in glob.glob(os.path.join(self.fpaths['geometry'],'*',''), recursive=False):
            if geometry_fpath not in [os.path.join(geometry.fpath,'') for geometry in self.data['geometry'].values()]:
                rmtree(geometry_fpath)
                print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(geometry_fpath)))
                check_deleted = True


        for material_fpath in glob.glob(os.path.join(self.fpaths['material'],'*',''), recursive=False):
            if material_fpath not in [os.path.join(material.fpath,'') for material in self.data['material'].values()]:
                rmtree(material_fpath)
                print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(material_fpath)))
                check_deleted = True


        for model_fpath in glob.glob(os.path.join(self.fpaths['model_files'],'*',''), recursive=False):
            if model_fpath not in [os.path.join(model.fpath,'') for model in self.data['model'].values()]:
                rmtree(model_fpath)
                print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(model_fpath)))
                check_deleted = True

        
        for extra_object_fpath in glob.glob(os.path.join(self.fpaths['object_files'],'*',''), recursive=False):
            if extra_object_fpath not in [os.path.join(self.fpaths["analysis"],''),os.path.join(self.fpaths['geometry'],''),os.path.join(self.fpaths['material'],'')]:
                rmtree(extra_object_fpath)
                print(red_text('\tDeleted Folder: "{}", that did not exist in the database.'.format(extra_object_fpath)))
                check_deleted = True

        check_deleted and print('-'*60)
        print(green_text('File Paths Validated.'))
        print('-'*60)
        print(green_text('Database Validation Successful.'))
    

    def yes_no_question(self, message):
        '''
        -----------------------------------------------
        Ask a yes/no question, "yes" returns True and "no" returns False
        -----------------------------------------------
        '''

        # Enquire the yes and no question using the final line as the message
        command = inquirer.prompt([inquirer.List('yes_no', message, choices=['yes','no'], carousel = True)], theme=Theme())['yes_no']

        if command == 'yes':
            return True 
        elif command == 'no':
            return False


    def get_relative_fpath(self, full_fpath, relative_to_fpath):
        '''
        
        '''
        if relative_to_fpath and full_fpath:

            full_fpath_list = os.path.normpath(full_fpath).split(os.path.sep)
            relative_to_fpath_list = os.path.normpath(relative_to_fpath).split(os.path.sep)
            
            for dir in relative_to_fpath_list:
                full_fpath_list.remove(dir)
                
            return os.path.join(*full_fpath_list)
        
        return full_fpath
        
        
    def delete_model(self):
        '''
        
        '''
        
        model_names = list(self.data['model'].keys())

        if model_names:
            
            print('-'*60)
            questions = [inquirer.List('model_to_delete','Please select the model you would like to delete from the database', choices = model_names+['cancel'], carousel = True)]
            model_to_delete = inquirer.prompt(questions, theme=Theme())['model_to_delete']

            if model_to_delete == 'cancel':
                print('-'*60)
                print('Delete model operation cancelled, returning to edit model loop')
                print('-'*60)

            try:
                # Delete folder
                rmtree(self.data['model'][model_to_delete].fpath)
                print('-'*60)
                print(green_text('Deleted Folder: "{}"'.format(self.data['model'][model_to_delete].fpath)))

                # Delete from database
                self.data['model'].pop(model_to_delete)
                print(green_text('Deleted model: "{}", from the database.'.format(model_to_delete)))
                print(green_text('{} Model Successfully Deleted.'.format(model_to_delete)))
                print('-'*60)

            except:
                print('-'*60)
                print(red_text('ERROR: Tried to delete the model: "{}", but could not. Check if the directory is open in another application.'.format(model_to_delete)))
                print(red_text('Try running the validate database command once the error has been rectified to ensure corruption does not occur.'))
                print('-'*60)

        else:
            print('-'*60)
            print(red_text('No models in database to delete, returning to edit model loop'))
            print('-'*60)   
        

    def create_model(self):
        '''
        Build model
        '''
        try:
            model = Model(self)
            
            self.data['model'][model.name] = model

        except:
            print('-'*60)
            print(red_text('Create Model Failed, validating database to ensure corruption does not occur.'))

            self.validate_database()
        

    def duplicate_model(self):
        '''
        
        '''
        model_names = list(self.data['model'].keys())

        if model_names:
            
            questions = [inquirer.List('model_to_duplicate','Please select the model you would like to duplicate from the database', choices = model_names+['cancel'], carousel = True)]
            model_to_duplicate = inquirer.prompt(questions, theme=Theme())['model_to_duplicate']

            if model_to_duplicate == 'cancel':
                print('-'*60)
                print(yellow_text('Duplicate model operation cancelled, returning to edit model loop'))
                print('-'*60)

            print('Model: "{}", chosen to be duplicated'.format(model_to_duplicate))

            # Try to copy the chosen model and then rebuild it from its base objects
            try:
                analysis_name = self.data['model'][model_to_duplicate].analysis.name
                geometry_name = self.data['model'][model_to_duplicate].geometry.name
                material_names = list(self.data['model'][model_to_duplicate].materials.keys())

                # Check that all the objects used to build the model to be duplicated still exist
                analysis_exists = analysis_name in self.data['analysis']
                geometry_exists = geometry_name in self.data['geometry'] 
                materials_exists = all([material_name in self.data['material'] for material_name in material_names])

                if analysis_exists and geometry_exists and materials_exists:

                    print(green_text('The Model: "{}", meets all the requirements for duplication.'.format(model_to_duplicate)))

                    duplicate_model = Model(self, analysis_name, geometry_name, material_names)

                    self.data['model'][duplicate_model.name] = duplicate_model

                    print(green_text('The Model: "{}", was successfully duplicated to the new Model: "{}".'.format(model_to_duplicate, duplicate_model.name)))
                    print('-'*60)

                else:
                    print('-'*60)
                    print(red_text('Tried to duplicate the model: "{}", and failed due to the previously used objects no longer existing.'.format(model_to_duplicate)))
                    print('-'*60)

            except:
                print('-'*60)
                print(red_text('Tried to duplicate the model: "{}", but could not. Check if the directory is open in another application.'.format(model_to_duplicate)))
                print(red_text('Validating database to ensure corruption does not occur.'))

                self.validate_database()


        else:
            print('-----------------------------------------------')
            print(red_text('No models in database to duplicate, returning to edit model loop'))
            print('-----------------------------------------------')
        
        






    def modify_model(self):
        '''
        
        '''
        model_names = list(self.data['model'].keys())

        if model_names:

            questions = [inquirer.List('model_name', 'Please select the model you would like to modify', choices = model_names+['cancel'], carousel = True)]
            model_name = inquirer.prompt(questions, theme=Theme())['model_name']

            if model_name == 'cancel':
                print('-'*60)
                print(yellow_text('Modify model operation cancelled, returning to edit model loop'))
                print('-'*60)
                return

            possible_changes = ['name', 'description', 'parameters', 'cancel']
        
            # Get Model changes
            questions = [inquirer.Checkbox('modifications','What would you like to change about the model: "{}".'.format(model_name), choices = possible_changes, carousel = True)]
            modifications = inquirer.prompt(questions, theme=Theme())['modifications']
            
            if ('cancel' in modifications) or not modifications:
                print('-'*60)
                print(yellow_text('Modify model operation cancelled, returning to edit model loop'))
                print('-'*60)
                return

            model_to_modify = self.data['model'].pop(name)

            if 'name' in modifications:

                # Set new name
                model_to_modify.new_model_name()
                old_name = name
                name = model_to_modify.name

                # Change fpath name
                try:
                    old_fpath = model_to_modify.fpath
                    new_fpath = os.path.join(self.fpaths['model_files'],name)
                    os.rename(old_fpath,new_fpath)
                    model_to_modify.fpath = new_fpath
                    model_to_modify.set_fpaths()

                    print(green_text('Renaming the filepath: "{}" to "{}" was successful.'.format(old_fpath,new_fpath)))

                except:
                    print('-'*60)
                    print(red_text('Renaming the filepath: "{}" to "{}" has failed.'.format(old_fpath,new_fpath)))

                    self.validate_database()
                    return
                
                # Change name of main sim file (and journal file contents for just fluent run)
                if all(model_to_modify.requirements['softwares'].values()):

                    # Rename mpcci model file
                    try:
                        os.rename(os.path.join(model_to_modify.solver_fpaths['mpcci'],old_name+'.csp'),os.path.join(model_to_modify.solver_fpaths['mpcci'],name+'.csp'))
                        print(green_text('Renaming the file: "{}" to "{}" was successful.'.format(old_name+'.csp',name+'.csp')))
                    except:
                        print('-'*60)
                        print(red_text('Renaming the file: "{}" to "{}" has failed.'.format(old_name+'.csp',name+'.csp')))
                        print(red_text('Please check the database entries and the files themselves to ensure corruption does not occur.'))

                        self.validate_database()
                        return
                
                elif model_to_modify.requirements['softwares']['abaqus']:

                    # Rename abaqus model file
                    try:
                        os.rename(os.path.join(model_to_modify.solver_fpaths['abaqus'],old_name+'.inp'),os.path.join(model_to_modify.solver_fpaths['abaqus'],name+'.inp'))
                        print(green_text('Renaming the file: "{}" to "{}" was successful.'.format(old_name+'.inp',name+'.inp')))
                    except:
                        print('-'*60)
                        print(red_text('Renaming the file: "{}" to "{}" has failed.'.format(old_name+'.inp',name+'.inp')))
                        print(red_text('Please check the database entries and the files themselves to ensure corruption does not occur.'))

                        self.validate_database()
                        return

                elif model_to_modify.requirements['softwares']['fluent']:

                    # Rename fluent model file
                    try:
                        os.rename(os.path.join(model_to_modify.solver_fpaths['fluent'],old_name+'.cas.h5'),os.path.join(model_to_modify.solver_fpaths['fluent'],name+'.cas.h5'))
                        print(green_text('Renaming the file: "{}" to "{}" was successful.'.format(old_name+'.cas.h5',name+'.cas.h5')))
                    except:
                        print('-'*60)
                        print(red_text('Renaming the file: "{}" to "{}" has failed.'.format(old_name+'.cas.h5',name+'.cas.h5')))
                        print(red_text('Please check the database entries and the files themselves to ensure corruption does not occur.'))

                        self.validate_database()
                        return

                    # Edit journal file to reference new .cas.h5 file
                    try:
                        
                        with open(os.path.join(model_to_modify.solver_fpaths['fluent'],'journal.jou'),'r') as old_file, open(os.path.join(model_to_modify.solver_fpaths['fluent'],'temp.jou'),'w') as new_file:

                            # Write new first two lines
                            new_file.write('\t; Read the case file\n')
                            new_file.write('\t/rc {}\n'.format(name+'.cas.h5'))

                            # Delete first two lines of old journal file
                            old_file.readline()
                            old_file.readline()

                            # Copy rest of journal file
                            copyfileobj(old_file,new_file)

                        # Overwrite old journal file
                        os.replace(os.path.join(model_to_modify.solver_fpaths['fluent'],'temp.jou'),os.path.join(model_to_modify.solver_fpaths['fluent'],'journal.jou'))
                        print(green_text('Updating the fluent journal file was successful.'))

                    except:
                        print('-'*60)
                        print(red_text('Updating the fluent journal file has failed.'))
                        print(red_text('Please check the database entries and the files themselves to ensure corruption does not occur.'))

                        self.validate_database()
                        return

                print(green_text('Name modification was successful.'))


            if 'description' in modifications:
                model_to_modify.new_description()
                print(green_text('Description modification was successful.'))


            if 'parameters' in modifications:
                pass # *************** TODO
                print(green_text('Parameter modification was successful.'))


            # Update database
            self.data['model'][name] = model_to_modify 
            print(green_text('Model: "{}", successfully modified.'.format(name)))
            print('-'*60)


        else:
            print(yellow_text('No models in database to modify, returning to edit model loop'))
            print('-'*60)   
    


    
    

    def postprocess_model(self):
        '''
        
        '''
        pass


    def run_model(self):
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
        Prints a help message for using the Edit Object text interface

        **********************************TODO***********************************
        ---------------------------------------------------
        '''


    def print_model_help_message(self):
        '''
        
        '''
        pass