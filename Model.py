import os
from shutil import copytree
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
from copy import deepcopy


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
        self.fpath = os.path.join(self.builder.fpaths['model_files'],self.name)

        self.new_description()

        # Select Analysis
        self.select_analysis()

        # Select Geometry
        self.select_geometry()

        # Add Materials
        self.select_materials()

        # Create parameters for the model
        self.create_parameters()
        
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
        Provide a description for the Model added to the database.
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
            print('Please enter a description for the Model to be created: ')
            print('Note: ')
            print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.?! ()[]"\'')
            print('---------------------------------------------------')
            
            description = input('Please enter a description for the Model to be created: ')

            if not (set(description) <= self.allowed_characters['Description']):
                print('---------------------------------------------------')
                print('ERROR: The description: "{}", does not meet the requirements.'.format(description))
                print('---------------------------------------------------')
            
            else:
                print('---------------------------------------------------')
                print('The description: "{}", for the new Model has been selected.'.format(description))
                print('---------------------------------------------------')
                self.description = description
                return
            
    
    def select_analysis(self):
        '''
        ---------------------------------------------------
        Select an analysis object from the database for this model
        ---------------------------------------------------
        '''
        
        # Get the Analysis objects loaded in the database
        potential_analyses = [analysis for analysis in self.builder.data['analysis'].keys()]

        # THIS NEEDS TO BE CAUGHT IN THE MODULAR ABAQUS BUILDER CLASS
        if not potential_analyses:
            raise FileExistsError('No analysis objects available in the database')

        print('---------------------------------------------------')
        print('Analyses Available for use:')
        print('---------------------------------------------------')
        for analysis in potential_analyses:
            print('Name: "{}"'.format(analysis))
            print('Description: "{}"'.format(self.builder.data['analysis'][analysis].description))
            print('---------------------------------------------------')

        potential_analyses.append('cancel')

        # Prompt user to pick an analysis
        analysis_name = inquirer.list_input('Pick Analysis to use', choices=potential_analyses, carousel = True)

        if (not analysis_name) or (analysis_name == 'cancel'):
            raise NameError('Select Analysis cancelled')

        self.analysis = self.builder.data['analysis'][analysis_name]

        self.requirements = self.analysis.requirements


    def get_potential_geometries(self):
        '''
        ---------------------------------------------------
        Get a list of all the potential geometries that fulfill the requirements
        ---------------------------------------------------
        '''
        potential_geometries = []

        for geometry_name,geometry_object in self.builder.data['geometry'].items():
            
            # Check that the selected geometry fulfills all of the requirements of the analysis
            are_requirements_fulfilled = [fulfilled_requirement[1] for requirement_to_fulfill, fulfilled_requirement in zip(self.requirements['geometries'].items(),geometry_object.requirements['geometries'].items()) if requirement_to_fulfill[1]]

            # Add name if all requirements fulfilled
            if all(are_requirements_fulfilled):
                potential_geometries.append(geometry_name)

        return potential_geometries


    def select_geometry(self):
        '''
        ---------------------------------------------------
        Select a Geometry object from the database for this model
        ---------------------------------------------------
        '''
        
        # Get the Geometry objects loaded in the database
        potential_geometries = self.get_potential_geometries()
        

        # THIS NEEDS TO BE CAUGHT IN THE MODULAR ABAQUS BUILDER CLASS
        if not potential_geometries:
            raise FileExistsError('No Geometry objects that meet the requirements available in the database')
        
        print('---------------------------------------------------')
        print('The Chosen Analysis: "{}".'.format(self.analysis.name))
        print('Description: "{}"'.format(self.analysis.description))
        print('Has the following Geometry requirements: ')
        for requirement, is_required in self.requirements['geometries'].items():
            if is_required:
                print('\t{}'.format(requirement))


        print('---------------------------------------------------')
        print('The following Geometries meet the requirements: ')
        print('---------------------------------------------------')
        for geometry in potential_geometries:
            print('Name: "{}"'.format(geometry))
            print('Description: "{}"'.format(self.builder.data['geometry'][geometry].description))
            print('---------------------------------------------------')

        potential_geometries.append('cancel')

        # Prompt user to pick a Geometry
        geometry_name = inquirer.list_input('Pick Geometry to use', choices=potential_geometries, carousel = True)

        # If cancel chosen, or no geometry name given
        if (not geometry_name) or (geometry_name == 'cancel'):
            raise NameError('Select Geometry cancelled')

        # Set as model geometry
        self.geometry = self.builder.data['geometry'][geometry_name]

    
    def get_potential_materials(self):
        '''
        ---------------------------------------------------
        Get a list of all the potential materials that fulfill a requirement
        ---------------------------------------------------
        '''
        potential_materials = []

        for material_name,material_object in self.builder.data['material'].items():
            
            # Check that the selected material fulfills a requirement of the analysis
            are_requirements_fulfilled = [fulfilled_requirement[1] for requirement_to_fulfill, fulfilled_requirement in zip(self.requirements['materials'].items(),material_object.requirements['materials'].items()) if requirement_to_fulfill[1]]

            # Add name if all requirements fulfilled
            if any(are_requirements_fulfilled):
                potential_materials.append(material_name)

        return potential_materials


    def select_materials(self):
        '''
        ---------------------------------------------------
        Select Material objects from the database for this model
        ---------------------------------------------------
        '''
        
        # Get the Material objects loaded in the database
        potential_materials = self.get_potential_materials()
        
        # THIS NEEDS TO BE CAUGHT IN THE MODULAR ABAQUS BUILDER CLASS
        if not potential_materials:
            raise FileExistsError('No Material objects that meet the requirements available in the database')

        requirements_to_be_fulfilled = {}
        
        print('---------------------------------------------------')
        print('The Chosen Analysis: "{}".'.format(self.analysis.name))
        print('Description: "{}"'.format(self.analysis.description))
        print('Has the following Material requirements: ')
        for requirement, is_required in self.requirements['materials'].items():
            if is_required:
                print('\t{}'.format(requirement))
                requirements_to_be_fulfilled[requirement] = is_required


        print('---------------------------------------------------')
        print('The following Materials meet at least one of the requirements: ')
        print('---------------------------------------------------')
        for material in potential_materials:
            print('Name: "{}"'.format(material))
            print('Description: "{}"'.format(self.builder.data['material'][material].description))
            requirement_fulfilled = [requirement[0] for requirement in self.builder.data['material'][material].requirements['materials'].items() if requirement[1]]
            print('Requirement Fulfilled: {}'.format(requirement_fulfilled[0]))
            print('---------------------------------------------------')

        potential_materials.append('cancel')
        self.materials = {}

        # Loop until all requirements have been met
        while len(requirements_to_be_fulfilled):
            print('Requirements still to be fulfilled: ')
            for requirement, is_required in requirements_to_be_fulfilled.items():
                print('\t{}'.format(requirement))
            print('---------------------------------------------------')
            
            # Prompt user to pick a Material
            material_name = inquirer.list_input('Pick a Material to use', choices=potential_materials, carousel = True)

            # If cancel chosen, or no material name given
            if (not material_name) or (material_name == 'cancel'):
                raise NameError('Select Material cancelled')


            requirement_fulfilled = [fulfilled[0] for fulfilled in self.builder.data['material'][material_name].requirements['materials'].items() if fulfilled[1]][0]
            print(requirement_fulfilled)
            
            
            try:
                requirements_to_be_fulfilled.pop(requirement_fulfilled)
            except:
                print('---------------------------------------------------')
                print('The Material: "{}", fulfills a requirement that has already been fulfilled by a previously chosen material.'.format(material_name))
                print('---------------------------------------------------')
                continue
            
            potential_materials.remove(material_name)
            
            # Append to Materials
            self.materials[material_name] = self.builder.data['material'][material_name]
            


    def create_parameters(self):
        pass        