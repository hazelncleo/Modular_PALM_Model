import os
import json

class Parameter:
    def __init__(
        self,
        name:          str,
        dtype:         str,
        value_range:   list,
        default_value,
        value
    ) -> None:
        
        self.name              = name
        self.dtype             = dtype
        self.value_range       = value_range
        self.default_value     = default_value
        self.value             = value
        self.attached_to_model = False


    @classmethod
    def clone_parameter_with_new_value(cls, old_parameter: Parameter, new_value) -> Parameter:
        '''Create a new parameter with all attributes identical, except for a new value'''

        return cls(
            name          = old_parameter.name,
            dtype         = old_parameter.dtype,
            value_range   = old_parameter.value_range,
            default_value = old_parameter.default_value,
            value         = new_value
        )


    @classmethod 
    def load_from_dict(cls, data_dict: dict) -> Parameter:
        '''Load a parameter instance from a dictionary'''

        if not cls.validate_dict(data_dict):
            raise ValueError('A parameter could not be created from the data dictionary provided')

        return cls(
            name          = data_dict['name'],
            dtype         = data_dict['dtype'],
            value_range   = data_dict['value_range'],
            default_value = data_dict['default_value'],
            value         = data_dict['default_value']
        )

    
    @classmethod
    def validate_dict(cls, data_dict: dict) -> bool:
        '''
        Validates the provided dictionary to ensure it produces a valid parameter object
        -------------------------------------------------
        Performs the following tests:

        - all keys exist
        - name is str
        - dtype is valid type
        - value_range is valid (i.e. value_range[0] <= value_range[1] for float,int)
        - default_value and value is dtype
        - default_value and value are within value_range
        -------------------------------------------------
        '''

        keys = [
            'name',
            'dtype',
            'value_range',
            'default_value',
            'value'
        ]

        dtypes = [
            'bool',
            'int',
            'float',
            'str'
        ]

        # Check keys in dict
        if any([key not in data_dict for key in keys]):
            return False

        # Check name is str
        if not isinstance(data_dict['name'], str):
            return False

        # Check datatype is str and is a valid type
        if (not isinstance(data_dict['dtype'], str)) or (data_dict['dtype'] not in dtypes):
            return False

        # Check value_range is a list and has a length of 2
        if (not isinstance(data_dict['value_range'], list)) or (len(data_dict['value_range'] != 2)):
            return False
        

        # Validations for bool dtype
        if (data_dict['dtype'] == 'bool'):
            
            # Check value range is valid
            if (data_dict['value_range'] != [False, True]):
                return False

            # Check correct dtypes for values
            if (not isinstance(data_dict['default_value'], bool)) or (not isinstance(data_dict['value'], bool)):
                return False
        

        # Validations for int dtype
        if (data_dict['dtype'] == 'int'):

            # Check value_range correct dtypes
            if (not isinstance(data_dict['value_range'][0], int)) or (not isinstance(data_dict['value_range'][1], int)):
                return False
            
            # Check value_range logically consistent
            if (data_dict['value_range'][0] >= data_dict['value_range'][1]):
                return False

            # Check correct dtypes for values
            if (not isinstance(data_dict['default_value'], int)) or (not isinstance(data_dict['value'], int)):
                return False


        # Validations for float dtype
        if (data_dict['dtype'] == 'float'):

            # Check value_range correct dtypes
            if (not isinstance(data_dict['value_range'][0], float)) or (not isinstance(data_dict['value_range'][1], float)):
                return False

            # Check value_range logically consistent
            if (data_dict['value_range'][0] >= data_dict['value_range'][1]):
                return False

            # Check correct dtypes for values
            if (not isinstance(data_dict['default_value'], float)) or (not isinstance(data_dict['value'], float)):
                return False

        
        # Validations for str dtype
        if (data_dict['dtype'] == 'str'):

            # Check value_range correct dtypes
            if (not isinstance(data_dict['value_range'][0], int)) or (not isinstance(data_dict['value_range'][1], int)):
                return False
            
            # Check value_range logically consistent
            if (data_dict['value_range'][0] != 0) or (data_dict['value_range'][1] < 1):
                return False

            # Check correct dtypes for values
            if (not isinstance(data_dict['default_value'], str)) or (not isinstance(data_dict['value'], str)):
                return False

        # TODO: ADD CHECKS FOR VALUE RANGES, THESE DO NOT WORK
        #if not self.validate_new_parameter_value(data_dict['default_value'])[0]:
        #    return False
        #
        #if not self.validate_new_parameter_value(data_dict['value'])[0]:
        #    return False


        return True


    @classmethod
    def load_from_file(cls, fpath: str, parameter_file_name: str) -> Parameter:
        '''Load a parameter instance from a json file'''

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        try:
            with open(os.path.join(fpath, parameter_file_name), 'r') as parameter_file:
                data_dict = json.load(parameter_file)

        except:
            raise FileNotFoundError(f'Could not load file: "{fpath}".')

        return cls.load_from_dict(data_dict)


    def convert_to_dict(self) -> dict:
        '''Converts the parameter to a dictionary representation'''
        return {
            'name'          : self.name,
            'dtype'         : self.dtype,
            'value_range'   : self.value_range,
            'default_value' : self.default_value,
            'value'         : self.value
        }

    
    def save_to_json_file(self, fpath: str, fname: str) -> None:
        '''Save the parameter to a .json file'''

        data_dict = self.convert_to_dict()

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        try:
            with open(os.path.join(fpath, fname), 'w') as file_to_save:
                json.dump(data_dict, file_to_save)
        except:
            raise FileExistsError('Could not save json file of Parameter: "{self.name}".')


    def validate_new_parameter_value(self, test_value) -> tuple[bool, str]:
        '''Validate that value provided meets the requirements.'''

        if self.dtype == 'bool':
            if isinstance(test_value, bool):
                return True, ''
            else:
                return False, 'Supplied value was not a boolean'


        elif self.dtype == 'int':
            if isinstance(test_value, int):
                if (test_value >= self.value_range[0]) and (test_value <= self.value_range[1]):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not an integer'


        elif self.dtype == 'float':
            if isinstance(test_value, float):
                if (test_value >= self.value_range[0]) and (test_value <= self.value_range[1]):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not a float'


        elif self.dtype == 'str':
            if isinstance(test_value, str):
                if (len(test_value) <= self.value_range[1]):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not a string'


        else:
            raise TypeError(f'The datatype "{self.dtype}" specified in parameter "{self.name}" is not supported.')