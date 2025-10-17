import os
from shutil import copytree
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
import json
from glob import glob

class Material_Object:
    '''
    ---------------------------------------------------
    Contains all the relevant information for a Material Object
    ---------------------------------------------------
    Attributes
    ---------------------------------------------------

    ---------------------------------------------------
    Methods
    ---------------------------------------------------

    ---------------------------------------------------
    '''
    def __init__(self, builder):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        
        print('-----------------------------------------------')
        print('Create Material Object operation started.')
        print('-----------------------------------------------')
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        # Specify allowed characters for certain attributes
        self.allowed_characters = {'Name' : set(string.ascii_lowercase + string.digits + '_-'), 'Description' : set(string.ascii_letters + string.digits + '_-,.?! ()[]"'), 'Parameter_Name' : set(string.ascii_letters + string.digits + '-_')}
        
        self.new_object_name()

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths['material'],self.name)

        self.new_description()
        
        source_fpath = self.get_file_path()
        
        # Return error if fpath not specified
        if not source_fpath:
            raise FileNotFoundError('A file path was not selected.')

        self.move_folder(source_fpath, self.fpath)

        self.load_requirements()

        self.parameters = {}
        self.load_parameters()


        print('-----------------------------------------------')
        print('Create Material object operation successful.')
        print('-----------------------------------------------')
    

    def move_folder(self, source_fpath, destination_fpath):
        copytree(source_fpath, destination_fpath, symlinks=True)

    
    def new_object_name(self):
        '''
        ---------------------------------------------------
        Gets a new Material Object name, ensures that no object already exists of that type
        ---------------------------------------------------
        '''
        # Get current names
        current_names = [name for name in self.builder.data['material'].keys()]

        name = ''

        # Loop until new name is unique
        while True:
            print('---------------------------------------------------')
            print('Please enter a new name for the Material Object to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, underscores and hyphens.')
            print('- It must be lowercase.')
            print('- It must be unique.')
            print('---------------------------------------------------')
            print('The Material names currently in use are listed below: ')
            print(current_names)
            print('---------------------------------------------------')
            
            name = input('Please enter a new name for the object to be created: ')

            if not name:
                print('---------------------------------------------------')
                print('ERROR: The name provided was an empty string')
                print('---------------------------------------------------')

            elif not (set(name) <= self.allowed_characters['name']):
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
        Provide a description for the Material Object added to the database.
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
            
            description = input('Please enter a description for the Material Object to be created: ')

            if not (set(description) <= self.allowed_characters['description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(description))
                print('---------------------------------------------------')
            
            else:
                print('---------------------------------------------------')
                print('The description: "{}", for the new object has been selected.'.format(description))
                print('---------------------------------------------------')
                self.description = description
                return
            
    
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
        file_path = askdirectory(title = 'Select folder to read Material files from: ', initialdir=os.path.abspath(os.getcwd()))

        root.destroy()
        
        return file_path
    

    def define_parameters(self):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        commands = ['add', 'modify', 'delete', 'exit']

        while True:

            # Get parameter type or exit choosing parameter command
            command = inquirer.list_input('Add more parameters or exit choose parameter dialog?', choices=commands, carousel = True)

            if command == 'exit':

                print('---------------------------------------------------')
                print('Exiting Choose parameter dialog.')
                print('Parameters chosen for the Material are: ')

                # Print all parameters added
                for parameter in self.parameters.keys():
                    print('---------------------------------------------------')
                    print('Name: {}'.format(self.parameters[parameter]['name']))
                    print('\tDescription: {}'.format(self.parameters[parameter]['description']))
                    print('\tData-type: {}'.format(self.parameters[parameter]['dtype']))
                    print('\tDefault Value: {}'.format(self.parameters[parameter]['default_value']))
                    print('\tSolvers: ')
                    for solver in self.parameters[parameter]['solvers']:
                        print('\t\t"{}"'.format(solver))

                print('---------------------------------------------------')

                return
            
            elif command == 'add':
                self.add_parameter()

            elif command == 'modify':
                parameter_to_modify = self.choose_parameter('modify')

                if parameter_to_modify: self.modify_parameter(parameter_to_modify)

            elif command == 'delete':
                parameter_to_delete = self.choose_parameter('delete')

                if parameter_to_delete: self.delete_parameter(parameter_to_delete)


    def add_parameter(self):
        '''
        ---------------------------------------------------

        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------

        ---------------------------------------------------
        '''

        dtypes = ['int', 'float']


        questions = [inquirer.Text('name', message='Please enter a name for the parameter to be added'),
                    inquirer.Text('description', message='Please enter a description of the parameter to be added'),
                    inquirer.List('dtype', message='Please choose a data-type for the parameter to be added', choices=dtypes, carousel = True),
                    inquirer.Text('default_value', 'Please enter the default value for the parameter to be added'),
                    inquirer.Checkbox('solvers', message='Please choose the solvers this parameter controls', choices = ['abaqus','fluent','mpcci'], carousel=True)]

        # Loop until new name is unique
        while True:
            print('The following names are already in use: {}'.format([name for name in self.parameters.keys()]))
            answers = inquirer.prompt(questions)

            # Convert default value **************WILL NEED TO BE UPDATED*****************
            if answers['dtype'] == 'int':
                answers['default_value'] = int(answers['default_value'])
            else:
                answers['default_value'] = float(answers['default_value'])
            

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
            elif not (set(answers['description']) <= self.allowed_characters['description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(answers['description']))
                print('---------------------------------------------------')

            # Check at least one file has been chosen
            elif not answers['solvers']:
                print('---------------------------------------------------')
                print('ERROR: No Solver chosen')
                print('---------------------------------------------------')

            else:
                self.parameters[answers['name']] = answers
                break


    def choose_parameter(self, command):

        # Get parameter names
        parameters = [params for params in self.parameters.keys()]

        # Check if empty
        if parameters:

            while True:

                parameters.append('cancel')

                # Ask user which parameter to select
                chosen_parameter = inquirer.list_input('Choose parameter to {}'.format(command), choices=parameters, carousel = True)

                if chosen_parameter == 'cancel':
                    print('-----------------------------------------------')
                    print('Parameter {} command cancelled, returning to loop.'.format(command))
                    print('-----------------------------------------------')
                    return ''
                
                else:
                    print('-----------------------------------------------')
                    print('Parameter "{}" chosen for {} command, returning to loop.'.format(chosen_parameter, command))
                    print('-----------------------------------------------')
                    return chosen_parameter
                    
        else:
            print('-----------------------------------------------')
            print('No parameters to pick, returning to loop.')
            print('-----------------------------------------------')
            return ''


    def modify_parameter(self, parameter_to_modify):

        '''
        ---------------------------------------------------

        ---------------------------------------------------
        RETURNS
        ---------------------------------------------------

        ---------------------------------------------------
        '''

        dtypes = ['int', 'float']

                                                                                            
        questions = [inquirer.Text('name', message='Please enter a new name for the parameter to be modified', default=parameter_to_modify),
                    inquirer.Text('description', message='Please enter a description of the parameter to be modified', default=self.parameters[parameter_to_modify]['description']),
                    inquirer.List('dtype', message='Please choose a data-type for the parameter to be modified', choices=dtypes, default=[self.parameters[parameter_to_modify]['dtype']], carousel = True),
                    inquirer.Text('default_value', 'Please enter the default value for the parameter to be modified', default=self.parameters[parameter_to_modify]['default_value']),
                    inquirer.Checkbox('solvers', message='Please choose the solvers this parameter controls', choices = ['abaqus','fluent','mpcci'], carousel=True,default=self.parameters[parameter_to_modify]['solvers'])]

        # Loop until new name is unique
        while True:
            print('The following names are already in use: {}'.format([name for name in self.parameters.keys() if name is not parameter_to_modify]))
            answers = inquirer.prompt(questions)

            # Convert default value **************WILL NEED TO BE UPDATED*****************
            if answers['dtype'] == 'int':
                answers['default_value'] = int(answers['default_value'])
            else:
                answers['default_value'] = float(answers['default_value'])
            

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
            elif answers['name'] in [name for name in self.parameters.keys() if name is not parameter_to_modify]:
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(answers['name']))
                print('---------------------------------------------------')

            # Check description only uses allowed characters
            elif not (set(answers['description']) <= self.allowed_characters['description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(answers['description']))
                print('---------------------------------------------------')

            # Check at least one file has been chosen
            elif not answers['solvers']:
                print('---------------------------------------------------')
                print('ERROR: No Solver chosen')
                print('---------------------------------------------------')

            else:
                
                self.delete_parameter(parameter_to_modify)

                self.parameters[answers['name']] = answers

                break
        

    def delete_parameter(self, parameter_to_delete):
        '''
        Delete a parameter from the parameter dictionary
        '''
        _ = self.parameters.pop(parameter_to_delete)


    def load_parameters(self):
        '''
        Try to load the parameters for the material from a file, if it does not exist prompt the user to specify the parameters
        '''
        try:
            # Read parameters
            with open(os.path.join(self.fpath,'parameters.json'),'r') as f:
                self.parameters = json.load(f)
                
            # Delete file from directory
            os.remove(os.path.join(self.fpath,'parameters.json'))

            self.get_all_files()
            
                
        except:
            # If no file to read have the user set the parameters
            self.get_all_files()

            self.define_parameters()


    def load_requirements(self):
        '''
        Try to load the requirements for the Material from a file, if it does not exist prompt the user to specify the requirements
        '''
        try:
            # Read requirements
            with open(os.path.join(self.fpath,'requirements.json'),'r') as f:
                self.requirements = json.load(f)
                
            # Delete file from directory
            os.remove(os.path.join(self.fpath,'requirements.json'))
                
        except:
            # If no file to read have the user set the requirements
            self.set_requirements()
        
        
    def set_requirements(self, reset_requirements = False):
        '''
        
        '''
        # Set the default requirement dict if it does not exist
        if (not hasattr(self, 'requirements')) or reset_requirements:
            self.requirements = {}
            self.requirements['material'] = self.builder.requirements['material']
            
        
        # Check if files exist in directory
        change_made = False
        for requirement_name in self.requirements['material'].keys():
            if os.path.exists(os.path.join(self.fpath,requirement_name+'.inp')):
                self.requirements['material'][requirement_name] = True
                change_made = True

        if not change_made:
            # Build questions object
            questions = [inquirer.List('material',
                                        message = 'Please choose the valid material type',
                                        choices = ['abaqus_solid', 'abaqus_acoustic'],
                                        carousel = True,
                                        default = [key for key in self.requirements['material'].keys() if self.requirements['material'][key]])]
            

            # Get answers to questions
            answers = inquirer.prompt(questions)


            # Set requirements according to answers
            for requirement_type in self.requirements.keys():

                for requirement in self.requirements[requirement_type].keys():

                    self.requirements[requirement_type][requirement] = requirement in answers[requirement_type]


    def get_all_files(self):
        '''
        ---------------------------------------------------
        Get all files in the filepath
        ---------------------------------------------------
        '''

        object_files = glob(os.path.join(self.fpath,'**','*.*'), recursive=True)
        
        self.files = [self.builder.get_relative_fpath(file,self.fpath) for file in object_files]