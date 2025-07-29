import numpy as np
import matplotlib.pyplot as plt
import os
import json
import optparse
import glob
from shutil import copy2 as copy_input_file

def main():

    model = Model()

    model.create_object('material', 'ISOTROPIC_PEEK', 'bin/MATERIALS/SOLID_MATERIALS/ISOTROPIC_PEEK', True)
    model.create_object('analysis', 'FREQUENCY_EXTRACT','bin/ANALYSIS/FREQUENCY_EXTRACT')
    model.create_object('geometry', 'IDEA_1', 'bin/GEOMETRY/IDEA_1')
    '''
    parser = optparse.OptionParser()

    parser.add_option('-o', dest='opt',type='str')
    (option, args) = parser.parse_args()
    print(option, args)
    '''


class Model:
    def __init__(self, file='Model_Data.json'):
        self.materials = {}
        self.analyses  = {}
        self.geometries = {}

    def create_object(self, object_type, object_name, source_file_path, solid=True):
        '''
        

        
        '''
        
        # Create material object in the database and move the .inp files to the destination folder
        if object_type == 'material':

            # Get filepath of material
            if solid:
                dest_file_path = 'Model_Files/MATERIALS/SOLID_MATERIALS/' + object_name.upper()
            else:
                dest_file_path = 'Model_Files/MATERIALS/FLUID_MATERIALS/' + object_name.upper()

            # Create object in the database
            self.materials[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}

            # Copy *.inp files from source file path to the destination file path
            if source_file_path == '':
                files_to_copy = glob.glob('*.inp')
            else:
                files_to_copy = glob.glob(source_file_path + '\\*.inp')
            
            # Create destination folder
            os.makedirs(dest_file_path, exist_ok=True)

            # Copy material file to new folder with new name
            for file in files_to_copy:
                file_name = file.split('\\')[-1]
                copy_input_file(file, dest_file_path + '/' + object_name.upper() + '.inp', follow_symlinks=True)


        # Create analysis object in the database and move the .inp files to the destination folder
        elif object_type == 'analysis':

            # Get destination filepath of analysis
            dest_file_path = 'Model_Files/ANALYSIS/' + object_name.upper()

            # Create object in the database
            self.analyses[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}

            # Copy *.inp files from source file path to the destination file path
            if source_file_path == '':
                files_to_copy = glob.glob('*.inp')
            else:
                files_to_copy = glob.glob(source_file_path + '\\*.inp')
            
            # Create destination folder
            os.makedirs(dest_file_path, exist_ok=True)

            # Copy analysis files to new folder with new name
            for file in files_to_copy:
                file_name = file.split('\\')[-1]
                copy_input_file(file, dest_file_path + '/' + file_name, follow_symlinks=True)

        # Create geometry object in the database and move the .inp files to the destination folder
        elif object_type == 'geometry':

            # Get destination filepath of analysis
            dest_file_path = 'Model_Files/GEOMETRY/' + object_name.upper()

            # Create object in the database
            self.analyses[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}

            # Copy *.inp files from source file path to the destination file path
            if source_file_path == '':
                files_to_copy = glob.glob('*.inp')
            else:
                files_to_copy = glob.glob(source_file_path + '\\*.inp')
            
            # Create destination folder
            os.makedirs(dest_file_path, exist_ok=True)

            # Copy geometry files to new folder with new name
            for file in files_to_copy:
                file_name = file.split('\\')[-1]
                copy_input_file(file, dest_file_path + '/' + file_name, follow_symlinks=True)

        # raise error if the object is not a valid type
        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))

    def modify_object(self, Object_Type):

        pass


    def delete_object(self, Object_Type):    

        pass


    def build_model(self, Model_Name):

        pass

    # *** STILL NOT SURE IF SHOULD RUN MODEL THROUGH THIS ***
    # def run_model(self, Model_Name): 

if __name__ == '__main__':
    main()