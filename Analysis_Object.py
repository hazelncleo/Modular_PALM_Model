import os
from shutil import copy2 as copy_input_file
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory

class Analysis_Object:
    def __init__(self, builder):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        
        print('-----------------------------------------------')
        print('Create Analysis Object operation started.')
        print('-----------------------------------------------')
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'), 'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"')}
        
        self.name = self.new_object_name()
        
        self.description = self.new_description()
        
        fpath = self.get_file_path()
        
        # Return error if fpath not specified
        if not fpath:
            return -1
            
        self.fpath = fpath
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
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
    
    
    def new_object_name(self):
        '''
        ---------------------------------------------------
        Gets a new Analysis Object name, ensures that no object already exists of that type
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        name : str
            The name for the new Analyis Object
        ---------------------------------------------------
        '''
        # Get current names
        current_names = self.Builder.data['analysis'].keys()

        name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the Analysis Object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, underscores and hyphens.')
            print('- It must be lowercase.')
            print('- It must be unique.')
            print('---------------------------------------------------')
            print('The Analysis names currently in use are listed below: ')
            print(current_names)
            print('---------------------------------------------------')
            
            name = input('Please enter a new name for the object to be created: ')

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
                return name
                
                
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

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a description for the object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.?! ()[]"\'')
            print('---------------------------------------------------')
            
            description = input('Please enter a description for the Analysis Object to be created: ')

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
            
    
    def get_file_path():
        # Create window and remove from view
        root = Tk()
        root.iconbitmap('cade.ico')
        root.overrideredirect(1)
        root.geometry('0x0+0+0')
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        
        # Get filepath from askdirectory dialog
        file_path = askdirectory(title = 'Select folder to read *.inp files: ', initialdir=os.path.abspath(os.getcwd()))

        root.destroy()
        
        return file_path