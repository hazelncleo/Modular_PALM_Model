from __future__ import annotations
import re


class Requirements:
    pass



class DatabaseRequirements(Requirements):

    keys = ['software', 'analysis', 'geometry']

    def __init__(
        self,
        software: list[str],
        analysis: list[str],
        geometry: list[str]
    ) -> None:
        self.software = software
        self.analysis = analysis
        self.geometry = geometry
    

    @classmethod
    def load_from_dict(cls, data_dict: dict) -> DatabaseRequirements:       
        ''''''

        if not cls.validate_dict(data_dict):
            raise ValueError('Provided requirements dictionary is not valid')

        return cls(
            software = data_dict['software'],
            analysis = data_dict['analysis'],
            geometry = data_dict['geometry']
        )
        
        
    @classmethod
    def load_from_file(cls, fpath: str, requirements_file_name: str) -> DatabaseRequirements:
        ''''''
        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        if not requirements_file_name.endswith('.json'):
            raise FileNotFoundError(f'File: "{requirements_file_name}"is not a .json file.')

        if not os.path.exists(os.path.join(fpath, requirements_file_name)):
            raise FileNotFoundError(f'File: "{requirements_file_name}" does not exist.')

        try:
            with open(os.path.join(fpath, requirements_file_name), 'r') as requirements_file:
                data_dict = json.load(requirements_file)

        except:
            raise FileNotFoundError(f'Could not load file: "{os.path.join(fpath, requirements_file_name)}".')

        return cls.load_from_dict(data_dict)


    @classmethod
    def validate_dict(cls, data_dict: dict) -> bool:
        ''''''
        
        if not isinstance(data_dict, dict):
            return False

        if not data_dict:
            return False

        if not all([isinstance(key, str) for key in data_dict]):
            return False

        if any([key not in data_dict for key in cls.keys]):
            return False

        if not all([isinstance(value, list) for value in data_dict.values()]):
            return False

        if not all([len(value) > 0 for value in data_dict.values()]):
            return False

        if not all([all([isinstance(requirement, str) for requirement in value]) for value in data_dict.values()]):
            return False

        if not all([all([re.match("^[A-Za-z0-9 _-]+$", requirement) for requirement in value]) for value in data_dict.values()]):
            return False

        if not all([all([len(requirement) <= 100 for requirement in value]) for value in data_dict.values()]):
            return False
        
        return True

    
    def add_requirements_from_dict(self, data_dict: dict) -> None:
        ''''''

        if not self.validate_dict(data_dict):
            raise ValueError('The provided requirements dictionary was invalid')

        self.software.extend([requirement for requirement in data_dict['software'] if requirement not in self.software])
        self.analysis.extend([requirement for requirement in data_dict['analysis'] if requirement not in self.analysis])
        self.geometry.extend([requirement for requirement in data_dict['geometry'] if requirement not in self.geometry])



class ObjectRequirements(Requirements):
    pass



# Maybe?
class ModelRequirements(Requirements):
    pass