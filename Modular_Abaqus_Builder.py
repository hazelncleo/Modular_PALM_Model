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


class Modular_Abaqus_Builder:
    def __init__(self, overwrite=False, overwrite_models=False):
        '''
        ---------------------------------------------------
        Initialise the class and load the data from the .pkl file.
        ---------------------------------------------------
        '''

        # Set filepaths
        objectfiles_fpath = 'object_files'
        self.fpaths = {'object_files' : objectfiles_fpath,
                    'analysis' : os.path.join(objectfiles_fpath, 'analysis'),
                    'geometry' : os.path.join(objectfiles_fpath, 'geometry'),
                    'material': os.path.join(objectfiles_fpath, 'materials'),
                    'model_files': 'model_files',
                    'data': 'data.pickle'}
        
        if overwrite:
            print('-----------------------------------------------')
            print('OVERWRITE FLAG SET TO TRUE')
            print('-----------------------------------------------')

            if self.yes_no_question('Are you sure you would like to overwrite the database? (This will delete all object, model and .pkl files)'):
                self.overwrite_database()
                return

            else:
                print('-----------------------------------------------')
                print('The overwrite flag was set to true, but the overwrite was denied. Closing the database.')
                print('-----------------------------------------------')

                exit(0)


        # Make storage folders if they dont exist
        os.makedirs(self.fpaths['analysis'], exist_ok=True)
        os.makedirs(self.fpaths['geometry'], exist_ok=True)
        os.makedirs(self.fpaths['material'], exist_ok=True)
        os.makedirs(self.fpaths['model_files'], exist_ok=True)

        # Load data from data.pickle
        try:
            self.load_database()

        # If it doesnt exist load an empty Modular_Abaqus_Builder
        except:

            self.instantiate_database()
            
            print('-----------------------------------------------')
            print('The data.pkl file: "{}" does not exist. An empty Modular_Abaqus_Builder has been loaded.'.format(self.fpaths['data']))
            print('-----------------------------------------------')

            self.save_database()
            
        # If overwrite_models flag set to true, delete all model files and their database entries
        if overwrite_models:
            print('-----------------------------------------------')
            print('OVERWRITE MODELS FLAG SET TO TRUE')
            print('-----------------------------------------------')

            if self.yes_no_question('Are you sure you would like to overwrite the models of the database? (This will delete all model files and their database entries)'):
                self.overwrite_models()
            
            else:
                print('-----------------------------------------------')
                print('The overwrite models flag was set to true, but the overwrite was denied. Closing the database.')
                print('-----------------------------------------------')

                exit(0)
        

    def overwrite_database(self):
        '''
        ---------------------------------------------------
        Delete all objects and models in the relevant filepaths
        ---------------------------------------------------
        '''
        
        for analysis in glob.glob(os.path.join(self.fpaths['analysis'], '*', ''), recursive=False):
            rmtree(analysis)
            print('Deleted: "{}"'.format(analysis))

        for geometry in glob.glob(os.path.join(self.fpaths['geometry'], '*', ''), recursive=False):
            rmtree(geometry)
            print('Deleted: "{}"'.format(geometry))

        for material in glob.glob(os.path.join(self.fpaths['material'], '*', ''), recursive=False):
            rmtree(material)
            print('Deleted: "{}"'.format(material))

        for model in glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False):
            rmtree(model)
            print('Deleted: "{}"'.format(model))

        self.instantiate_database()


    def overwrite_models(self):
        '''
        ---------------------------------------------------
        Delete all models in the relevant filepaths and removes their entries from the database
        ---------------------------------------------------
        '''

        for model in glob.glob(os.path.join(self.fpaths['model_files'], '*', ''), recursive=False):
            rmtree(model)
            print('Deleted: "{}"'.format(model))

        self.data['model'] = {}


    def load_database(self):
        '''
        ---------------------------------------------------
        Load the database from the .pkl file
        ---------------------------------------------------
        '''
        with open(self.fpaths['data'], 'rb') as df:

            self.__dict__ = pkl.load(df).__dict__
            print('-----------------------------------------------')
            print('Loading from: "{}" was successful.'.format(self.fpaths['data']))
            print('-----------------------------------------------')
            
        self.save_database()


    def instantiate_database(self):
        '''
        ---------------------------------------------------
        Instantiate an empty database
        ---------------------------------------------------
        '''

        # Set allowed characters
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'),
                                'Model' : set(string.ascii_letters + string.digits + '_-!()[]'),
                                'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"')}
        
        # Set inquirer dialog lists
        self.inquirer_dialogs = {'Object_Types' : ['analysis','geometry','material'],
                                'Main_Loop' : ['edit_objects', 'edit_models', 'save_database', 'help', 'exit', 'force_exit'],
                                'Object_Loop' : ['create', 'modify', 'duplicate', 'delete', 'help', 'back'],
                                'Model_Loop' : ['create', 'modify', 'duplicate', 'delete', 'post_process', 'run', 'help', 'back']}
    
        self.data = {'analysis': {}, 'geometry': {}, 'material': {}, 'model': {}}


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
            
        return


    def main_loop(self):
        '''
        ---------------------------------------------------
        Main loop that controls the tui of the database
        ---------------------------------------------------
        '''
        command = 'edit_objects'

        while True:
            
            # Commands = ['edit_objects', 'edit_models', 'save_database', 'help', 'exit', 'force_exit']
            command = inquirer.list_input('Pick Command: ', choices=self.inquirer_dialogs['Main_Loop'], carousel = True, default = command)

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

            elif command == 'force_exit':
                if self.yes_no_question('Are you sure you would like to force exit without saving?'):
                    break


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

            elif command == 'modify':
                self.modify_model()

            elif command == 'duplicate':
                self.duplicate_model()

            elif command == 'delete':
                self.delete_model()

            elif command == 'post_process':
                self.postprocess_model()

            elif command == 'run':
                self.run_model()

        
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
        choices = [x for x in self.data[object_type].keys()]

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

                print('\t\t\tFiles parameter modifies: ')
                for file in analysis.parameters[parameter]['files']:
                        print('\t\t\t\t"{}"'.format(file))


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

                print('\t\t\tFiles parameter modifies: ')
                for file in geometry.parameters[parameter]['files']:
                        print('\t\t\t\t"{}"'.format(file))


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

                print('\t\t\tFiles parameter modifies: ')
                for file in material.parameters[parameter]['files']:
                        print('\t\t\t\t"{}"'.format(file))


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
            print('\tPath: "{}"'.format(model.fpath))
            print('\tDescription: "{}"'.format(model.description))
            print('\tFiles: ')

            for file in glob.glob(os.path.join(model.fpath,'*.*')):
                print('\t\t"{}"'.format(file))

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
        
        
        
        




    def create_model(self): # update
        '''
        Build model
        '''
        try:
            model = Model(self)
            
            self.data['model'][model.name] = model
        except:
            print('-----------------------------------------------')
            print('Create Model Failed, returning to Model loop.')
            print('-----------------------------------------------')
            return
        

        
        
        
        


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
    

    def postprocess_model(self):
        '''
        
        '''
        pass


    def run_model(self):
        '''
        
        '''
        pass 


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