import os
from shutil import copytree
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
import json
from glob import glob
from copy import deepcopy

from HazelsAwesomeTheme import red_text,green_text,blue_text,yellow_text
from HazelsAwesomeTheme import HazelsAwesomeTheme as Theme


class Parent_Object:
    '''
    ------------------------------------------------------------
        ***Parent Object Class***
    ------------------------------------------------------------
        **Attributes**
    ------------------------------------------------------------
    name : str
        The name of the object.

    builder : Modular_Abaqus_Builder Class
        The database Class that contains this object.
    
    description : str
        A short description of what the object is.

    fpath : str
        File path to the objects data.

    files : list
        A list of all files stored in the filepath. Stored relative to fpath.

    requirements : dict
        A dictionary containing the requirements dictionary.

    parameters : dict
        A dictionary containing the parameters that can be modified when creating models.

    ------------------------------------------------------------
        **Methods**
    ------------------------------------------------------------
    ----------------------------------------
        Setting Attributes
    ----------------------------------------

    new_object_name():

    new_description():

    get_file_path():

    load_requirements():

    set_requirements(reset_requirements=False):

    load_parameters():

    define_parameters():

    choose_parameter(command):

    add_parameter(parameter_to_modify={}):

    delete_parameter(parameter_to_delete):

    load_requirements():

    ----------------------------------------
        Validations
    ----------------------------------------

    validate_name(_, name):

    validate_description(_, description):

    validate_fpath(fpath):

    validate_parameter_name(_, name):

    validate_parameter_description(_, description):

    validate_parameter_dtype(_, dtype):

    validate_parameter_value(answers, value):

    validate_parameter_solvers(_, solvers):

    ----------------------------------------
        Other
    ----------------------------------------

    move_folder(source_fpath, destination_fpath):

    get_all_files():

    ------------------------------------------------------------
    '''
    
    def __init__(self, builder, object_type = ''):
        '''
        ---------------------------------------------------
        Initialise the Object class
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        builder : Modular_Abaqus_Builder
            The Modular_Abaqus_Builder class used to create this class.
        ---------------------------------------------------
        '''
        self.object_type = object_type

        print('-'*60)
        print('Create {} Object operation started.'.format(blue_text(self.object_type)))
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        self.new_object_name()

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths[object_type],self.name)
        
        if os.path.exists(self.fpath):
            print(red_text('File path "{}", already exists.'.format(self.fpath)))
            raise FileExistsError
        
        print('File path set to "{}".'.format(blue_text(self.fpath)))

        self.new_description()
        
        source_fpath = self.get_file_path()
        
        # Return error if fpath not specified
        if (not source_fpath) or (not self.validate_fpath(source_fpath)):
            print(red_text('ERROR: A valid file path was not selected.'))
            print(red_text('Returning to edit objects loop.'))
            raise FileNotFoundError
        
        if len(source_fpath) < 35:
            print('The file path: "{}" to source files from was successfully chosen.'.format(blue_text(source_fpath)))
        else:
            shortened_fpath = os.path.join('...',os.path.join('',*source_fpath.split('/')[-4:]))
            print('The file path: "{}" to source files from was successfully chosen.'.format(blue_text(shortened_fpath)))

        self.move_folder(source_fpath, self.fpath)

        self.load_parameters() 

        self.get_all_files()
    
    '''
    ----------------------------------------
        Setting Attributes
    ----------------------------------------
    '''

    def new_object_name(self):
        '''
        ---------------------------------------------------
        Gets a new Object name, ensures that no object already exists of that type
        ---------------------------------------------------
        '''
        # Get current names
        current_names = list(self.builder.data[self.object_type].keys())
        if hasattr(self, 'name'): current_names.remove(self.name)
        
        print('-'*60)
        print('Please enter a new ' + blue_text('name') + ' for the ' + blue_text(self.object_type) + ' Object to be created: ')
        print('Note: ')
        print('- It must only use lowercase letters, numbers, underscores and hyphens.')
        print('- It must have fewer than 30 characters')
        print('- It must be unique.')
        print('- To cancel the create object process, enter nothing.')
        print('-'*60)
        if len(current_names):
            print('The {} names currently in use are listed below: '.format(self.object_type))
            print('"'+'", "'.join([blue_text(name) for name in current_names])+'"')
            print('-'*60)
        else:
            print('No {} names currently in use.'.format(self.object_type))
            print('-'*60)
        
        object_name = inquirer.prompt([inquirer.Text('object_name', 
                                                     'Enter the ' + blue_text('name') + ' of the new object', 
                                                     validate = self.validate_name)], 
                                                     theme=Theme())['object_name']

        if not object_name:
            print('-'*60)
            print(yellow_text('Cancel command given.'))
            raise NameError
        
        else: 
            print('-'*60)
            print(green_text('The name: "{}" for the new object has been selected.'.format(object_name)))

        self.name = object_name
        return
                
                
    def new_description(self):
        '''
        ---------------------------------------------------
        Provide a description for the Object added to the database.
        ---------------------------------------------------
        '''

        print('-'*60)
        print('Please enter a short ' + blue_text('description') + ' of the new object:')
        print('Note: ')
        print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.! ()[]\'')
        print('- It must have fewer than 100 characters')
        print('- It must be unique.')
        print('-'*60)
        
        description = inquirer.prompt([inquirer.Text('description', 
                                                     'Please enter a short ' + blue_text('description') + ' of the new object', 
                                                     validate = self.validate_description)], theme=Theme())['description']

        print('-'*60)
        print(green_text('The description: "{}" for the new object has been selected.'.format(description)))
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
        print('-'*60)
        # Create window and remove from view
        root = Tk()
        root.iconbitmap('cade.ico')
        root.overrideredirect(1)
        root.geometry('0x0+0+0')
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        
        # Get filepath from askdirectory dialog
        file_path = askdirectory(title = 'Select folder to read {} files from: '.format(self.object_type), initialdir=os.path.abspath(os.getcwd()))

        root.destroy()
        
        return file_path
    

    def load_parameters(self):
        '''
        ---------------------------------------------------
        Try to load the parameters for the object from a file, if it does not exist prompt the user to specify the parameters.
        ---------------------------------------------------
        '''
        self.parameters = {}
        if os.path.exists(os.path.join(self.fpath,'parameters.json')):
            print('-'*60)
            # Read parameters
            with open(os.path.join(self.fpath,'parameters.json'),'r') as f:
                self.parameters = json.load(f)
                print(green_text('Loaded parameters from "parameters.json".'))
                
            # Delete file from directory
            os.remove(os.path.join(self.fpath,'parameters.json'))
  
        else:
            print('-'*60)
            print(yellow_text('No "parameters.json" in source filepath.'))
            self.define_parameters()


    def define_parameters(self):
        '''
        ---------------------------------------------------
        Used to add, modify and delete parameters from the object
        ---------------------------------------------------
        '''
        command = 'add'
        
        while command != 'done':
            
            print('-'*60)
            # Get parameter type or exit choosing parameter command
            command = inquirer.prompt([inquirer.List('command',
                                                     'Add more '+ blue_text('parameters') + ' or exit dialog', 
                                                     choices=['add', 'modify', 'delete', 'done'], 
                                                     carousel = True,
                                                     default=command)], theme=Theme())['command']
            
            if command == 'add':
                self.add_parameter()

            elif command == 'modify':
                parameter_to_modify_name = self.choose_parameter('modify')

                if parameter_to_modify_name: self.add_parameter(self.parameters.pop(parameter_to_modify_name))

            elif command == 'delete':
                parameter_to_delete = self.choose_parameter('delete')

                if parameter_to_delete: self.delete_parameter(parameter_to_delete)

        print('-'*60)
        print(green_text('Exiting Choose parameter dialog.'))
        print('-'*60)
        print(green_text('Parameters chosen for the {}, "{}" are: '.format(self.object_type, self.name))) if len(self.parameters.keys()) else print('No parameters chosen.')

        # Print all parameters added
        for parameter in self.parameters.keys():
            print('-'*60)
            print('Name: "{}"'.format(blue_text(self.parameters[parameter]['name'])))
            print('\tDescription: "{}"'.format(self.parameters[parameter]['description']))
            print('\tData-type: "{}"'.format(self.parameters[parameter]['dtype']))
            print('\tDefault Value: "{}"'.format(blue_text(self.parameters[parameter]['default_value'])))
            print('\tSolvers: ')
            for solver in self.parameters[parameter]['solvers']:
                print('\t\t"{}"'.format(solver))


    def choose_parameter(self, command):
        '''
        ---------------------------------------------------
        Prompts the user to choose a parameter currently stored in the object.
        ---------------------------------------------------
        Variables
        ---------------------------------------------------
        command : str
            Used to alter the string shown to the user when choosing a parameter
        ---------------------------------------------------
        '''
        # Get parameter names
        parameters = [params for params in self.parameters.keys()]
        print('-'*60)

        # Check if empty
        if parameters: 
            parameters.append('cancel')
            # Ask user which parameter to select
            chosen_parameter = inquirer.prompt([inquirer.List('parameter','Choose parameter to {}'.format(blue_text(command)), choices=parameters, carousel = True)], theme=Theme())['parameter']

            if chosen_parameter == 'cancel':
                print('-'*60)
                print(yellow_text('Parameter {} command cancelled, returning to loop.'.format(command)))
                return ''
            
            else:
                print('-'*60)
                print(green_text('Parameter "{}" chosen to {}, returning to loop.'.format(chosen_parameter, command)))
                return chosen_parameter
                    
        else:
            print(red_text('No parameters to pick, returning to loop.'))
            return ''


    def add_parameter(self, parameter_to_modify={}):
        '''
        ---------------------------------------------------
        Prompts the user to add a parameter to the object
        ---------------------------------------------------
        '''  

        # Get current names
        current_names = list(self.parameters.keys())
        
        print('-'*60)   
        print('Please enter a new ' + blue_text('parameter name') + '.')
        print('Note: ')
        print('- It must only use lowercase letters, numbers, underscores and hyphens.')
        print('- It must have fewer than 30 characters')
        print('- It must be unique.')
        print('-'*60)
        if len(current_names):
            print('The parameters added to the object currently are:')
            print('"'+'", "'.join([blue_text(name) for name in current_names])+'"')
            print('-'*60)
        else:
            print('No Parameters currently added')
            print('-'*60)


        questions = [inquirer.Text('name', 
                                   message='Please enter a ' + blue_text('name') + ' for the parameter', 
                                   validate=self.validate_parameter_name,
                                   default=parameter_to_modify['name'] if parameter_to_modify else None),
                    inquirer.Text('description', 
                                  message='Please enter a ' + blue_text('short description') + ' of the parameter', 
                                  validate=self.validate_parameter_description,
                                  default=parameter_to_modify['description'] if parameter_to_modify else None),
                    inquirer.List('dtype', 
                                  message='Please choose a ' + blue_text('data type') + ' for the parameter', 
                                  choices=['int', 'float'], 
                                  carousel = True, 
                                  validate=self.validate_parameter_dtype,
                                  default=parameter_to_modify['dtype'] if parameter_to_modify else None),
                    inquirer.Text('default_value', 
                                  'Please enter the ' + blue_text('default value') + ' (dtype = "' + blue_text('{dtype}') + '")', 
                                  validate=self.validate_parameter_value,
                                  default=parameter_to_modify['default_value'] if parameter_to_modify else None),
                    inquirer.Checkbox('solvers', 
                                      message='Please choose the ' + blue_text('solvers') + ' this parameter controls', 
                                      choices = ['abaqus','fluent','mpcci'], 
                                      carousel=True, 
                                      validate=self.validate_parameter_solvers,
                                      default=parameter_to_modify['solvers'] if parameter_to_modify else None)]


        answers = inquirer.prompt(questions, theme=Theme())
        print('-'*60)
        print(green_text('Solvers chosen: "'+'", "'.join(answers['solvers'])+'"'))

        answers['default_value'] = float(answers['default_value']) if answers['dtype'] == 'float' else int(answers['default_value'])
        self.parameters[answers['name']] = answers
        

    def delete_parameter(self, parameter_to_delete):
        '''
        ---------------------------------------------------
        Delete a parameter from the parameter dictionary
        ---------------------------------------------------
        '''
        print('-'*60)
        _ = self.parameters.pop(parameter_to_delete)
        print(green_text('Successfully deleted parameter "{}".'.format(parameter_to_delete)))


    def load_requirements(self):
        '''
        ---------------------------------------------------
        Try to load the requirements for the object from a file included in the source_fpath, if it does not exist prompt the user to specify the requirements.
        ---------------------------------------------------
        '''
        print('-'*60)
        if os.path.exists(os.path.join(self.fpath,'requirements.json')):
            with open(os.path.join(self.fpath,'requirements.json'),'r') as f:
                self.requirements = json.load(f)

            print(green_text('Loaded requirements from "requirements.json".'))
            os.remove(os.path.join(self.fpath,'requirements.json'))
                
        else:
            print(yellow_text('No "requirements.json" in directory.'))
            self.set_requirements()


    def set_requirements(self):
        '''
        ---------------------------------------------------
        Placeholder method for child object classes
        ---------------------------------------------------
        '''
        pass

    '''
    ----------------------------------------
        Validations
    ----------------------------------------
    '''    

    def validate_name(self, _, name):
        '''
        
        '''

        current_names = list(self.builder.data[self.object_type].keys())

        # Cancel command given
        if not name:
            return True
        
        # If name meets requirements
        if (len(name) < 30):
            if (set(name) <= self.builder.allowed_characters['name']):
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


    def validate_description(self, _, description):

        # If description meets requirements
        if (len(description) < 100):
            if (set(description) <= self.builder.allowed_characters['description']):
                return True
            else:
                print(red_text('\nEntered description contains non-valid characters.'))
                return False
        else:
            print(red_text('\nEntered description has a length of {} which is greater than the max length of 100.'.format(len(description))))
            return False


    def validate_fpath(self, fpath):
        '''

        '''
        files_in_path = glob(os.path.join(fpath,'**','*.*'), recursive=True)
        extensions = set([os.path.split(file)[1].split('.')[1] for file in files_in_path if os.path.split(file)[1]])

        allowed_extensions = set(['inp','msh','json','jou','csp','py'])

        if extensions >= allowed_extensions:
            print(red_text('The filepath chosen was not valid as it contains unsupported file extensions.'))
            return False
        
        return True

    
    def validate_parameter_name(self, _, name):
        '''
        
        '''

        current_names = list(self.parameters.keys())
        
        # If name meets requirements
        if (len(name) < 30):
            if (set(name) <= self.builder.allowed_characters['name']):
                if (name not in current_names):
                    print('\n'+'-'*60)
                    print(green_text('Name: "{}" chosen.'.format(name)))
                    print('-'*60)
                    return True
                else:
                    print(red_text('\nName: "{}" is already in use by another parameter'.format(name)))
                    return False
            else:
                print(red_text('\nEntered name contains non-valid characters.'.format(name)))
                return False
        else:
            print(red_text('\nEntered name has a length of {} which is greater than the max length of 30.'.format(len(name))))
            return False


    def validate_parameter_description(self, _, description):

        # If description meets requirements
        if (len(description) < 100):
            if (set(description) <= self.builder.allowed_characters['description']):
                print('\n'+'-'*60)
                print(green_text('Description: "{}" chosen.'.format(description)))
                print('-'*60)
                return True
            else:
                print(red_text('\nEntered description contains non-valid characters.'))
                return False
        else:
            print(red_text('\nEntered description has a length of {} which is greater than the max length of 100.'.format(len(description))))
            return False


    def validate_parameter_dtype(self, _, dtype):
        print('\n'+'-'*60)
        print(green_text('Data type: "{}" chosen.'.format(dtype)))
        print('-'*60)
        return True


    def validate_parameter_value(self, answers, value):
        
        # Check parameter value matches entered datatype
        if answers['dtype'] == 'int':
            if value.isnumeric():
                print('\n'+'-'*60)
                print(green_text('Value: "{}" chosen.'.format(value)))
                print('-'*60)
                return True
            else:
                print(red_text('\nThe entered value is not a valid integer'))
        else:
            try:
                float(value)
                print('\n'+'-'*60)
                print(green_text('Value: "{}" chosen.'.format(value)))
                print('-'*60)
                return True
            except ValueError:
                print(red_text('\nThe entered value is not a valid float'))
                return False


    def validate_parameter_solvers(self, _, solvers):
        if len(solvers):
            return True
        print(red_text('At least one solver must be chosen\n\n\n\n'))
        raise inquirer.errors.ValidationError([], reason=' ')

    
    def validate_requirements(self, _, notused):
        print('\n'+'-'*60)
        return True
        
        
    '''
    ----------------------------------------
        Other
    ----------------------------------------
    '''

    def move_folder(self, source_fpath, destination_fpath):
        '''
        ---------------------------------------------------
        Moves a folder from a source path to a destination path
        ---------------------------------------------------
        '''
        copytree(source_fpath, destination_fpath, symlinks=True)

        if os.path.isabs(source_fpath):
            source_fpath = os.path.join('...',os.path.join('',*source_fpath.split('/')[-4:]))

        print(green_text('Successfully copied files from:\n"{}" -> "{}"'.format(source_fpath, destination_fpath)))

    
    def get_all_files(self):
        '''
        ---------------------------------------------------
        Get all files in the filepath
        ---------------------------------------------------
        '''

        object_files = glob(os.path.join(self.fpath,'**','*.*'), recursive=True)

        self.files = [self.builder.get_relative_fpath(file,self.fpath) for file in object_files if (('requirements.json' not in file) and ('parameters.json' not in file))]



