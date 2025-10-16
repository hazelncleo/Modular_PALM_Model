import os
from shutil import copytree
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
import json
from glob import glob

from HazelsAwesomeTheme import red_text,green_text,blue_text,yellow_text
from HazelsAwesomeTheme import HazelsAwesomeTheme as Theme

class Analysis_Object:
    '''
    ---------------------------------------------------
    Contains all the relevant information for an Analysis Object
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
        Initialise the Analysis Object class
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        builder : Modular_Abaqus_Builder
            The Modular_Abaqus_Builder class used to create this class.
        ---------------------------------------------------
        '''
        
        print('-'*60)
        print('Create Analysis Object operation started.')
        print('-'*60)
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        # Specify allowed characters for certain attributes
        self.allowed_characters = self.builder.allowed_characters
        
        self.new_object_name()

        if not self.name:
            return

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths['analysis'],self.name)
        print('File path set to "{}".'.format(blue_text(self.fpath)))

        self.new_description()
        
        source_fpath = self.get_file_path()
        
        # Return error if fpath not specified
        if not source_fpath:
            print(red_text('ERROR: A valid file path was not selected.'))
            print(red_text('Returning to edit objects loop.'))
            raise FileNotFoundError
        
        self.validate_fpath(source_fpath)
        
        if len(source_fpath) < 35:
            print('The file path: "{}" to source files from was successfully chosen.'.format(blue_text(source_fpath)))
        else:
            shortened_fpath = os.path.join('...',os.path.join('',*source_fpath.split('/')[-4:]))
            print('The file path: "{}" to source files from was successfully chosen.'.format(blue_text(shortened_fpath)))

        self.move_folder(source_fpath, self.fpath)
        
        self.load_requirements()

        self.parameters = {}
        self.load_parameters() 
        
        
        print('-'*60)
        print(green_text('Create Analysis object operation successful.'))
        print('-'*60)
    

    def move_folder(self, source_fpath, destination_fpath):
        '''
        ---------------------------------------------------
        Moves a folder from a source path to a destination path
        ---------------------------------------------------
        '''
        copytree(source_fpath, destination_fpath, symlinks=True)

        if os.path.isabs(source_fpath):
            source_fpath = os.path.join('...',os.path.join('',*source_fpath.split('/')[-4:]))

        print(green_text('Successfully copied files from:\n\t"{}" -> "{}"'.format(source_fpath, destination_fpath)))

    
    def new_object_name(self):
        '''
        ---------------------------------------------------
        Gets a new Analysis Object name, ensures that no object already exists of that type
        ---------------------------------------------------
        '''
        # Get current names
        current_names = list(self.builder.data['analysis'].keys())

        print('Please enter a new name for the Analysis Object to be created: ')
        print('Note: ')
        print('- It must only use lowercase letters, numbers, underscores and hyphens.')
        print('- It must have fewer than 30 characters')
        print('- It must be unique.')
        print('- To cancel the create object process, enter nothing.')
        print('-'*60)
        if len(current_names):
            print('The Analysis names currently in use are listed below: ')
            print('"'+'", "'.join([blue_text(name) for name in current_names])+'"')
            print('-'*60)
        else:
            print('No Analysis names currently in use.')
        
        questions = [inquirer.Text('object_name', 'Enter the name of the new object', validate = self.validate_name)]
        object_name = inquirer.prompt(questions, theme=Theme())['object_name']

        if not object_name:
            print('-'*60)
            print(yellow_text('Cancel command given.'))
            print('-'*60)
        
        else: 
            print('-'*60)
            print(green_text('The name: "{}" for the new object has been selected.'.format(object_name)))

        self.name = object_name
        return
                
                
    def new_description(self):
        '''
        ---------------------------------------------------
        Provide a description for the Analysis Object added to the database.
        ---------------------------------------------------
        '''

        print('-'*60)
        print('Please enter a short description of the new object:')
        print('Note: ')
        print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.! ()[]\'')
        print('- It must have fewer than 100 characters')
        print('- It must be unique.')
        print('-'*60)
        
        questions = [inquirer.Text('description', 'Please enter a short description of the new object', validate = self.validate_description)]
        description = inquirer.prompt(questions, theme=Theme())['description']

        print('-'*60)
        print(green_text('The description: "{}" for the new object has been selected.'.format(description)))
        print('-'*60)
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
        file_path = askdirectory(title = 'Select folder to read Analysis files from: ', initialdir=os.path.abspath(os.getcwd()))

        root.destroy()
        
        return file_path
    

    def define_parameters(self):
        '''
        ---------------------------------------------------
        Used to add, modify and delete parameters from the object
        ---------------------------------------------------
        '''
        commands = ['add', 'modify', 'delete', 'exit']

        while True:

            # Get parameter type or exit choosing parameter command
            command = inquirer.list_input('Add more parameters or exit choose parameter dialog?', choices=commands, carousel = True)

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
        Prompts the user to add a parameter to the object
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
            elif not (set(answers['name']) <= self.allowed_characters['Name']):
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

            # Check at least one solver has been chosen
            elif not answers['solvers']:
                print('---------------------------------------------------')
                print('ERROR: No Solver chosen')
                print('---------------------------------------------------')

            else:
                self.parameters[answers['name']] = answers
                break


    def choose_parameter(self, command):
        '''
        ---------------------------------------------------
        Prompts the user to choose a parameter currently stored in the analysis object.
        ---------------------------------------------------
        Variables
        ---------------------------------------------------
        command : str
            Used to alter the string shown to the user when choosing a parameter
        ---------------------------------------------------
        '''
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
        Prompts the user to modify a parameter 
        ---------------------------------------------------
        Variables
        ---------------------------------------------------
        parameter_to_modify : str
            The name of the parameter to modify
        ---------------------------------------------------
        '''

        dtypes = ['int', 'float']
                                                                     
        questions = [inquirer.Text('name', message='Please enter a new name for the parameter to be modified', default=parameter_to_modify),
                    inquirer.Text('description', message='Please enter a description of the parameter to be modified', default=self.parameters[parameter_to_modify]['description']),
                    inquirer.List('dtype', message='Please choose a data-type for the parameter to be modified', choices=dtypes, default=[self.parameters[parameter_to_modify]['dtype']], carousel = True),
                    inquirer.Text('default_value', 'Please enter the default value for the parameter to be modified', default=self.parameters[parameter_to_modify]['default_value']),
                    inquirer.Checkbox('solvers', message='Please choose the solvers this parameter controls', choices = ['abaqus','fluent','mpcci'], carousel=True, default=self.parameters[parameter_to_modify]['solvers'])]

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
            elif not (set(answers['name']) <= self.allowed_characters['Name']):
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", is not entirely letters, numbers or underscores and hyphens.'.format(answers['name']))
                print('---------------------------------------------------')
            
            # Check name is unique
            elif answers['name'] in [name for name in self.parameters.keys() if name is not parameter_to_modify]:
                print('---------------------------------------------------')
                print('ERROR: The name: "{}", already exists in the database.'.format(answers['name']))
                print('---------------------------------------------------')

            # Check description only uses allowed characters
            elif not (set(answers['description']) <= self.allowed_characters['Description']):
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
        ---------------------------------------------------
        Delete a parameter from the parameter dictionary
        ---------------------------------------------------
        '''
        _ = self.parameters.pop(parameter_to_delete)


    def load_parameters(self):
        '''
        ---------------------------------------------------
        Try to load the parameters for the analysis from a file, if it does not exist prompt the user to specify the parameters.
        ---------------------------------------------------
        '''
        if os.path.exists(os.path.join(self.fpath,'parameters.json')):
            # Read parameters
            with open(os.path.join(self.fpath,'parameters.json'),'r') as f:
                self.parameters = json.load(f)
                print(green_text('Loaded parameters from "parameters.json".'))
                
            # Delete file from directory
            os.remove(os.path.join(self.fpath,'parameters.json'))

            self.get_all_files()
                  
        else:
            # If no file to read have the user set the parameters
            self.get_all_files()

            self.define_parameters()


    def load_requirements(self):
        '''
        ---------------------------------------------------
        Try to load the requirements for the analysis from a file, if it does not exist prompt the user to specify the requirements.
        ---------------------------------------------------
        '''
        try:
            # Read requirements
            with open(os.path.join(self.fpath,'requirements.json'),'r') as f:
                self.requirements = json.load(f)
                print(green_text('Loaded requirements from "requirements.json".'))
                
            # Delete file from directory
            os.remove(os.path.join(self.fpath,'requirements.json'))
                
        except:
            # If no file to read have the user set the requirements
            print(yellow_text('No "requirements.json" in directory.\nPlease enter the requirements.'))
            self.set_requirements()
        
        
    def set_requirements(self, reset_requirements = False):
        '''
        ---------------------------------------------------
        Prompts the user to set the requirements for this Analysis object
        ---------------------------------------------------
        '''
        # Set the default requirement dict if it does not exist
        if (not hasattr(self, 'requirements')) or reset_requirements:
            self.requirements = self.builder.requirements
        
        # Build questions object
        questions = [inquirer.Checkbox('softwares',
                                       message = 'Please choose the softwares required for this analysis',
                                       choices = list(self.builder.requirements['softwares'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['softwares'].keys() if self.requirements['softwares'][key]]),
                     inquirer.Checkbox('geometries',
                                       message = 'Please enter the geometries required for this analysis',
                                       choices = list(self.builder.requirements['geometries'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['geometries'].keys() if self.requirements['geometries'][key]]),
                     inquirer.Checkbox('materials',
                                       message = 'Please choose the materials required for this analysis',
                                       choices = list(self.builder.requirements['materials'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['materials'].keys() if self.requirements['materials'][key]]),
                     inquirer.Checkbox('analysis',
                                       message = 'Please choose the additional components required for this analysis',
                                       choices = list(self.builder.requirements['analysis'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['analysis'].keys() if self.requirements['analysis'][key]])]
        

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

    
    def validate_name(self, _, name):
        '''
        
        '''

        current_names = list(self.builder.data['analysis'].keys())

        # Cancel command given
        if not name:
            return True
        
        # If name meets requirements
        if (len(name) < 30):
            if (set(name) <= self.allowed_characters['Name']):
                if (name not in current_names):
                    return True
                else:
                    print(red_text('\nName: "{}" is already in use in the database.'.format(name)))
                    return False
            else:
                print(red_text('\nEntered name contains non-valid characters.'.format(name)))
                return False
        else:
            print(red_text('\nEntered name has a length of {} which is greater than the max length of 30.'.format(len(name))))
            return False


    def validate_fpath(self, fpath):
        '''

        '''
        files_in_path = glob(os.path.join(fpath,'**','*.*'), recursive=True)
        extensions = set([os.path.split(file)[1].split('.')[1] for file in files_in_path if os.path.split(file)[1]])

        allowed_extensions = set(['inp','msh','json','jou','csp','py'])

        if extensions >= allowed_extensions:
            print(red_text('The filepath chosen was not valid as it contains unsupported file extensions.'))
            raise FileExistsError()
        
        return
    

    def validate_description(self, _, description):

        # If description meets requirements
        if (len(description) < 100):
            if (set(description) <= self.allowed_characters['Description']):
                return True
            else:
                print(red_text('\nEntered description contains non-valid characters.'))
                return False
        else:
            print(red_text('\nEntered description has a length of {} which is greater than the max length of 100.'.format(len(description))))
            return False

    
    def validate_parameter_name(self, name):

        pass


    def validate_parameter_value(self, value, type):

        pass
