from __future__ import annotations
import re
import os
import json
import warnings



class Requirements:
    '''
    ------------------------------
        Object/Model Requirements Class
    ------------------------------
    Requirements class that stores requirements for a database, object or model
    ------------------------------
        Attributes
    ------------------------------
    keys : list[str], ['software', 'analysis', 'geometry']
        The available categories of requirements that can be specified
    
    software : list[str]
        A list of all softwares that are:
        - Able to be used by objects/models created in the database
        - Required by the parent in the case of objects/models

    analysis : list[str]
        A list of all analyses that are:
        - Able to be used by objects/models created in the database
        - Required by the parent in the case of objects/models

    geometry : list[str]
        A list of all geometries that are:
        - Able to be used by objects/models created in the database
        - Required by the parent in the case of objects/models
    
    ------------------------------
        Examples/Usage
    ------------------------------

    >>> requirements = Requirements.load_from_dict(valid_req_dict)

    >>> requirements = Requirements.load_from_file(fpath, 'file.json') 

    '''

    keys = ['software', 'analysis', 'geometry']

    def __init__(self, software: list[str], analysis: list[str], geometry: list[str]) -> None:
        self.software = software
        self.analysis = analysis
        self.geometry = geometry
    

    @classmethod
    def load_from_dict(cls, data_dict: dict) -> Requirements:       
        '''Loads Requirements from a dictionary'''

        if not cls.validate_dict(data_dict):
            raise ValueError('Provided requirements dictionary is not valid')

        return cls(
            software = data_dict['software'],
            analysis = data_dict['analysis'],
            geometry = data_dict['geometry']
        )
        
        
    @classmethod
    def load_from_file(cls, fpath: str, fname: str) -> Requirements:
        '''Loads requirements from a .json file'''

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        if not fname.endswith('.json'):
            raise FileNotFoundError(f'File: "{fname}" is not a .json file.')

        if not os.path.exists(os.path.join(fpath, fname)):
            raise FileNotFoundError(f'File: "{fname}" does not exist.')

        try:
            with open(os.path.join(fpath, fname), 'r') as requirements_file:
                data_dict = json.load(requirements_file)

        except:
            raise FileNotFoundError(f'Could not load file: "{os.path.join(fpath, fname)}".')

        return cls.load_from_dict(data_dict)


    @classmethod
    def validate_dict(cls, data_dict: dict, full_dict: bool = True) -> bool:
        '''
        ---------------------------------------------------------------------------------------
        Validates that a dictionary is valid for use in interacting with Requirements objects
        
        Checks:
        - is dict
        - is not empty
        - all keys are strings
        - if keys are valid strings
        - if values are lists
        - if all requirements in lists are strings and are valid strings
        ---------------------------------------------------------------------------------------
            Arguments
        ---------------------------------------------------------------------------------------
        
        data_dict : dict
            The dictionary to validate

        full_dict : bool
            Whether to validate the dictionary as a full/database dictionary or as a part dictionary

        ---------------------------------------------------------------------------------------

        '''
        
        if not isinstance(data_dict, dict):
            return False

        if not data_dict:
            return False

        if not all([isinstance(key, str) for key in data_dict]):
            return False

        if full_dict:
            if any([key not in data_dict for key in cls.keys]):
                return False
        else:
            if any([key not in cls.keys for key in data_dict]):
                return False

        if not all([isinstance(value, list) for value in data_dict.values()]):
            return False

        if full_dict and (not all([len(value) > 0 for value in data_dict.values()])):
            return False

        if not all([all([isinstance(requirement, str) for requirement in value]) for value in data_dict.values()]):
            return False

        if not all([all([re.match("^[A-Za-z0-9 _-]+$", requirement) for requirement in value]) for value in data_dict.values()]):
            return False

        if not all([all([len(requirement) <= 100 for requirement in value]) for value in data_dict.values()]):
            return False
        
        return True


    def save_to_file(self, fpath: str, fname: str) -> None:
        '''Saves Requirements to a json file'''    

        data_dict = self.convert_to_dict()

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        if os.path.exists(os.path.join(fpath, fname)):
            warnings.warn(f'The file: "{os.path.join(fpath, fname)}" was overwritten when saving.')

        try:
            with open(os.path.join(fpath, fname), 'w') as file_to_save:
                json.dump(data_dict, file_to_save, indent = 4)
        except:
            raise FileExistsError('Could not save json file of Requirements')


    def convert_to_dict(self) -> dict:
        '''Converts Requirements to a dictionary representation'''

        dict_representation = {
            'software' : self.software,
            'analysis' : self.analysis,
            'geometry' : self.geometry
        }

        assert self.validate_dict(dict_representation)

        return dict_representation

    
    def add_requirements_from_dict(self, data_dict: dict) -> None:
        '''Add requirements from a dictionary'''

        if not self.validate_dict(data_dict, full_dict=False):
            raise ValueError('The provided requirements dictionary was invalid')
        
        if 'software' in data_dict:
            self.software.extend([requirement for requirement in data_dict['software'] if requirement not in self.software])

        if 'analysis' in data_dict:
            self.analysis.extend([requirement for requirement in data_dict['analysis'] if requirement not in self.analysis])

        if 'geometry' in data_dict:
            self.geometry.extend([requirement for requirement in data_dict['geometry'] if requirement not in self.geometry])


    def add_requirements_from_file(self, fpath: str, fname: str) -> None:
        ''''''

        temp_reqs = self.load_from_file(fpath, fname)

        self.add_requirements_from_dict(temp_reqs.convert_to_dict())


    def add_requirements_from_requirements(self, requirements: Requirements) -> None:
        ''''''
        self.add_requirements_from_dict(requirements.convert_to_dict())

    
    def remove_requirements_from_dict(self, data_dict: dict) -> None:
        '''Remove requirements from a dictionary'''

        if not self.validate_dict(data_dict, full_dict=False):
            raise ValueError('The provided requirements dictionary was invalid')

        if 'software' in data_dict:
            for requirement_to_remove in data_dict['software']:
                if requirement_to_remove in self.software: self.software.remove(requirement_to_remove)

        if 'analysis' in data_dict:
            for requirement_to_remove in data_dict['analysis']:
                if requirement_to_remove in self.analysis: self.analysis.remove(requirement_to_remove)

        if 'geometry' in data_dict:
            for requirement_to_remove in data_dict['geometry']:
                if requirement_to_remove in self.geometry: self.geometry.remove(requirement_to_remove)


    def requirements_is_subset(self, requirements_to_test: Requirements) -> bool:
        '''Check if provided Requirements object is a subset of current Requirements object'''

        if all([requirement in self.software for requirement in requirements_to_test.software]):
            if all([requirement in self.analysis for requirement in requirements_to_test.analysis]):
                if all([requirement in self.geometry for requirement in requirements_to_test.geometry]):
                    return True

        return False