class Analysis_Object(Parent_Object):
    def __init__(self, builder, object_type='analysis'):
        super().__init__(builder, object_type)

        self.load_requirements()

        print('-'*60)
        print(green_text('Create analysis object operation successful.'))
        
        
    def set_requirements(self, reset_requirements=False):
        '''
        ---------------------------------------------------
        Prompts the user to set the requirements for this Analysis object
        ---------------------------------------------------
        '''
        # Set the default requirement dict if it does not exist or if found to be invalid
        if (not hasattr(self, 'requirements')) or reset_requirements:
            self.requirements = self.builder.requirements
        
        # Build questions object
        questions = [inquirer.Checkbox('software',
                                       message = 'Please choose the ' + blue_text('softwares') + ' required for this analysis',
                                       choices = list(self.builder.requirements['software'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['software'].keys() if self.requirements['software'][key]],
                                       validate = self.validate_requirements),
                     inquirer.Checkbox('geometry',
                                       message = 'Please enter the ' + blue_text('geometry types') + ' required for this analysis',
                                       choices = list(self.builder.requirements['geometry'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['geometry'].keys() if self.requirements['geometry'][key]],
                                       validate = self.validate_requirements),
                     inquirer.Checkbox('material',
                                       message = 'Please choose the ' + blue_text('materials') + ' required for this analysis',
                                       choices = list(self.builder.requirements['material'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['material'].keys() if self.requirements['material'][key]],
                                       validate = self.validate_requirements),
                     inquirer.Checkbox('analysis',
                                       message = 'Please choose the ' + blue_text('additional analysis components') + ' required for this analysis',
                                       choices = list(self.builder.requirements['analysis'].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements['analysis'].keys() if self.requirements['analysis'][key]])]
        
        print('-'*60)
        # Get answers to questions
        answers = inquirer.prompt(questions, theme=Theme())
        print('-'*60)


        # Set requirements according to answers
        for requirement_type in self.requirements.keys():
            for requirement in self.requirements[requirement_type].keys():
                self.requirements[requirement_type][requirement] = requirement in answers[requirement_type]

        print(green_text('Requirements set successfully.'))



class Geometry_Object(Parent_Object):
    def __init__(self, builder, object_type='geometry'):
        super().__init__(builder, object_type)

        self.load_requirements()

        print('-'*60)
        print(green_text('Create geometry object operation successful.'))
        
        
    def set_requirements(self, reset_requirements = False):
        '''
        
        '''
        # Set the default requirement dict if it does not exist
        if (not hasattr(self, 'requirements')) or reset_requirements:
            self.requirements = {}
            self.requirements[self.object_type] = self.builder.requirements[self.object_type]
            
        # Check if files exist in directory
        change_made = False
        for requirement_name in self.requirements[self.object_type].keys():
            if ('abaqus' in requirement_name) or ('assembly' in requirement_name):
                if os.path.exists(os.path.join(self.fpath,requirement_name+'.inp')):
                    self.requirements[self.object_type][requirement_name] = True
                    print(green_text('Automatically detected the file: "{}".'.format(requirement_name+'.inp')))
                    change_made = True
            else:
                if os.path.exists(os.path.join(self.fpath,requirement_name+'.msh')):
                    self.requirements[self.object_type][requirement_name] = True
                    print(green_text('Automatically detected the file: "{}".'.format(requirement_name+'.msh')))
                    change_made = True
        
        # If file names dont match then prompt user
        if change_made:
            print(green_text('Automatically detected the requirements based on files in the selected folder.'))
            return
        else:
            print('-'*60)
            print(red_text('No requirements automatically detected, you can select the requirements, but it is recommended to use a "requirements.json" file.'))
            print('-'*60)
            questions = [inquirer.Checkbox('geometry',
                                           message = 'Please choose the Requirements fulfilled by this object',
                                           choices = list(self.builder.requirements[self.object_type].keys()),
                                           carousel = True,
                                           default = [key for key in self.requirements[self.object_type].keys() if self.requirements[self.object_type][key]])]
            
            answers = inquirer.prompt(questions, theme=Theme())
            print('-'*60)

            for requirement_type in self.requirements.keys():
                for requirement in self.requirements[requirement_type].keys():
                    self.requirements[requirement_type][requirement] = requirement in answers[requirement_type]

            print(green_text('Requirements set successfully.'))



class Material_Object(Parent_Object):
    def __init__(self, builder, object_type='material'):
        super().__init__(builder, object_type)

        self.load_requirements()

        print('-'*60)
        print(green_text('Create material object operation successful.'))
 
        
    def set_requirements(self, reset_requirements = False):
        '''
        
        '''
        # Set the default requirement dict if it does not exist
        if (not hasattr(self, 'requirements')) or reset_requirements:
            self.requirements = {}
            self.requirements[self.object_type] = self.builder.requirements[self.object_type]
            
        
        # Check if files exist in directory
        change_made = False
        for requirement_name in self.requirements[self.object_type].keys():
            if os.path.exists(os.path.join(self.fpath,requirement_name+'.inp')):
                self.requirements[self.object_type][requirement_name] = True
                print(green_text('Automatically detected the file: "{}".'.format(requirement_name+'.inp')))
                change_made = True

        if change_made:
            print(green_text('Automatically detected the requirements based on files in the selected folder.'))
            return
        else:
            print('-'*60)
            print(red_text('No requirements automatically detected, you can select the requirements, but it is recommended to use a "requirements.json" file.'))
            print('-'*60)
            questions = [inquirer.List('material',
                                       message = 'Please choose the valid material type',
                                       choices = list(self.builder.requirements[self.object_type].keys()),
                                       carousel = True,
                                       default = [key for key in self.requirements[self.object_type].keys() if self.requirements[self.object_type][key]])]
            
            answers = inquirer.prompt(questions, theme=Theme())
            print('-'*60)

            for requirement_type in self.requirements.keys():
                for requirement in self.requirements[requirement_type].keys():
                    self.requirements[requirement_type][requirement] = requirement in answers[requirement_type]

            print(green_text('Requirements set successfully.'))