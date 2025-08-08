import numpy as np
import matplotlib.pyplot as plt
import os
import json
import glob
from shutil import copy2 as copy_input_file
from shutil import rmtree

# Global File Paths
modelfile_fpath = 'Model_Files'

analysis_fpath = os.path.join(modelfile_fpath, 'ANALYSIS')
geometry_fpath = os.path.join(modelfile_fpath, 'GEOMETRY')
material_fpath = os.path.join(modelfile_fpath, 'MATERIALS')

solidmaterial_fpath = os.path.join(material_fpath, 'SOLID_MATERIALS')
fluidmaterial_fpath = os.path.join(material_fpath, 'FLUID_MATERIALS')

model_data_fpath = 'Model_Data.json'

def main():

    model = Model()

    model.create_object('material', 'ISOTROPIC_PEEK', 'bin/MATERIALS/SOLID_MATERIALS/ISOTROPIC_PEEK', True)
    model.create_object('analysis', 'FREQUENCY_EXTRACT','bin/ANALYSIS/FREQUENCY_EXTRACT')
    model.create_object('geometry', 'IDEA_1', 'bin/GEOMETRY/IDEA_1')
    print(model.geometries)
    model.delete_object('geometry', 'IDEA_1')
    print(model.geometries)
    model.delete_object('analysis', 'bruh')
    print(model.materials,model.analyses,model.geometries)



class Model:
    def __init__(self, file=model_data_fpath):
        self.materials = {}
        self.analyses  = {}
        self.geometries = {}

    def create_object(self, object_type, object_name, source_file_path, solid=True):
        '''
        ---------------------------------------------------
        Creates a new object in the database with an object type  from a specified file path. All input files from this file path will be copied to a new destination folder
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of object to be added to the database. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be added. This will be used in the database, and as the file path that the input files will be stored in.

        source_file_path : str
            The file path which contains the input files to be added to the database. The names of these files will be used in the database, so must be set correctly.

        solid : boolean
            This parameter only has an effect if the added object_type is a "material". In this case, True will refer to a solid material, whereas, False will refer to an acoustic medium.
        ---------------------------------------------------
        '''
        
        # Create material object in the database and move the .inp files to the destination folder
        if object_type == 'material':

            # Get filepath of material
            if solid:
                dest_file_path = os.path.join(solidmaterial_fpath, object_name.upper())
            else:
                dest_file_path = os.path.join(fluidmaterial_fpath, object_name.upper())

            # Create object in the database
            self.materials[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The material: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # Create analysis object in the database and move the .inp files to the destination folder
        elif object_type == 'analysis':

            # Get destination filepath of analysis
            dest_file_path = os.path.join(analysis_fpath, object_name.upper())

            # Create object in the database
            self.analyses[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The analysis: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # Create geometry object in the database and move the .inp files to the destination folder
        elif object_type == 'geometry':

            # Get destination filepath of analysis
            dest_file_path = os.path.join(geometry_fpath, object_name.upper())

            # Create object in the database
            self.geometries[object_name.lower()] = {'Name': object_name.lower(), 'File_Path': dest_file_path}
            print('The geometry: "{}" has been successfully added to the local dictionary.'.format(object_name))


        # raise error if the object is not a valid type
        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        # Copy *.inp files from source file path to the destination file path
        files_to_copy = glob.glob(os.path.join(source_file_path,'*.inp'))
        
        # Create destination folder
        os.makedirs(dest_file_path, exist_ok=True)
        print('The Destination folder: "{}" has been successfully created.'.format(dest_file_path))

        # Copy material file to new folder with new name
        for file in files_to_copy:
            file_name = file.split('\\')[-1]

            try:
                copy_input_file(file, os.path.join(dest_file_path, file_name.upper()+'.inp'), follow_symlinks=True)
                print('The file: "{}" has been successfully added to the destination filepath.'.format(file_name.upper()+'.inp'))
            except:
                raise FileNotFoundError('The file: "{}" was not moved to the destination filepath.'.format(file_name.upper()+'.inp'))
            

    def modify_object(self, object_type, object_name, new_name, solid = True):
        '''
        ---------------------------------------------------
        Modifies either an objects name or its fpath
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of the object to be modified. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be modified. If this does not match an object in the object type dictionary then an error will be thrown.
        
        new_name : str
            The new name of the object. This only has an effect if modify_name is set to True.

        solid : boolean
            Whether the material to be modified is solid or 
        ---------------------------------------------------
        '''

        if object_type == 'material':
            # Change folder name
            fpath = os.path.join()
            os.rename()

            # Change fpath

            # Change name

        elif object_type == 'analysis':

        elif object_type == 'geometry':

        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))

    def delete_object(self, object_type, object_name):    
        '''
        ---------------------------------------------------
        Deletes an object from the local database and the folder of *.inp files.
        *******************************************************************************************************************************
        *************************NEEDS TO BE UPDATED FOR SOLID AND FLUID GEOMETRIES****************************************************
        *******************************************************************************************************************************
        ---------------------------------------------------
        PARAMETERS
        ---------------------------------------------------
        object_type : str, [analysis/geometry/material]
            The type of the object to be deleted from the database. This can be either of the three types listed above. If the string does not match exactly an error will be thrown.

        object_name : str
            The name of the object to be deleted. If this does not match an object in the object type dictionary then an error will be thrown.
        ---------------------------------------------------
        '''
        # Make object name lower case
        object_name = object_name.lower()


        if object_type == 'analysis':
            
            # First delete from local dictionary
            try:
                self.analyses.pop(object_name)
                print('The analysis: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Analysis Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.analyses.keys()]))
            
            # Get file path of files
            fpath = os.path.join(analysis_fpath, object_name.upper())


        elif object_type == 'geometry':
            
            # First delete from local dictionary
            try:
                self.geometries.pop(object_name)
                print('The geometry: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Geometry Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.geometries.keys()]))
            
            # Get file path of files
            fpath = os.path.join(geometry_fpath, object_name.upper())


        elif object_type == 'material':

            # First delete from local dictionary
            try:
                self.materials.pop(object_name)
                print('The material: "{}" has been successfully removed from the local dictionary.'.format(object_name))
            except:
                raise NameError('Material Name: "{}" does not exist. The valid names are: {}'.format(object_name,[key for key in self.materials.keys()]))
            
            # Get file path of files
            fpath = os.path.join(material_fpath, object_name.upper())

        
        else:
            raise NameError('Object Type: "{}" is not a valid type. The valid types are: "material", "analysis" and "geometry"'.format(object_type))
        

        # Delete files
        try:
            rmtree(fpath)
            print('The file path: "{}" has been successfully removed from the local dictionary.'.format(fpath))
        except:
            raise FileNotFoundError('The fpath: "{}" does not exist. The database may be corrupted.'.format(fpath))
        

    def build_model(self, Model_Name):

        pass

    # *** STILL NOT SURE IF SHOULD RUN MODEL THROUGH THIS ***
    # def run_model(self, Model_Name): 

if __name__ == '__main__':
    main()