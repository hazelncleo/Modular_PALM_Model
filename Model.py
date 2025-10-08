import os
from shutil import copytree
from shutil import copyfile
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
from copy import deepcopy
from shutil import copyfileobj
from importlib import import_module


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
        if any(self.requirements['materials'].values()):
            self.select_materials()
        else:
            print('-----------------------------------------------')
            print('No Abaqus Materials required, skipping select materials')
            print('-----------------------------------------------')
            self.materials = {}

        # Get solver fpaths
        self.set_fpaths()
            
        # Copy parameters from objects and prompt user to modify their values
        self.copy_and_modify_parameters()
        
        # Move files from object fpaths to the solver fpaths
        self.move_files_from_objects()
        
        print('-----------------------------------------------')
        print('Create Model operation successful.')
        print('-----------------------------------------------')
    

    def move_object_folder(self, source_fpath, destination_fpath, dirs_exist_ok=False):
        copytree(source_fpath, destination_fpath, symlinks=True, dirs_exist_ok=dirs_exist_ok)

    
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
            

    def set_fpaths(self):
        '''
        
        '''
        
        # If all softwares required set solver fpaths accordingly.
        if all(self.requirements['softwares'].values()):
            self.solver_fpaths = {'abaqus' : os.path.join(self.fpath,'abaqus'),
                                  'fluent' : os.path.join(self.fpath,'fluent'),
                                  'mpcci' : os.path.join(self.fpath,'mpcci')}
            return
            
        # If only abaqus
        elif self.requirements['softwares']['abaqus']:
            self.solver_fpaths = {'abaqus' : self.fpath,
                                  'fluent' : None,
                                  'mpcci' : None}
            return
        
        # If only fluent
        elif self.requirements['softwares']['fluent']:
            self.solver_fpaths = {'abaqus' : None,
                                  'fluent' : self.fpath,
                                  'mpcci' : None}
            return
        
        else:
            print('---------------------------------------------------')
            print('Software Requirements are not valid.')
            print('---------------------------------------------------')
            raise ValueError('Software Requirements are not valid.')


    def print_model_parameter_info(self):
        '''
        
        '''

        self.parameters = {}

        # Print parameters of the analysis object
        print('---------------------------------------------------')
        print('The Chosen Analysis: "{}".'.format(self.analysis.name))
        print('Has the following Parameters that can be changed: ')
        for parameter_name,parameter in self.analysis.parameters.items():
                    print('---------------------------------------------------')
                    print('Name: {}'.format(parameter_name))
                    print('\tDescription: {}'.format(parameter['description']))
                    print('\tData-type: {}'.format(parameter['dtype']))
                    print('\tDefault Value: {}'.format(parameter['default_value']))
                    print('\tSolvers: ')
                    for solver in parameter['solvers']:
                        print('\t\t"{}"'.format(solver))
                        
        self.parameters.update(deepcopy(self.analysis.parameters))
        
        # Print parameters of the geometry object
        print('---------------------------------------------------')
        print('The Chosen Geometry: "{}".'.format(self.geometry.name))
        print('Has the following Parameters that can be changed: ')
        for parameter_name,parameter in self.geometry.parameters.items():
                    print('---------------------------------------------------')
                    print('Name: {}'.format(parameter_name))
                    print('\tDescription: {}'.format(parameter['description']))
                    print('\tData-type: {}'.format(parameter['dtype']))
                    print('\tDefault Value: {}'.format(parameter['default_value']))
                    print('\tSolvers: ')
                    for solver in parameter['solvers']:
                        print('\t\t"{}"'.format(solver))
        
        self.parameters.update(deepcopy(self.geometry.parameters))
        
        # Check if materials required
        if any(self.requirements['materials'].values()):

            # Print parameters for all of the materials
            for material_name in self.materials.keys():
                print('---------------------------------------------------')
                print('The Chosen Material: "{}".'.format(material_name))
                requirement_fulfilled = [requirement[0] for requirement in self.materials[material_name].requirements['materials'].items() if requirement[1]][0]
                print('Material Type: "{}"'.format(requirement_fulfilled))
                print('Has the following Parameters that can be used: ')
                for parameter_name,parameter in self.materials[material_name].parameters.items():
                            print('---------------------------------------------------')
                            print('Name: {}'.format(parameter_name))
                            print('\tDescription: {}'.format(parameter['description']))
                            print('\tData-type: {}'.format(parameter['dtype']))
                            print('\tDefault Value: {}'.format(parameter['default_value']))
                            print('\tSolvers: ')
                            for solver in parameter['solvers']:
                                print('\t\t"{}"'.format(solver))
                
                self.parameters.update(deepcopy(self.materials[material_name].parameters))

        else:
            print('---------------------------------------------------')
            print('No materials chosen for this model')


        print('---------------------------------------------------')

    
    def copy_and_modify_parameters(self):
        '''
        
        '''
        
        self.print_model_parameter_info()
            
        # Query user to pick which parameters they would like to edit the values of for use in this model
        questions = [inquirer.Checkbox('chosen_parameters', 'Pick the parameters that you would like to change the values of for this model', choices = list(self.parameters.keys()), carousel = True)]
        answers = inquirer.prompt(questions)

        # Loop over parameters that user would like to change the values of
        for chosen_parameter in answers['chosen_parameters']:

            value = inquirer.text('What value would you like to assign to: "{}", Note: dtype = "{}"'.format(chosen_parameter,self.parameters[chosen_parameter]['dtype']),
                                  default = self.parameters[chosen_parameter]['default_value'])

            if self.parameters[chosen_parameter]['dtype'] == 'int':
                self.parameters[chosen_parameter]['default_value'] = int(value)
                print('---------------------------------------------------')
                print('The value of Parameter "{}" was changed to: {}'.format(chosen_parameter,int(value)))
 

            else:
                self.parameters[chosen_parameter]['default_value'] = float(value)
                print('---------------------------------------------------')
                print('The value of Parameter "{}" was changed to: {}'.format(chosen_parameter,float(value)))
                

        print('---------------------------------------------------')
        

    def move_files_from_objects(self):
        '''
        
        '''

        # Copy analysis files to model directory
        self.move_object_folder(self.analysis.fpath, self.fpath)
    
        # If mpcci abaqus-fluent coupled analysis
        if all(self.requirements['softwares'].values()):
            self.build_mpcci_model()
           
        # If just abaqus analysis
        elif self.requirements['softwares']['abaqus']:
            self.build_abaqus_model()

        # If just fluent analysis
        elif self.requirements['softwares']['fluent']:
            self.build_fluent_model()

        else:
            print('---------------------------------------------------')
            print('Software Requirements are not valid.')
            print('---------------------------------------------------')
            raise ValueError('Software Requirements are not valid.')
        

    def build_abaqus_model(self):
        '''
        
        '''

        # Satisfy geometry requirements
        for requirement_name,requirement_value in self.requirements['geometries'].items():
            if requirement_value:
                copyfile(os.path.join(self.geometry.fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))


        # Satisfy material requirements
        for material_name in self.materials.keys():
            for requirement_name, requirement_value in self.materials[material_name].requirements['materials'].items():
                if requirement_value:
                    copyfile(os.path.join(self.materials[material_name].fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))


        # Add parameter values to main abaqus input file
        with open(os.path.join(self.solver_fpaths['abaqus'],'main.inp'),'r') as inp_read, open(os.path.join(self.solver_fpaths['abaqus'],self.name+'.inp'),'w') as inp_write:

            inp_write.write('*Parameter\n')
            inp_write.write('# -------------------------------------\n')
            inp_write.write('# --------USER DEFINED PARAMETERS------\n')
            inp_write.write('# -------------------------------------\n')

            # Write parameter values as dictated by user
            for parameter_name,parameter in self.parameters.items():
                if 'abaqus' in parameter['solvers']:
                    inp_write.write('{} = {}\n'.format(parameter_name, parameter['default_value']))

            # Copy main input file contents
            copyfileobj(inp_read,inp_write)

        # Delete old main input file
        os.remove(os.path.join(self.solver_fpaths['abaqus'],'main.inp'))


        # If submodel analysis, import global .odb and .prt files (Note: This only works if global analysis has been run, and global script preparation run)
        if self.requirements['analysis']['abaqus_global_odb'] and self.requirements['analysis']['abaqus_global_prt']:

            potential_models = [model_name for model_name in self.builder.data['model'].keys() if model_name is not self.name]

            if potential_models:
            
                model_to_import_global = inquirer.list_input('This model requires a global .odb and .prt file to function, please specify the model you would like to import these from', choices=potential_models, carousel=True)
                
                # Copy global .odb 
                if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.odb')):
                    copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.odb'),
                                os.path.join(self.solver_fpaths['abaqus'],'global.odb'))
                
                # Copy global .prt
                if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.prt')):
                    copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.prt'),
                                os.path.join(self.solver_fpaths['abaqus'],'global.prt'))

            else:
                print('---------------------------------------------------')
                print('No models to import global files from')
                print('---------------------------------------------------')


    def build_fluent_model(self):
        '''
        
        '''
        # Satisfy geometry requirements
        for requirement_name,requirement_value in self.requirements['geometries'].items():
            if requirement_value:
                copyfile(os.path.join(self.geometry.fpath,requirement_name+'.msh'), os.path.join(self.solver_fpaths['fluent'],requirement_name+'.msh'))

        


    def build_mpcci_model(self):
        '''
        
        '''

        # Satisfy geometry requirements
        for requirement_name,requirement_value in self.requirements['geometries'].items():
            if requirement_value:
                if 'abaqus' in requirement_name:
                    copyfile(os.path.join(self.geometry.fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))
                else:
                    copyfile(os.path.join(self.geometry.fpath,requirement_name+'.msh'), os.path.join(self.solver_fpaths['fluent'],requirement_name+'.msh'))


        # Satisfy material requirements
        for material_name in self.materials.keys():
            for requirement_name, requirement_value in self.materials[material_name].requirements['materials'].items():
                if requirement_value:
                    copyfile(os.path.join(self.materials[material_name].fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))


        # Add parameter values to main abaqus input file
        with open(os.path.join(self.solver_fpaths['abaqus'],'main.inp'),'r') as inp_read, open(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),'w') as inp_write:

            inp_write.write('*Parameter\n')
            inp_write.write('# -------------------------------------\n')
            inp_write.write('# --------USER DEFINED PARAMETERS------\n')
            inp_write.write('# -------------------------------------\n')

            # Write parameter values as dictated by user
            for parameter_name,parameter in self.parameters.items():
                if 'abaqus' in parameter['solvers']:
                    inp_write.write('{} = {}\n'.format(parameter_name, parameter['default_value']))

            # Copy main input file contents
            copyfileobj(inp_read,inp_write)
        
        # Replace old main.inp file
        os.replace(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),os.path.join(self.solver_fpaths['abaqus'],'main.inp'))


        # Fluent parameters and assemble .cas file


        # Copy journal file if requirement
        if self.requirements['analysis']['fluent_journal']:
            pass



        # If submodel analysis, import global .odb and .prt files (Note: This only works if global analysis has been run, and global script preparation run)
        if self.requirements['analysis']['abaqus_global_odb'] and self.requirements['analysis']['abaqus_global_prt']:

            potential_models = [model_name for model_name in self.builder.data['model'].keys() if model_name is not self.name]

            if potential_models:
            
                model_to_import_global = inquirer.list_input('This model requires a global .odb and .prt file to function, please specify the model you would like to import these from', choices=potential_models, carousel=True)
                
                # Copy global .odb 
                if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.odb')):
                    copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.odb'),
                                os.path.join(self.solver_fpaths['abaqus'],'global.odb'))
                
                # Copy global .prt
                if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.prt')):
                    copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'_global.prt'),
                                os.path.join(self.solver_fpaths['abaqus'],'global.prt'))

            else:
                print('---------------------------------------------------')
                print('No models to import global files from')
                print('---------------------------------------------------')

        