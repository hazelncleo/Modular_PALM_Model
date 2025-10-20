import os
from shutil import copytree
from shutil import copyfile
import string
from tkinter import Tk
from tkinter.filedialog import askdirectory
import inquirer
from copy import deepcopy
from shutil import copyfileobj
from importlib.util import spec_from_file_location
from importlib.util import module_from_spec
import warnings
import sys
import xml.etree.ElementTree as ET

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import ansys.fluent.core as pyfluent
    
from HazelsAwesomeTheme import red_text,green_text,blue_text,yellow_text
from HazelsAwesomeTheme import HazelsAwesomeTheme as Theme



class Model:
    def __init__(self, builder, analysis_name = None, geometry_name = None, material_names = None):
        '''
        ---------------------------------------------------
        
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        
        ---------------------------------------------------
        '''
        
        print('-'*60)
        print('Create ' + blue_text('model') + ' operation started')
        
        # Modular_Abaqus_Builder class containing this object 
        self.builder = builder
        
        self.new_model_name()

        # Set destination fpath
        self.fpath = os.path.join(self.builder.fpaths['model'], self.name)
        
        if os.path.exists(self.fpath):
            print(red_text('File path "{}", already exists.'.format(self.fpath)))
            raise FileExistsError
        
        print('File path set to "{}".'.format(blue_text(self.fpath)))

        self.new_description()

        # Select Analysis
        self.select_analysis(analysis_name)

        # Select Geometry
        self.select_geometry(geometry_name)

        # Add Materials
        if any(self.requirements['material'].values()):
            self.select_materials(material_names)
        else:
            print('-'*60)
            print(yellow_text('No material objects required for analysis: "{}", skipping select materials'.format(self.analysis.name)))
            self.materials = {}

        # Get solver fpaths
        self.set_fpaths()
            
        # Copy parameters from objects and prompt user to modify their values
        self.copy_and_modify_parameters()
        
        # Move files from object fpaths to the solver fpaths
        self.move_files_from_objects()
        
        print('-'*60)
        print(green_text('Create model operation successful.'))
    

    def move_object_folder(self, source_fpath, destination_fpath, dirs_exist_ok=False):
        '''
        
        '''
        copytree(source_fpath, destination_fpath, symlinks=True, dirs_exist_ok=dirs_exist_ok)
        
        if os.path.isabs(source_fpath):
            source_fpath = os.path.join('...',os.path.join('',*source_fpath.split('/')[-4:]))
            
        print('-'*60)
        print(green_text('Successfully copied files from:\n"{}" -> "{}"'.format(source_fpath, destination_fpath)))

    
    def new_model_name(self):
        '''
        ---------------------------------------------------
        Gets a new model name, ensures that no model already exists of that type
        ---------------------------------------------------
        '''
        # Get current names
        current_names = list(self.builder.data['model'].keys())
        if hasattr(self, 'name'): current_names.remove(self.name)
        
        print('-'*60)
        print('Please enter a new ' + blue_text('name') + ' for the model to be created: ')
        print('Note: ')
        print('- It must only use lowercase letters, numbers, underscores and hyphens.')
        print('- It must have fewer than 30 characters')
        print('- It must be unique.')
        print('- To cancel the create model process, enter nothing.')
        print('-'*60)
        if len(current_names):
            print('The model names currently in use are listed below: ')
            print('"'+'", "'.join([blue_text(name) for name in current_names])+'"')
            print('-'*60)
        else:
            print('No model names currently in use.')
            print('-'*60)
        
        model_name = inquirer.prompt([inquirer.Text('model_name', 
                                                     'Enter the ' + blue_text('name') + ' of the new model', 
                                                     validate = self.validate_name)], 
                                                     theme=Theme())['model_name']

        if not model_name:
            print('-'*60)
            print(yellow_text('Cancel command given.'))
            raise NameError
        
        else: 
            print('-'*60)
            print(green_text('The name: "{}" for the new model has been selected.'.format(model_name)))

        self.name = model_name
        return
                
                
    def new_description(self):
        '''
        ---------------------------------------------------
        Provide a description for the model added to the database.
        ---------------------------------------------------
        '''

        print('-'*60)
        print('Please enter a short ' + blue_text('description') + ' of the new model:')
        print('Note: ')
        print('- It must only use letters, numbers, or the following symbols (not including single quotes): \'_-,.! ()[]\'')
        print('- It must have fewer than 100 characters')
        print('- It must be unique.')
        print('-'*60)
        
        description = inquirer.prompt([inquirer.Text('description', 
                                                     'Please enter a short ' + blue_text('description') + ' of the new model', 
                                                     validate = self.validate_description)], theme=Theme())['description']

        print('-'*60)
        print(green_text('The description: "{}" for the new model has been selected.'.format(description)))
        self.description = description
        return
            
 
    def select_analysis(self, analysis_name = None):
        '''
        ---------------------------------------------------
        Select an analysis object from the database for this model
        ---------------------------------------------------
        '''

        if not analysis_name:

            # Get the Analysis objects loaded in the database
            potential_analyses = list(self.builder.data['analysis'].keys())

            if not potential_analyses:
                raise FileExistsError

            print('-'*60)
            print(blue_text('Analyses') + ' available for use:')
            print('-'*60)
            for analysis in potential_analyses:
                print('Name: "{}"'.format(blue_text(analysis)))
                print('Description:\n"{}"'.format(self.builder.data['analysis'][analysis].description))
                print('-'*60)

            potential_analyses.append('cancel')

            # Prompt user to pick an analysis
            analysis_name = inquirer.prompt([inquirer.List('analysis_name','Pick Analysis to use', choices=potential_analyses, carousel = True)], theme=Theme())['analysis_name']

            if analysis_name == 'cancel':
                raise NameError

        print('-'*60)
        print(green_text('The analysis: "{}" was chosen for the current model.'.format(analysis_name)))
        self.analysis = self.builder.data['analysis'][analysis_name]
        self.requirements = self.analysis.requirements


    def get_potential_geometries(self):
        '''
        ---------------------------------------------------
        Get a list of all the potential geometries that fulfill the analysis requirements
        ---------------------------------------------------
        '''
        potential_geometries = []

        for geometry_name,geometry_object in self.builder.data['geometry'].items():
            # Check that the selected geometry fulfills all of the requirements of the analysis
            are_requirements_fulfilled = [fulfilled_requirement[1] for requirement_to_fulfill, fulfilled_requirement in zip(self.requirements['geometry'].items(),geometry_object.requirements['geometry'].items()) if requirement_to_fulfill[1]]

            if all(are_requirements_fulfilled):
                potential_geometries.append(geometry_name)
                
        if not potential_geometries:
            print(red_text('No geometry objects that meet the requirements available in the database'))
            raise FileExistsError

        return potential_geometries


    def select_geometry(self, geometry_name = None):
        '''
        ---------------------------------------------------
        Select a Geometry object from the database for this model
        ---------------------------------------------------
        '''
        
        if not geometry_name:
                        
            # Get the Geometry objects loaded in the database
            potential_geometries = self.get_potential_geometries()
            
            print('-'*60)
            print('The chosen analysis: "{}".'.format(blue_text(self.analysis.name)))
            print('Description:\n"{}"'.format(self.analysis.description))
            print('Has the following geometry requirements:')
            for requirement, is_required in self.requirements['geometry'].items():
                if is_required:
                    print(blue_text(requirement))

            print('-'*60)
            print('The following geometries meet these requirements:')
            print('-'*60)
            for geometry in potential_geometries:
                print('Name: "{}"'.format(blue_text(geometry)))
                print('Description:\n"{}"'.format(self.builder.data['geometry'][geometry].description))
                print('-'*60)

            potential_geometries.append('cancel')

            # Prompt user to pick a Geometry
            geometry_name = inquirer.prompt([inquirer.List('geometry_name', 'Pick Geometry to use', choices=potential_geometries, carousel = True)], theme=Theme())['geometry_name']

            # If cancel chosen, or no geometry name given
            if geometry_name == 'cancel':
                raise NameError
            
        print('-'*60)
        print(green_text('The geometry: "{}" was chosen for the current model.'.format(geometry_name)))
        self.geometry = self.builder.data['geometry'][geometry_name]
        
    
    def get_potential_materials(self):
        '''
        ---------------------------------------------------
        Get a list of all the potential materials that fulfill a requirement
        ---------------------------------------------------
        '''
        potential_materials = {key : [name for name,obj in self.builder.data['material'].items() if obj.requirements['material'][key]] for key,value in self.requirements['material'].items() if value}

        if len(potential_materials) and all([len(mats) for mats in potential_materials.values()]):
            return potential_materials
        else:
            print(red_text('No Material objects that meet all the requirements of the analysis.'))
            raise FileExistsError
        

    def select_materials(self, material_names = None):
        '''
        ---------------------------------------------------
        Select Material objects from the database for this model
        ---------------------------------------------------
        '''
        self.materials = {}
        print('-'*60)
        
        if material_names:
            
            for material_name in material_names:
                self.materials[material_name] = self.builder.data['material'][material_name]
                print(green_text('The material: "{}" has been added to the model.'.format(material_name)))
                return
        else:
            # Get the material objects loaded in the database
            potential_materials = self.get_potential_materials()

            print('The chosen analysis: "{}".'.format(blue_text(self.analysis.name)))
            print('Description:\n{}'.format(self.analysis.description))
            print('Has the following material requirements:')
            for requirement, is_required in self.requirements['material'].items():
                if is_required:
                    print(blue_text(requirement))


            print('-'*60)
            print('The following Materials meet each of the requirements:')
            print('-'*60)
            for requirement,materials in potential_materials.items():
                print('Requirement: "{}"'.format(blue_text(requirement)))
                print('-'*60)
                for material in materials:
                    print('Name: "{}"'.format(blue_text(material)))
                    print('Description:\n"{}"'.format(self.builder.data['material'][material].description))
                print('-'*60)
                materials.append('cancel')

            for requirement,materials in potential_materials.items():

                material_name = inquirer.prompt([inquirer.List('material_name',
                                                               'Choose a material to fulfill the requirement: "{}"'.format(blue_text(requirement)), 
                                                               choices=materials, 
                                                               carousel=True)], theme=Theme())['material_name']
                
                if material_name == 'cancel':
                    raise NameError

                self.materials[material_name] = self.builder.data['material'][material_name]
                print('-'*60)
                print(green_text('The material: "{}", that satisfies the requirement: "{}", has been added to the model.'.format(material_name, requirement)))
                print('-'*60)
                
            print(green_text('The following materials were chosen for the current model:'))
            for material in self.materials.keys():
                print(green_text('"{}"'.format(material)))
                    

    def set_fpaths(self):
        '''
        
        '''
        print('-'*60)
        # If all softwares required set solver fpaths accordingly.
        if all(self.requirements['software'].values()):
            self.solver_fpaths = {'abaqus' : os.path.join(self.fpath,'abaqus'),
                                  'fluent' : os.path.join(self.fpath,'fluent'),
                                  'mpcci' : os.path.join(self.fpath,'mpcci')}
            print('Analysis is an MPCCI analysis, setting fpaths accordingly.')
            print('-'*60)
            print(green_text('abaqus fpath set to: "{}"'.format(self.solver_fpaths['abaqus'])))
            print(green_text('FLUENT fpath set to: "{}"'.format(self.solver_fpaths['fluent'])))
            print(green_text('MPCCI fpath set to: "{}"'.format(self.solver_fpaths['mpcci'])))
            return
            
        # If only abaqus
        elif self.requirements['software']['abaqus']:
            self.solver_fpaths = {'abaqus' : self.fpath,
                                  'fluent' : None,
                                  'mpcci' : None}
            print('Analysis is an abaqus analysis, setting fpaths accordingly.')
            print('-'*60)
            print(green_text('abaqus fpath set to: "{}"'.format(self.solver_fpaths['abaqus'])))
            return
        
        # If only fluent
        elif self.requirements['software']['fluent']:
            self.solver_fpaths = {'abaqus' : None,
                                  'fluent' : self.fpath,
                                  'mpcci' : None}
            print('Analysis is a FLUENT analysis, setting fpaths accordingly.')
            print('-'*60)
            print(green_text('FLUENT fpath set to: "{}"'.format(self.solver_fpaths['fluent'])))
            return
        
        else:
            print('-'*60)
            print('Software Requirements are not valid.')
            raise FileExistsError


    def print_model_parameter_info(self):
        '''
        
        '''

        self.parameters = {}

        # Print parameters of the analysis object
        print('-'*60)
        print('The chosen analysis: "{}".'.format(blue_text(self.analysis.name)))
        print('Has the following parameters that can alter the current analysis') if self.analysis.parameters else print('Has no parameters that can be used.')
        for parameter_name,parameter in self.analysis.parameters.items():
            if any([self.requirements['software'][solver] for solver in parameter['solvers']]):
                print('-'*60)
                print('Name: "{}"'.format(blue_text(parameter_name)))
                print('\tDescription: {}'.format(parameter['description']))
                print('\tData-type: {}'.format(parameter['dtype']))
                print('\tDefault value: {}'.format(blue_text(parameter['default_value'])))  
                self.parameters[parameter_name] = deepcopy(self.analysis.parameters[parameter_name])
        
        # Print parameters of the geometry object
        print('-'*60)
        print('The chosen geometry: "{}".'.format(blue_text(self.geometry.name)))
        print('Has the following parameters that can be changed: ') if self.geometry.parameters else print('Has no parameters that can be used.')
        for parameter_name,parameter in self.geometry.parameters.items():
            if any([self.requirements['software'][solver] for solver in parameter['solvers']]):
                print('-'*60)
                print('Name: {}'.format(blue_text(parameter_name)))
                print('\tDescription: {}'.format(parameter['description']))
                print('\tData-type: {}'.format(parameter['dtype']))
                print('\tDefault value: {}'.format(blue_text(parameter['default_value'])))
                self.parameters[parameter_name] = deepcopy(self.geometry.parameters[parameter_name])

        if not len(self.materials):
            print('-'*60)
            print('No materials required for the analysis.')
        else:
            # Print parameters for all of the materials
            for material_name in self.materials.keys():
                print('-'*60)
                print('The chosen material: "{}" of material type: "{}".'.format(blue_text(material_name),blue_text([requirement[0] for requirement in self.materials[material_name].requirements['material'].items() if requirement[1]][0])))
                print('Has the following parameters that can be used: ') if self.materials[material_name].parameters else print('Has no parameters that can be used.')
                for parameter_name,parameter in self.materials[material_name].parameters.items():
                    if any([self.requirements['software'][solver] for solver in parameter['solvers']]):
                        print('-'*60)
                        print('Name: {}'.format(blue_text(parameter_name)))
                        print('\tDescription: {}'.format(parameter['description']))
                        print('\tData-type: {}'.format(parameter['dtype']))
                        print('\tDefault Value: {}'.format(blue_text(parameter['default_value'])))
                        self.parameters[parameter_name] = deepcopy(self.materials[material_name].parameters[parameter_name])

    
    def copy_and_modify_parameters(self):
        '''
        
        '''
        
        self.print_model_parameter_info()
            
        print('-'*60)
        answers = inquirer.prompt([inquirer.Checkbox('chosen_parameters', 
                                                     'Pick the parameters that you would like to change the values of for this model', 
                                                     choices = list(self.parameters.keys()), 
                                                     carousel = True)] , theme=Theme())['chosen_parameters']
        print('-'*60)

        # Loop over parameters that user would like to change the values of
        for chosen_parameter in answers:

            value = inquirer.prompt([inquirer.Text('parameter_value',
                                                   'What value would you like to assign to: "{}", Note: dtype = "{}"'.format(chosen_parameter,self.parameters[chosen_parameter]['dtype']),
                                                   default = self.parameters[chosen_parameter]['default_value'],
                                                   validate = lambda _,ans: self.validate_parameter_value(self.parameters[chosen_parameter]['dtype'], _, ans))], theme=Theme())['parameter_value']

            print('-'*60)
            self.parameters[chosen_parameter]['default_value'] = int(value) if self.parameters[chosen_parameter]['dtype'] == 'int' else float(value)
            print(green_text('The value of Parameter "{}" was changed to: {}'.format(chosen_parameter,int(value)))) if self.parameters[chosen_parameter]['dtype'] == 'int' else print(green_text('The value of Parameter "{}" was changed to: {}'.format(chosen_parameter,float(value))))
            print('-'*60)
            
        print(green_text('The parameter values assigned to the model: "{}" have been successfully modified.'.format(self.name)))
        

    def move_files_from_objects(self):
        '''
        
        '''

        # Copy analysis files to model directory
        try:
            self.move_object_folder(self.analysis.fpath, self.fpath)
            print(green_text('Moved analysis files successfully'))
        except:
            print('-'*60)
            print(red_text('Analysis files could not be moved from object folder to the new model folder.'))
            raise FileNotFoundError
        
        
        # If mpcci abaqus-fluent coupled analysis
        if all(self.requirements['software'].values()):
            self.build_mpcci_model()
           
        # If just abaqus analysis
        elif self.requirements['software']['abaqus']:
            self.build_abaqus_model()

        # If just fluent analysis
        elif self.requirements['software']['fluent']:
            self.build_fluent_model()

        else:
            print('-'*60)
            print(red_text('Software Requirements are not valid.'))
            raise ValueError
 

    def build_abaqus_model(self):
        '''
        
        '''
        print('-'*60)
        print('Assembling abaqus model')
        print('-'*60)

        # Satisfy geometry requirements
        for requirement_name,requirement_value in self.requirements['geometry'].items():
            if requirement_value and (('abaqus' in requirement_name) or ('assembly' in requirement_name)):
                copyfile(os.path.join(self.geometry.fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))
                print(green_text('File: "{}", copied to model path'.format(requirement_name+'.inp')))
                
                
        # Modify assembly.inp based on geometry requirements       
        if self.requirements['geometry']['assembly']:
            with open(os.path.join(self.solver_fpaths['abaqus'],'assembly.inp'),'r') as inp_read, open(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),'w') as inp_write:
                
                # get the names of the geometry requirements
                abaqus_reqs = [requirement_name for requirement_name,requirement_value in self.requirements['geometry'].items() if requirement_value and (('abaqus' in requirement_name) or ('assembly' in requirement_name))]
                
                line = inp_read.readline()
                
                # while end of file not reached
                while line:
                        
                    # if geometry is required then write its assembly lines
                    if '**' in line and any(req in line for req in abaqus_reqs):
                        line = inp_read.readline()

                        while '**' not in line:
                            inp_write.write(line)
                            line = inp_read.readline()
                            
                    line = inp_read.readline()

                # Write comment on final line to ensure no empty lines
                inp_write.write('**')

            # Replace old assembly.inp with modified version
            os.replace(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),os.path.join(self.solver_fpaths['abaqus'],'assembly.inp'))
            print(green_text('File: "assembly.inp", modified to reflect requirements'))
                                

        # Satisfy material requirements
        for material_name in self.materials.keys():
            for requirement_name, requirement_value in self.materials[material_name].requirements['material'].items():
                if requirement_value:
                    copyfile(os.path.join(self.materials[material_name].fpath,requirement_name+'.inp'), os.path.join(self.solver_fpaths['abaqus'],requirement_name+'.inp'))
                    print(green_text('File: "{}", copied to model path'.format(requirement_name+'.inp')))


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
                    print(green_text('Parameter: "{} = {}", inserted into main input file'.format(parameter_name,parameter['default_value'])))

            # Copy main input file contents
            copyfileobj(inp_read,inp_write)

        # Save modified main input file
        if self.solver_fpaths['mpcci']:
            os.replace(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),os.path.join(self.solver_fpaths['abaqus'],'main.inp'))
            print(green_text('Parameters successfully added to abaqus main input file: "main.inp".'))
            
        else: 
            os.remove(os.path.join(self.solver_fpaths['abaqus'],'main.inp'))
            os.rename(os.path.join(self.solver_fpaths['abaqus'],'temp.inp'),os.path.join(self.solver_fpaths['abaqus'],self.name+'.inp'))
            print(green_text('Parameters successfully added to abaqus main input file: "{}".'.format(self.name+'.inp')))
            
            
        # If submodel analysis, import global .odb and .prt files (Note: This only works if global analysis has been run, and global script preparation run)
        if self.requirements['analysis']['abaqus_global_odb'] and self.requirements['analysis']['abaqus_global_prt']:

            potential_models = list(self.builder.data['model'].keys())
            if self.name in potential_models: potential_models.remove(self.name)

            if potential_models:
                potential_models.append('choose_directory')
                print('-'*60)
                print('Select "choose_directory" to specify the files yourself.')
                print('-'*60)
                model_to_import_global = inquirer.prompt([inquirer.List('model_to_import_global',
                                                                        'This model requires a global .odb and .prt file to function, please specify the model you would like to import these from', 
                                                                        choices=potential_models, 
                                                                        carousel=True)], theme=Theme())['model_to_import_global']
                
                if model_to_import_global == 'choose_directory':
                    self.pick_global_files()
                else:
                    print('-'*60)
                    # Copy global .odb 
                    if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'.odb')):
                        copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'.odb'),
                                    os.path.join(self.solver_fpaths['abaqus'],'global.odb'))
                        print(green_text('Global .odb file copied from model: "{}".'.format(model_to_import_global)))
                    else:
                        print(red_text('{}.odb does not exist in the model: "{}"'.format(model_to_import_global)))
                        raise FileNotFoundError
                    
                    # Copy global .prt
                    if os.path.exists(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'.prt')):
                        copyfile(os.path.join(self.builder.data['model'][model_to_import_global].solver_fpaths['abaqus'],model_to_import_global+'.prt'),
                                    os.path.join(self.solver_fpaths['abaqus'],'global.prt'))
                        print(green_text('Global .prt file copied from model: "{}".'.format(model_to_import_global)))
                    else:
                        print(red_text('{}.prt does not exist in the model: "{}"'.format(model_to_import_global)))
                        raise FileNotFoundError

            else:
                print(red_text('No models to import global files from'))
                if self.builder.yes_no_question('Choose global.odb and global.prt files yourself?'):
                    self.pick_global_files()
                else:
                    raise FileNotFoundError

        print('-'*60)
        print(green_text('Assembly of abaqus model successful'))


    def build_fluent_model(self):
        '''
        
        '''

        print('-'*60)
        print('Assembling FLUENT model')
        print('-'*60)

        fluent_setup = self.get_fluent_script()
        print(green_text('Fluent script: "fluent_setup.py" retrieved successfully'))

        # Satisfy geometry requirements
        for requirement_name,requirement_value in self.requirements['geometry'].items():
            if requirement_value and ('fluent' in requirement_name):
                copyfile(os.path.join(self.geometry.fpath,requirement_name+'.msh'), os.path.join(self.solver_fpaths['fluent'],requirement_name+'.msh'))
                print(green_text('File: "{}", copied to model path'.format(requirement_name+'.msh')))
                break

        print('Calling fluent_setup script to build case file')
        
        if self.solver_fpaths['mpcci']:
            fluent_name = 'fluent_model.cas.h5'
        else: 
            fluent_name = self.name+'.cas.h5'

        # Call setup script
        fluent_setup(file_name = fluent_name,
                        mesh_file_name = requirement_name+'.msh',
                        fluent_wd = os.path.join(os.getcwd(),self.solver_fpaths['fluent']),
                        parameters = self.parameters)
        
        sys.dont_write_bytecode = False
        print('-'*60)

        
        # Edit journal file
        if not self.solver_fpaths['mpcci']:
            with open(os.path.join(self.solver_fpaths['fluent'],'journal.jou'),'r') as old_file, open(os.path.join(self.solver_fpaths['fluent'],'temp.jou'),'w') as new_file:

                # Write new first two lines
                new_file.write('\t; Read the case file\n')
                new_file.write('\t/rc {}\n'.format(fluent_name))

                # Delete first two lines of old journal file
                old_file.readline()
                old_file.readline()

                # Copy rest of journal file
                copyfileobj(old_file,new_file)
                
            
            os.replace(os.path.join(self.solver_fpaths['fluent'],'temp.jou'),os.path.join(self.solver_fpaths['fluent'],'journal.jou'))
            print(green_text('Journal file successfully edited to import case file.'))

        
        print('-'*60)
        print(green_text('Assembly of FLUENT model successful'))


    def build_mpcci_model(self):
        '''
        
        '''

        print('-'*60)
        print('Assembling MPCCI coupled abaqus-FLUENT model')

        self.build_fluent_model()

        self.build_abaqus_model()

        mpcci_setup = self.get_mpcci_script()
        print(green_text('MPCCI script: "mpcci_setup.py" retrieved successfully'))

        print('-'*60)
        # Prompt user for number of cpus for fluent and number of cpus for abaqus
        questions = [inquirer.Text('fluent_cpus', 'Please enter the number of cpus to use for the fluent simulation', default = 2, validate = lambda _, c : c.isnumeric() and (int(c) > 1)),
                     inquirer.Text('abaqus_cpus', 'Please enter the number of cpus to use for the abaqus simulation', default = 2, validate = lambda _, c : c.isnumeric() and (int(c) > 1))]
        
        answers = inquirer.prompt(questions, theme=Theme())
        print('-'*60)

        # Edit mpcci .csp file via script, depending on parameters set for the analysis.
        mpcci_setup(fpath = self.solver_fpaths['mpcci'], name = self.name, parameters = self.parameters, fluent_cpus = answers['fluent_cpus'], abaqus_cpus = answers['abaqus_cpus'])
        sys.dont_write_bytecode = False
        print('-'*60)

        # Delete old main.csp
        os.remove(os.path.join(self.solver_fpaths['mpcci'],'main.csp'))
        print(green_text('Deleted old main.csp'))

        print('-'*60)
        print(green_text('Assembly of MPCCI coupled abaqus-FLUENT model successful'))


    def get_fluent_script(self):
        '''
        
        '''
        sys.dont_write_bytecode = True

        # Get setup python script
        spec = spec_from_file_location('fluent_setup',os.path.join(self.solver_fpaths['fluent'],'fluent_setup.py'))
        temp = module_from_spec(spec)
        sys.modules["fluent_setup"] = temp
        spec.loader.exec_module(temp)

        return temp.fluent_setup
        

    def get_mpcci_script(self):
        '''
        
        '''
        sys.dont_write_bytecode = True

        # Get setup python script
        spec = spec_from_file_location('mpcci_setup',os.path.join(self.solver_fpaths['mpcci'],'mpcci_setup.py'))
        temp = module_from_spec(spec)
        sys.modules["mpcci_setup"] = temp
        spec.loader.exec_module(temp)

        return temp.mpcci_setup


    def pick_global_files(self): # TODO
        
        pass

    
    def validate_name(self, _, name):
            '''
            
            '''

            current_names = list(self.builder.data['model'].keys())

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

   
    def validate_parameter_value(self, dtype , _, value):
        
        # Check parameter value matches entered datatype
        if dtype == 'int':
            if value.isnumeric():
                return True
            else:
                print(red_text('\nThe entered value is not a valid integer'))
        else:
            try:
                float(value)
                return True
            except ValueError:
                print(red_text('\nThe entered value is not a valid float'))
                return False
            
            
    def validate_global_files(self): # TODO
        
        pass
    
