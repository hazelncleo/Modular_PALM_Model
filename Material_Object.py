import os
from shutil import copytree
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer



class Material_Object:
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
        
        # Specify allowed characters for certain attributes
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'), 'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"'), 'Parameter_Name' : set(string.ascii_letters + string.digits + '-_')}
        
        self.name = self.new_object_name()

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths['analysis'],self.name)

        self.description = self.new_description()
        
        source_fpath = self.get_file_path()
        
        # Return error if fpath not specified
        if not source_fpath:
            raise FileNotFoundError('A file path was not selected.')

        copytree(source_fpath, self.fpath, symlinks=True)

        self.choose_parameters()
        
        self.requirements = {'softwares' : {'abaqus' : False, 'fluent' : False, 'mpcci' : False},
                             'geometries' : {'abaqus_whole-chip_solid' : False, 'abaqus_whole-chip_acoustic' : False, 'abaqus_submodel_solid' : False, 'abaqus_submodel_acoustic' : False, 'fluent_whole-chip_fluid' : False, 'fluent_submodel_fluid' : False},
                             'materials' : {'abaqus_solid' : False, 'abaqus_acoustic' : False},
                             'analysis' : {'abaqus_global_odb' : False, 'abaqus_global_prt' : False, 'fluent_journal' : False}
                             }
        
        self.set_requirements()
        
        print('-----------------------------------------------')
        print('Create Analysis object operation successful.')
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
        current_names = self.builder.data['analysis'].keys()

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

        # Loop until new description entered
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
            
    
    def get_file_path(self):
        '''
        ---------------------------------------------------
        Prompt the user to select a filepath.
        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------
        file_path : str
            A string containing the filepath the user selected. If the user clicked cancel, an empty string will be returned
        ---------------------------------------------------
        '''
        # Create window and remove from view
        root = Tk()
        root.iconbitmap('cade.ico')
        root.overrideredirect(1)
        root.geometry('0x0+0+0')
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        
        # Get filepath from askdirectory dialog
        file_path = askdirectory(title = 'Select folder to read Analysis files from: ', initialdir=os.path.abspath(os.getcwd()))

        root.destroy()
        
        return file_path
    

    def choose_parameters(self):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        commands = ['add', 'exit']
        
        self.parameters = {}
        while True:

            # Get parameter type or exit choosing parameter command
            command = inquirer.list_input('Add more parameters or exit choose parameter dialog?', choices=commands)

            if command == 'exit':

                print('---------------------------------------------------')
                print('Exiting Choose parameter dialog.')
                print('Parameters chosen for the analysis are: ')

                # Print all parameters added
                for parameter in self.parameters.keys():
                    print('---------------------------------------------------')
                    print('Name: {}'.format(self.parameters[parameter]['name']))
                    print('\tDescription: {}'.format(self.parameters[parameter]['description']))
                    print('\tData-type: {}'.format(self.parameters[parameter]['dtype']))
                    print('\tRange: {}'.format(self.parameters[parameter]['range']))
                    print('\tDefault Value: {}'.format(self.parameters[parameter]['default_value']))

                print('---------------------------------------------------')
                return
            
            if command == 'add':
                self.add_parameter()


    def add_parameter(self):
        '''
        ---------------------------------------------------

        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------

        ---------------------------------------------------
        '''

        ranges = ['positive', 'all']
        dtypes = ['int', 'float']
                                                                                                            
        questions = [inquirer.Text('name', message='Please enter a name for the parameter to be added'),
                     inquirer.Text('description', message='Please enter a description of the parameter to be added'),
                     inquirer.List('dtype', message='Please choose a data-type for the parameter to be added', choices=dtypes),
                     inquirer.List('range', message='Please choose a data range for the parameter to be added', choices=ranges),
                     inquirer.Text('default_value', 'Please enter the default value for the parameter to be added')]

        # Loop until new name is unique
        while True:
            print('The following names are already in use: {}'.format([name for name in self.parameters.keys()]))
            answers = inquirer.prompt(questions)

            # Convert default value **************WILL NEED TO BE UPDATED*****************
            if answers['dtype'] == 'int':
                answers['default_value'] = int(answers['default_value'])
                answers['dtype'] = int
            else:
                answers['default_value'] = float(answers['default_value'])
                answers['dtype'] = float
            

            # Check name is not empty
            if not answers['name']:
                print('---------------------------------------------------')
                print('ERROR: The name provided was an empty string')
                print('---------------------------------------------------')

            # Check name only uses allowed characters
            elif not (set(answers['name']) <= self.allowed_characters['Parameter_Name']):
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", is not entirely letters, numbers or underscores and hyphens.'.format(answers['name']))
                print('---------------------------------------------------')
            
            # Check name is unique
            elif answers['name'] in self.parameters.keys():
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(answers['name']))
                print('---------------------------------------------------')

            # Check description only uses allowed characters
            elif not (set(answers['description']) <= self.allowed_characters['Description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(answers['description']))
                print('---------------------------------------------------')
            
            # Check default value is within range
            elif (answers['range'] == 'positive') and (answers['default_value'] < 0): 
                print('---------------------------------------------------')
                print('The default value: "{}", is outside of the range "positive" specified.'.format(answers['default_value']))
                print('---------------------------------------------------')

            else:
                self.parameters[answers['name']] = answers
                break


    def set_requirements(self):
        pass    