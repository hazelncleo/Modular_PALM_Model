from __future__ import annotations

class Model:
    def __init__(self): # TODO
        pass

    
    @classmethod
    def load_from_dict(cls, data_dict: dict) -> Model: # TODO
        pass


    @classmethod
    def load_from_file(cls, fpath: str, fname: str) -> Model: # TODO
        pass


    @classmethod
    def validate_dict(cls, data_dict: dict) -> tuple[bool, str]: # TODO
        pass


    @classmethod
    def build_from_objects(cls, objects: list) -> Model: # TODO
        pass


    def change_name(self, new_name: str) -> tuple[bool, str]: # TODO
        ''''''
        name_valid, message = self.validate_name(new_name)

        if name_valid:
            old_name = self.name
            self.name = new_name
            return True, f'Model "{old_name}" name changed to: "{self.name}"'
        else:
            return False, message


    def change_description(self, new_description: str) -> tuple[bool, str]:
        ''''''
        description_valid, message = self.validate_description(new_description)

        if description_valid:
            self.description = new_description
            return True, f'Model "{self.name}" description changed to: "{self.description}"'
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
