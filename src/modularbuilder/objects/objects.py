from __future__ import annotations
import os
from glob import iglob

'''

TODO
- docstrings
- tests


# build object
- select object type: [a, g, m]
- select to clone or build from fpath

- clone
    - select new name

- fpath
    - select fpath
    - contents read
    - if valid
    - enter name & description
    - create new fpath
    - move files & initialise object

'''



class Parent_Object:

    def __init__(
        self,
        name: str,
        description: str,
        object_type: str,
        fpath: str,
        files: list[str],
        requirements: Requirements,
        parameters: dict[str, Parameter]
    ) -> None:
        
        self.name         = name
        self.description  = description
        self.object_type  = object_type
        self.fpath        = fpath
        self.files        = files
        self.requirements = requirements
        self.parameters   = parameters

    
    @classmethod
    def load_from_dict(cls, data_dict: dict) -> Parent_Object: # TODO
        pass


    @classmethod
    def load_from_file(cls, fpath: str, fname: str) -> Parent_Object: # TODO
        pass


    @classmethod 
    def build_from_fpath(
        cls, 
        name: str, 
        description: str, 
        object_type: str, 
        fpath: str
    ) -> Parent_Object: # TODO
        
        if not os.path.exists(os.abspath(fpath)):
            raise FileNotFoundError('The path supplied does not exist')
        
        if not os.path.exists(os.abspath(os.path.join(fpath, 'object_data'))): # TODO 
            raise FileNotFoundError('The object_data path does not exist')

        # get parameters

        # create object folder

        # move other files to object folder
        return cls(
            name         = name,
            description  = description,
            object_type  = object_type,
            fpath        = new_fpath,
            files        = files,
            requirements = requirements,
            parameters   = parameters,
        )

    
    @classmethod
    def validate_dict(cls, data_dict: dict) -> tuple[bool, str]: # TODO
        pass


    def clone_object(self) -> Parent_Object: # TODO
        pass


    def convert_to_dict(self) -> dict: # TODO
        pass


    def save_to_file(self, fpath, fname) -> None: # TODO
        pass


    def change_name(self, new_name: str) -> tuple[bool, str]: # TODO
        ''''''
        name_valid, message = self.validate_name(new_name)

        if name_valid:
            old_name = self.name
            self.name = new_name
            return True, f'Object "{old_name}" name changed to: "{self.name}"'
        else:
            return False, message


    def change_description(self, new_description: str) -> tuple[bool, str]:
        ''''''
        description_valid, message = self.validate_description(new_description)

        if description_valid:
            self.description = new_description
            return True, f'Object "{self.name}" description changed to: "{self.description}"'
        else:
            return False, message

    
    @classmethod
    def validate_name(cls, test_name: str) -> tuple[bool, str]:
        ''''''
        
        if isinstance(test_name, str):
            if len(test_name) <= 100:
                if re.match("^[A-Za-z0-9 _-]+$", test_name):
                    return True, ''
                else:
                    return False, 'Supplied name contains invalid characters'    
            else:
                return False, 'Supplied name was greater than 100 characters'
        else:
            return False, 'Supplied name was not a string'


    @classmethod
    def validate_description(cls, test_description: str) -> tuple[bool, str]:
        ''''''
        
        if isinstance(test_description, str):
            if len(test_description) <= 250:
                if re.match("^[A-Za-z0-9 _-]+$", test_description):
                    return True, ''
                else:
                    return False, 'Supplied description contains invalid characters'    
            else:
                return False, 'Supplied description was greater than 250 characters'
        else:
            return False, 'Supplied description was not a string'

    



    