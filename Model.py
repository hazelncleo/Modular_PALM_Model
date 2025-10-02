import os
from shutil import copytree
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer


class Model:
    def __init__(self, builder):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        
        print('-----------------------------------------------')
        print('Create Model Started')
        print('-----------------------------------------------')
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        # Specify allowed characters for certain attributes
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'), 'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"')}
        
        self.new_model_name()

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths['analysis'],self.name)

        self.new_description()

        # Select analysis object

        # Get requirements

        # Add geometry

        # Check geometry requirements fulfilled

        # Add materials

        
        print('-----------------------------------------------')
        print('Create Model operation successful.')
        print('-----------------------------------------------')
    

    def move_folder(self, source_fpath, destination_fpath):
        copytree(source_fpath, destination_fpath, symlinks=True)

    
    def new_model_name(self):
        '''
        ---------------------------------------------------
        Gets a new Model name, ensures that no model with that name exists
        ---------------------------------------------------
        '''
        # Get current names
        current_names = [name for name in self.builder.data['model'].keys()]

        name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the Model to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, underscores and hyphens.')
            print('- It must be lowercase.')
            print('- It must be unique.')
            print('---------------------------------------------------')
            print('The Model names currently in use are listed below: ')
            print(current_names)
            print('---------------------------------------------------')
            
            name = input('Please enter a new name for the model to be created: ')

            if not name:
                print('---------------------------------------------------')
                print('ERROR: The name provided was an empty string')
                print('---------------------------------------------------')

            elif not (set(name) <= self.allowed_characters['Name']):
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", is not entirely lowercase, numbers or underscores and hyphens.'.format(name))
                print('---------------------------------------------------')
            
            elif name in current_names:
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(name))
                print('---------------------------------------------------')
            
            else: 
                print('---------------------------------------------------')
                print('The name: "{}", for the new object has been selected.'.format(name))
                print('---------------------------------------------------')
                self.name = name
                return
                
                
    def new_description(self):
        '''
        ---------------------------------------------------
        Provide a description for the Analysis Object added to the database.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        description : str
            A string typed by the user that describes the new object that only has characters from "allowed_characters_description".
        ---------------------------------------------------
        '''

        description = ''

        # Loop until new description entered
        while True:
            print('---------------------------------------------------')
            print('Please enter a description for the object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.?! ()[]"\'')
            print('---------------------------------------------------')
            
            description = input('Please enter a description for the Analysis Object to be created: ')

            if not (set(description) <= self.allowed_characters['Description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(description))
                print('---------------------------------------------------')
            
            else:
                print('---------------------------------------------------')
                print('The description: "{}", for the new object has been selected.'.format(description))
                print('---------------------------------------------------')
                self.description = description
                return