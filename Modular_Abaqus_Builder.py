import glob
import os
import string
import inquirer
from shutil import rmtree
import pickle as pkl
from copy import deepcopy
from sys import exit
from Analysis_Object import Analysis_Object
from Geometry_Object import Geometry_Object
from Material_Object import Material_Object
from Model import Model
import json
from shutil import copyfileobj



class Modular_Abaqus_Builder:
    def __init__(self, overwrite=False, overwrite_models=False):
        '''
        ---------------------------------------------------
        Initialise the class and load the data from the .pkl file.
        ---------------------------------------------------
        '''
        
        # Create base database
        self.instantiate_database()
        
        # If overwrite flag set to true, delete all files
        if overwrite:
            print('-----------------------------------------------')
            print('OVERWRITE FLAG SET TO TRUE')
            print('-----------------------------------------------')

            if self.yes_no_question('Are you sure you would like to overwrite the database? (This will delete all object, model and .pkl files)'):
                self.overwrite_database()

            else:
                print('-----------------------------------------------')
                print('The overwrite flag was set to true, but the overwrite was denied. Closing the database.')
                print('-----------------------------------------------')

                exit(0)

        # If overwrite models flag set to true, delete all model files
        elif overwrite_models:
            print('-----------------------------------------------')
            print('OVERWRITE MODELS FLAG SET TO TRUE')
            print('-----------------------------------------------')

            if self.yes_no_question('Are you sure you would like to overwrite the models of the database? (This will delete all model files and their database entries)'):

                try:
                    self.load_database()
                except:
                    print('-----------------------------------------------')
                    print('The data.pkl file: "{}" does not exist. An empty Modular_Abaqus_Builder has been loaded.'.format(self.fpaths['data']))
                    print('-----------------------------------------------')

                self.overwrite_models()
            
            else:
                print('-----------------------------------------------')
                print('The overwrite models flag was set to true, but the overwrite was denied. Closing the database.')
                print('-----------------------------------------------')

                exit(0)

        else:

            # Load data from data.pickle
            try:
                self.load_database()

            # If it doesnt exist load an empty Modular_Abaqus_Builder
            except:
                
                print('-----------------------------------------------')
                print('The data.pkl file: "{}" does not exist. An empty Modular_Abaqus_Builder has been loaded.'.format(self.fpaths['data']))
                print('-----------------------------------------------')        

        self.save_database()
    

    def instantiate_database(self):
        '''
        ---------------------------------------------------
        Instantiate an empty database
        ---------------------------------------------------
        '''

        # Try to load the base_data .json
        try:
            with open('base_data.json') as f_load:
                base_data = json.load(f_load)

            self.fpaths = base_data['fpaths']

            self.requirements = base_data['requirements']

            self.allowed_characters = {key : set(value) for key, value in base_data['allowed_characters'].items()}

            self.inquirer_dialogs = base_data['inquirer_dialogs']

            self.data = base_data['data']


        except:

            print('Loading the base database information failed, using base information in program instead')
            print('Note, that preferably a "base_data.json" should be created by the user.')

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
                                    'Model' : set(string.ascii_letters + string.digits + '_-!()[]'),
                                    'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"')}
            
            # Set inquirer dialog lists
            self.inquirer_dialogs = {'Object_Types' : ['analysis','geometry','material'],
                                    'Main_Loop' : ['edit_objects', 'edit_models', 'save_database', 'validate_database', 'help', 'exit'],
                                    'Object_Loop' : ['create', 'modify', 'duplicate', 'delete', 'help', 'back'],
                                    'Model_Loop' : ['create', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']}
        
            self.data = {'analysis': {}, 'geometry': {}, 'material': {}, 'model': {}}


        # Make storage folders if they dont exist
        if not os.path.exists(self.fpaths['analysis']):
            os.makedirs(self.fpaths['analysis'], exist_ok=True)
            print('Analysis objects fpath did not exist, one has been created')
        
        if not os.path.exists(self.fpaths['geometry']):
            os.makedirs(self.fpaths['geometry'], exist_ok=True)
            print('Geometry objects fpath did not exist, one has been created')

        if not os.path.exists(self.fpaths['material']):
            os.makedirs(self.fpaths['material'], exist_ok=True)
            print('Material objects fpath did not exist, one has been created')

        if not os.path.exists(self.fpaths['model_files']):
            os.makedirs(self.fpaths['model_files'], exist_ok=True)
            print('Model fpath did not exist, one has been created')
        

    def overwrite_database(self):
        '''
        ---------------------------------------------------
        Delete all objects and models in the relevant filepaths
        ---------------------------------------------------
        '''
        
        try:
            # Delete all analysis object files
            for analysis in glob.glob(os.path.join(self.fpaths['analysis'], '*', ''), recursive=False):
                rmtree(analysis)
                print('Deleted: "{}"'.format(analysis))

            # Delete all geometry object files
            for geometry in glob.glob(os.path.join(self.fpaths['geometry'], '*', ''), recursive=False):
                rmtree(geometry)
                print('Deleted: "{}"'.format(geometry))

            # Delete all material object files
            for material in glob.glob(os.path.join(self.fpaths['material'], '*', ''), recursive=False):
                rmtree(material)
                print('Deleted: "{}"'.format(material))

            # Delete all model files
            for model in glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False):
                rmtree(model)
                print('Deleted: "{}"'.format(model))

            if os.path.exists(self.fpaths['data']):
                # Delete pickle storage file
                os.remove(self.fpaths['data'])

        except:
            print('-----------------------------------------------')
            print('ERROR: The program cannot delete a file due to another program using a directory.')
            print('-----------------------------------------------')

            exit(0)


    def overwrite_models(self):
        '''
        ---------------------------------------------------
        Delete all models in the relevant filepaths and removes their entries from the database
        ---------------------------------------------------
        '''

        try:
            for model in glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False):
                rmtree(model)
                print('Deleted Directory: "{}"'.format(model))

            for model in self.data['model'].keys():
                print('Deleted Model: "{}", from the database.'.format(model))

            self.data['model'] = {}

        except:
            print('-----------------------------------------------')
            print('ERROR: The program cannot delete a file due to another program using a directory.')
            print('-----------------------------------------------')

            exit(0)


    def load_database(self):
        '''
        ---------------------------------------------------
        Load the database from the .pkl file
        ---------------------------------------------------
        '''
        with open(self.fpaths['data'], 'rb') as df:
            

            self.data = pkl.load(df).data

            print('-----------------------------------------------')
            print('Loading from: "{}" was successful.'.format(self.fpaths['data']))
            print('The following data was imported into the database: ')
            print('-----------------------------------------------')

        self.print_database()


    def save_database(self):
        '''
        ---------------------------------------------------
        Saves the database to a .pkl file
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Saving the Database')
        print('-----------------------------------------------')
        # Save data
        with open(self.fpaths['data'], 'wb') as df:
            pkl.dump(self, df)
            print('-----------------------------------------------')
            print('Save to: "{}" was successful.'.format(self.fpaths['data']))
            print('-----------------------------------------------')


    def main_loop(self):
        '''
        ---------------------------------------------------
        Main loop that controls the tui of the database
        ---------------------------------------------------
        '''
        command = 'edit_objects'

        while True:
            
            # Commands = ['edit_objects', 'edit_models', 'save_database', 'validate_database', 'help', 'exit']
            command = inquirer.list_input('Pick Command: ', choices=self.inquirer_dialogs['Main_Loop'], carousel=True, default=command)

            if command == 'exit':
                if self.yes_no_question('Are you sure you would like to exit?'):
                    self.save_database()
                    break

            elif command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'], carousel = True)

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_main_help_message()

            elif command == 'save_database':
                self.save_database()

            elif command == 'edit_models':
                self.edit_models()
                
            elif command == 'edit_objects':
                self.edit_objects()

            elif command == 'validate_database':
                self.validate_database()


        print('-----------------------------------------------')
        print('Exiting the interface :3')
        print('-----------------------------------------------')


    def edit_objects(self):
        '''
        ---------------------------------------------------
        Main loop for editing objects in the database
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Entering Edit Objects interface')
        print('-----------------------------------------------')

        command = 'create'

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'help', 'back']
            command = inquirer.list_input('Pick Edit Object Command', choices=self.inquirer_dialogs['Object_Loop'], carousel = True, default = command)


            if command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'], carousel = True)

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_object_help_message()


            elif command == 'create':

                object_type = self.select_object_type()

                self.create_object(object_type)

                self.save_database()


            elif command == 'modify':
                
                # Select object to be modified
                object_name, object_type = self.select_object()
                
                # Check if object was available
                if object_name:

                    self.modify_object(object_name, object_type)
                    
                    self.save_database()

                else: 
                    print('Returning to object loop.')
                    print('-----------------------------------------------')

            elif command == 'duplicate':

                # Select object to be duplicated
                object_name, object_type = self.select_object()

                # Check if object was available
                if object_name:

                    # Duplicate the object to a new name
                    self.duplicate_object(object_type, object_name)

                    self.save_database()

                else: 
                    print('Returning to object loop.')
                    print('-----------------------------------------------')


            elif command == 'delete':
                
                # Select object to be deleted
                object_name, object_type = self.select_object(message = ' you would like to delete')

                # Check if object was available
                if object_name:

                    # Delete the object
                    self.delete_object(object_type, object_name)

                    self.save_database()

                else: 
                    print('Returning to object loop.')
                    print('-----------------------------------------------')


        print('-----------------------------------------------')
        print('Returning to the main loop')
        print('-----------------------------------------------')


    def edit_models(self):
        '''
        ---------------------------------------------------
        Main loop for editing models in the database
        ---------------------------------------------------
        '''

        print('-----------------------------------------------')
        print('Entering edit models interface')
        print('-----------------------------------------------')
        
        command = 'create'

        while command != 'back':
            
            # Commands = ['create', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']
            command = inquirer.list_input('Pick Model Edit Command: ', choices=self.inquirer_dialogs['Model_Loop'], carousel = True, default = command)

            if command == 'help':
                help_message = inquirer.list_input('Print database structure or Help menu? ', choices=['print','help'], carousel = True)

                if help_message == 'print':
                    self.print_database()
                else:
                    self.print_model_help_message()

            elif command == 'create':
                self.create_model()

                self.save_database()

            elif command == 'modify':
                self.modify_model()

                self.save_database()

            elif command == 'duplicate':
                self.duplicate_model()

                self.save_database()

            elif command == 'delete':
                self.delete_model()

                self.save_database()

            elif command == 'post_process':
                self.postprocess_model()

                self.save_database()

            elif command == 'run':
                self.run_model()

                self.save_database()

        
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

        object_type = inquirer.list_input('Pick Object Type: ', choices=self.inquirer_dialogs['Object_Types'], carousel = True)

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
        choices = list(self.data[object_type].keys())

        # Check there are choices available
        if len(choices):
            selected_object = inquirer.list_input('Pick the {} object{}'.format(object_type,message), choices=choices, carousel = True)

        else:
            print('-----------------------------------------------')
            print('ERROR: no objects of type: "{}" to select.'.format(object_type))
            return '', object_type
        
        print('-----------------------------------------------')
        print('Object: "{}" of object type: "{}" was selected.'.format(selected_object,object_type))
        print('-----------------------------------------------')
        
        return selected_object, object_type


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
        modifications = inquirer.checkbox('What would you like to change about the object: "{}", of type: "{}"'.format(object_name,object_type),
                                        choices = possible_changes)

        # Create change dictionary
        object_modifications = {'name': False,
                       'description' : False,
                       'parameters' : False,
                       'requirements' : False}
        
        # If no changes picked or cancelled return to main loop
        if (not modifications) or ('cancel' in modifications):
            print('-----------------------------------------------')
            print('No changes picked or cancel command picked')
            print('Returning to main loop.')
            print('-----------------------------------------------')
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

                self.data['analysis'][temp_object.name] = temp_object

            elif object_type == 'geometry':

                temp_object = Geometry_Object(self)

                self.data['geometry'][temp_object.name] = temp_object

            elif object_type == 'material':

                temp_object = Material_Object(self)

                self.data['material'][temp_object.name] = temp_object

        except:
            print('-----------------------------------------------')
            print('An error occurred while adding the object to the Database.')
            print('-----------------------------------------------')
            
    
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
        if not self.yes_no_question('Would you like to modify object: "{}" of type: "{}"? \nNOTE: The database will be saved automatically afterwards and the previous information will be LOST'.format(object_name, object_type)):
            return

        print('-----------------------------------------------')
        print('Modify object operation begun.')
        print('-----------------------------------------------')

        object_modifications = self.get_object_modifications(object_name, object_type)
        
        # Change name/file directory
        if object_modifications['name']:


            # Pick new name
            self.data[object_type][object_name].new_object_name()
            new_name = self.data[object_type][object_name].name

            self.data[object_type][new_name] = self.data[object_type].pop(object_name)


            # Change folder name
            try:
                fpath = os.path.join(self.fpaths[object_type], object_name)
                new_fpath = os.path.join(self.fpaths[object_type], new_name)
                os.rename(fpath, new_fpath)
                print('Renaming the filepath: "{}" to "{}" was successful.'.format(fpath,new_fpath))

            except:
                raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(fpath,new_fpath))
            
            # Change fpath
            self.data[object_type][new_name].fpath = new_fpath
            print('The filepath for {} "{}" was successfully changed to "{}" in the local dictionary.'.format(object_type,new_name,new_fpath))
            
            object_name = new_name

            print('Name modification was successful.')

        # Change description
        if object_modifications['description']:
            self.data[object_type][object_name].new_description()
            print('Description modification was successful.')

        # Change parameters
        if object_modifications['parameters']:
            self.data[object_type][object_name].define_parameters()
            print('Parameters modification was successful.')
            
        if object_modifications['requirements']:
            self.data[object_type][object_name].set_requirements()


        print('-----------------------------------------------')
        print('Modify object operation successful.')
        print('-----------------------------------------------')


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
        print('-----------------------------------------------')
        print('Duplicate object operation begun.')
        print('-----------------------------------------------')

        # Copy object and change its name
        duplicated_object = deepcopy(self.data[object_type][object_name])
        duplicated_object.builder = self
        duplicated_object.new_object_name()
        
        new_name = duplicated_object.name

        # Get new fpath
        new_fpath = os.path.join(self.fpaths[object_type], new_name)
        duplicated_object.fpath = new_fpath

        self.data[object_type][new_name] = duplicated_object

        # Get old file path
        fpath = os.path.join(self.fpaths[object_type], object_name)

        # Check file path does not already exist
        if os.path.exists(new_fpath):
            raise FileExistsError('The file path: "{}" already exists.'.format(new_fpath))

        self.data[object_type][new_name].move_folder(fpath, new_fpath)  

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

        # Get file path of files
        fpath = os.path.join(self.fpaths[object_type], object_name)

        # Delete files from filepath
        rmtree(fpath)
        print('The file path: "{}" and its contents have been successfully removed from the {} folder.'.format(fpath, object_type))
            
        
        # Then delete from local dictionary
        self.data[object_type].pop(object_name)
        print('The {}: "{}" has been successfully removed from the local dictionary.'.format(object_type,object_name))     
        
        print('-----------------------------------------------')
        print('Delete object operation successful.')
        print('-----------------------------------------------')
        

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

            print('Analysis Name: "{}"'.format(analysis.name))
            print('\tPath: "{}"'.format(analysis.fpath))
            print('\tDescription: "{}"'.format(analysis.description))
            print('\tFiles: ')

            for file in analysis.files:
                print('\t\t"{}"'.format(file))

            print('\tParameters: ')

            for parameter in analysis.parameters.keys():

                print('\t\tName: "{}"'.format(analysis.parameters[parameter]['name']))
                print('\t\t\tDescription: "{}"'.format(analysis.parameters[parameter]['description']))
                print('\t\t\tData-type: "{}"'.format(analysis.parameters[parameter]['dtype']))
                print('\t\t\tDefault Value: "{}"'.format(analysis.parameters[parameter]['default_value']))

                print('\t\t\tSolvers parameter modifies: ')
                for solver in analysis.parameters[parameter]['solvers']:
                        print('\t\t\t\t"{}"'.format(solver))


            print('\tRequirements: ')

            for requirement_type in analysis.requirements.keys():
                
                print('\t\t"{}"'.format(requirement_type))

                for requirement,requirement_value in analysis.requirements[requirement_type].items():
                    print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-----------------------------------------------')

        
        print('The Geometries currently loaded are: ')
        print('-----------------------------------------------')
        for geometry in self.data['geometry'].values():

            print('Geometry Name: "{}"'.format(geometry.name))
            print('\tPath: "{}"'.format(geometry.fpath))
            print('\tDescription: "{}"'.format(geometry.description))
            print('\tFiles: ')

            for file in geometry.files:
                print('\t\t"{}"'.format(file))

            print('\tParameters: ')

            for parameter in geometry.parameters.keys():

                print('\t\tName: "{}"'.format(geometry.parameters[parameter]['name']))
                print('\t\t\tDescription: "{}"'.format(geometry.parameters[parameter]['description']))
                print('\t\t\tData-type: "{}"'.format(geometry.parameters[parameter]['dtype']))
                print('\t\t\tDefault Value: "{}"'.format(geometry.parameters[parameter]['default_value']))

                print('\t\t\tSolvers parameter modifies: ')
                for solver in geometry.parameters[parameter]['solvers']:
                        print('\t\t\t\t"{}"'.format(solver))


            print('\tRequirements: ')

            for requirement_type in geometry.requirements.keys():
                
                print('\t\t"{}"'.format(requirement_type))

                for requirement,requirement_value in geometry.requirements[requirement_type].items():
                    print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-----------------------------------------------')


        print('The Materials currently loaded are: ')
        print('-----------------------------------------------')
        for material in self.data['material'].values():

            print('Material Name: "{}"'.format(material.name))
            print('\tPath: "{}"'.format(material.fpath))
            print('\tDescription: "{}"'.format(material.description))
            print('\tFiles: ')

            for file in material.files:
                print('\t\t"{}"'.format(file))

            print('\tParameters: ')

            for parameter in material.parameters.keys():

                print('\t\tName: "{}"'.format(material.parameters[parameter]['name']))
                print('\t\t\tDescription: "{}"'.format(material.parameters[parameter]['description']))
                print('\t\t\tData-type: "{}"'.format(material.parameters[parameter]['dtype']))
                print('\t\t\tDefault Value: "{}"'.format(material.parameters[parameter]['default_value']))

                print('\t\t\tSolvers parameter modifies: ')
                for solver in material.parameters[parameter]['solvers']:
                        print('\t\t\t\t"{}"'.format(solver))


            print('\tRequirements: ')

            for requirement_type in material.requirements.keys():
                
                print('\t\t"{}"'.format(requirement_type))

                for requirement,requirement_value in material.requirements[requirement_type].items():
                    print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('-----------------------------------------------')


        # ******************* WILL NEED TO BE UPDATED UPON ADDING MODEL CLASS *************************

        print('The Models currently loaded are: ')
        print('-----------------------------------------------')
        for model in self.data['model'].values():

            print('Model Name: "{}"'.format(model.name))
            print('\tDescription: "{}"'.format(model.description))
            print('\tPath: "{}"'.format(model.fpath))
            print('\tSolver Fpaths: ')

            for solver,fpath in model.solver_fpaths.items():
                if fpath is not None:
                    print('\t\t "{}": "{}"'.format(solver,fpath))

            print('\tAnalysis used: "{}"'.format(model.analysis.name))
            print('\tWhich has requirements: ')

            for requirement_type in model.requirements.keys():
                
                print('\t\t"{}"'.format(requirement_type))

                for requirement,requirement_value in model.requirements[requirement_type].items():
                    print('\t\t\t"{}": "{}"'.format(requirement,requirement_value))

            print('\tGeometry used: "{}"'.format(model.geometry.name))
            print('\tMaterials used: ')

            for material in model.materials.keys():
                print('\t\t"{}"'.format(model.materials[material].name))

            print('\tParameters: ')

            for parameter in model.parameters.keys():

                print('\t\tName: "{}"'.format(model.parameters[parameter]['name']))
                print('\t\t\tDescription: "{}"'.format(model.parameters[parameter]['description']))
                print('\t\t\tData-type: "{}"'.format(model.parameters[parameter]['dtype']))
                print('\t\t\tDefault Value: "{}"'.format(model.parameters[parameter]['default_value']))

                print('\t\t\tSolvers parameter modifies: ')
                for solver in model.parameters[parameter]['solvers']:
                        print('\t\t\t\t"{}"'.format(solver))


            print('-----------------------------------------------')


    def validate_database(self):
        '''
        
        '''
        print('-----------------------------------------------')
        print('Validating the Database to ensure no corruption has occured.')
        print('-----------------------------------------------')

        # Validate Analyses
        print('Validating Analyses...')
        for analysis_name in list(self.data['analysis'].keys()):
            
            print('Validating Analysis: "{}"'.format(analysis_name))

            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['analysis'],analysis_name) == self.data['analysis'][analysis_name].fpath


            # Check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['analysis'],analysis_name))


            # Check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['analysis'],analysis_name,file_to_check)) for file_to_check in self.data['analysis'][analysis_name].files])


            # Check requirements match database requirements
            if (self.requirements.keys() != self.data['analysis'][analysis_name].requirements.keys()) or any([self.requirements[key].keys() != self.data['analysis'][analysis_name].requirements[key].keys() for key in self.requirements.keys()]):

                print('The requirements for the Analysis object: "{}" do not match the default requirements of the database. Please select new requirements.'.format(analysis_name))
                self.data['analysis'][analysis_name].set_requirements(reset_requirements = True)


            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print('Analysis: "{}", validated successfully'.format(analysis_name))

            else:
                self.data['analysis'].pop(analysis_name)
                print('Analysis: "{}", was found to be not valid. Deleting from database'.format(analysis_name))

        print('Analyses Validated.')


        # Validate Geometries
        print('Validating Geometries...')
        for geometry_name in list(self.data['geometry'].keys()):
            
            print('Validating Geometry: "{}"'.format(geometry_name))

            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['geometry'],geometry_name) == self.data['geometry'][geometry_name].fpath


            # Check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['geometry'],geometry_name))


            # Check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['geometry'],geometry_name,file_to_check)) for file_to_check in self.data['geometry'][geometry_name].files])


            # Check requirements match database requirements
            if self.requirements['geometries'].keys() != self.data['geometry'][geometry_name].requirements['geometries'].keys():

                print('The requirements for the Geometry object: "{}" do not match the default requirements of the database.'.format(geometry_name))
                self.data['geometry'][geometry_name].set_requirements(reset_requirements = True)


            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print('Geometry: "{}", validated successfully'.format(geometry_name))

            else:
                self.data['geometry'].pop(geometry_name)
                print('Geometry: "{}", was found to be not valid. Deleting from database'.format(geometry_name))

        print('Geometries Validated.')


        # Validate Materials
        print('Validating Materials...')
        for material_name in list(self.data['material'].keys()):
            
            print('Validating Material: "{}"'.format(material_name))


            # Check fpath matches path + name
            fpath_matches = os.path.join(self.fpaths['material'],material_name) == self.data['material'][material_name].fpath


            # check directory exists
            directory_exists = os.path.exists(os.path.join(self.fpaths['material'],material_name))


            # check all files exist in object folder
            all_files_exist = all([os.path.exists(os.path.join(self.fpaths['material'],material_name,file_to_check)) for file_to_check in self.data['material'][material_name].files])


            # check requirements match database requirements
            if self.requirements['materials'].keys() != self.data['material'][material_name].requirements['materials'].keys():

                print('The requirements for the Material object: "{}" do not match the default requirements of the database.'.format(material_name))
                self.data['material'][material_name].set_requirements(reset_requirements = True)

            # Check all validations passed
            if fpath_matches and directory_exists and all_files_exist:
                print('Material: "{}", validated successfully'.format(material_name))

            else:
                self.data['material'].pop(material_name)
                print('Material: "{}", was found to be not valid. Deleting from database'.format(material_name))

        print('Materials Validated.')


        # Validate Models
        print('Validating Models...')
        for model_name in list(self.data['model'].keys()):


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

                print('The requirements for the Model: "{}" do not match the default requirements of the database.'.format(model_name))

                if analysis_exists:
                    self.data['model'][model_name].requirements = self.data['model'][model_name].analysis.requirements
                    requirements_valid = True
                else:
                    requirements_valid = False
            else:
                requirements_valid = True


            # Check all validations passed
            if fpath_matches and directory_exists and objects_exist and requirements_valid:
                print('Model: "{}", validated successfully'.format(model_name))

            else:
                self.data['model'].pop(model_name)
                print('Model: "{}", was found to be not valid. Deleting from database'.format(model_name))

        print('Models Validated.')


        # Delete any folders not connected to objects in the database
        for analysis_fpath in glob.glob(os.path.join(self.fpaths['analysis'],'*',''), recursive=False):
            if analysis_fpath not in [os.path.join(analysis.fpath,'') for analysis in self.data['analysis'].values()]:
                rmtree(analysis_fpath)
                print('Deleted Folder: "{}", that did not exist in the database.'.format(analysis_fpath))
                
        
        for geometry_fpath in glob.glob(os.path.join(self.fpaths['geometry'],'*',''), recursive=False):
            if geometry_fpath not in [os.path.join(geometry.fpath,'') for geometry in self.data['geometry'].values()]:
                rmtree(geometry_fpath)
                print('Deleted Folder: "{}", that did not exist in the database.'.format(geometry_fpath))


        for material_fpath in glob.glob(os.path.join(self.fpaths['material'],'*',''), recursive=False):
            if material_fpath not in [os.path.join(material.fpath,'') for material in self.data['material'].values()]:
                rmtree(material_fpath)
                print('Deleted Folder: "{}", that did not exist in the database.'.format(material_fpath))


        for model_fpath in glob.glob(os.path.join(self.fpaths['model_files'],'*',''), recursive=False):
            if model_fpath not in [os.path.join(model.fpath,'') for model in self.data['model'].values()]:
                rmtree(model_fpath)
                print('Deleted Folder: "{}", that did not exist in the database.'.format(model_fpath))

        
        for extra_object_fpath in glob.glob(os.path.join(self.fpaths['object_files'],'*',''), recursive=False):
            if extra_object_fpath not in [os.path.join(self.fpaths["analysis"],''),os.path.join(self.fpaths['geometry'],''),os.path.join(self.fpaths['material'],'')]:
                rmtree(extra_object_fpath)
                print('Deleted Folder: "{}", that did not exist in the database.'.format(extra_object_fpath))


        print('-----------------------------------------------')
        print('Database Validation Complete')
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
        command = inquirer.list_input(strings[-1], choices=['yes','no'], carousel = True)

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
        
            answer = inquirer.list_input('Please select the model you would like to delete from the database', choices = model_names+['cancel'], carousel = True)

            if answer == 'cancel':
                print('-----------------------------------------------')
                print('Delete model operation cancelled, returning to edit model loop')
                print('-----------------------------------------------')

            try:
                # Delete folder
                rmtree(self.data['model'][answer].fpath)
                print('-----------------------------------------------')
                print('Deleted Folder: "{}"'.format(self.data['model'][answer].fpath))

                # Delete from database
                self.data['model'].pop(answer)
                print('Deleted model: "{}", from the database.'.format(answer))
                print('-----------------------------------------------')

            except:
                print('-----------------------------------------------')
                print('Tried to delete the model: "{}", but could not. Check if the directory is open in another application.'.format(answer))
                print('Try running the validate database command once the error has been rectified to ensure corruption does not occur.')
                print('-----------------------------------------------')

        else:
            print('-----------------------------------------------')
            print('No models in database to delete, returning to edit model loop')
            print('-----------------------------------------------')   
        

    def create_model(self):
        '''
        Build model
        '''
        try:
            model = Model(self)
            
            self.data['model'][model.name] = model
        except:
            print('-----------------------------------------------')
            print('Create Model Failed, validating database to ensure corruption does not occur.')

            self.validate_database()
        

    def duplicate_model(self):
        '''
        
        '''
        model_names = list(self.data['model'].keys())

        if model_names:
        
            answer = inquirer.list_input('Please select the model you would like to duplicate from the database', choices = model_names+['cancel'], carousel = True)

            if answer == 'cancel':
                print('-----------------------------------------------')
                print('Duplicate model operation cancelled, returning to edit model loop')
                print('-----------------------------------------------')

            print('Model: "{}", chosen to be duplicated'.format(answer))

            # Try to copy the chosen model and then rebuild it from its base objects
            try:
                analysis_name = self.data['model'][answer].analysis.name
                geometry_name = self.data['model'][answer].geometry.name
                material_names = list(self.data['model'][answer].materials.keys())

                # Check that all the objects used to build the model to be duplicated still exist
                analysis_exists = analysis_name in self.data['analysis']
                geometry_exists = geometry_name in self.data['geometry'] 
                materials_exists = all([material_name in self.data['material'] for material_name in material_names])

                if analysis_exists and geometry_exists and materials_exists:

                    duplicate_model = Model(self, analysis_name, geometry_name, material_names)

                    self.data['model'][duplicate_model.name] = duplicate_model

                else:
                    print('-----------------------------------------------')
                    print('Tried to duplicate the model: "{}", and failed due to the previously used objects no longer existing.'.format(answer))
                    print('-----------------------------------------------')

            except:
                print('-----------------------------------------------')
                print('Tried to duplicate the model: "{}", but could not. Check if the directory is open in another application.'.format(answer))
                print('Validating database to ensure corruption does not occur.')
                print('-----------------------------------------------')

                self.validate_database()


        else:
            print('-----------------------------------------------')
            print('No models in database to duplicate, returning to edit model loop')
            print('-----------------------------------------------')
        
        






    def modify_model(self):
        '''
        
        '''
        model_names = list(self.data['model'].keys())

        if model_names:
        
            name = inquirer.list_input('Please select the model you would like to modify', choices = model_names+['cancel'], carousel = True)

            if name == 'cancel':
                print('-----------------------------------------------')
                print('Modify model operation cancelled, returning to edit model loop')
                print('-----------------------------------------------')
                return

            possible_changes = ['name', 'description', 'parameters', 'cancel']
        
            # Get Model changes
            modifications = inquirer.checkbox('What would you like to change about the model: "{}".'.format(name), choices = possible_changes, carousel = True)
            
            if ('cancel' in modifications) or not modifications:
                print('-----------------------------------------------')
                print('Modify model operation cancelled, returning to edit model loop')
                print('-----------------------------------------------')
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
                except:
                    raise FileExistsError('Renaming the filepath: "{}" to "{}" has failed.'.format(old_fpath,new_fpath))
                
                # Change name of main sim file (and journal file contents for just fluent run)
                if all(model_to_modify.requirements['softwares'].values()):
                    os.rename(os.path.join(model_to_modify.solver_fpaths['mpcci'],old_name+'.csp'),os.path.join(model_to_modify.solver_fpaths['mpcci'],name+'.csp'))
                
                elif model_to_modify.requirements['softwares']['abaqus']:
                    os.rename(os.path.join(model_to_modify.solver_fpaths['abaqus'],old_name+'.inp'),os.path.join(model_to_modify.solver_fpaths['abaqus'],name+'.inp'))

                elif model_to_modify.requirements['softwares']['fluent']:
                    os.rename(os.path.join(model_to_modify.solver_fpaths['fluent'],old_name+'.cas.h5'),os.path.join(model_to_modify.solver_fpaths['fluent'],name+'.cas.h5'))

                    # Edit journal file to reference new .cas.h5 file
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


            if 'description' in modifications:
                model_to_modify.new_description()

            if 'parameters' in modifications:
                pass # change parameter values and then rebuild model

            self.data['model'][name] = model_to_modify 

        else:
            print('-----------------------------------------------')
            print('No models in database to modify, returning to edit model loop')
            print('-----------------------------------------------')   
            return
    


    
    

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