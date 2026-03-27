from __future__ import annotations
import os
import json
import re

'''
-------------------
    TODO
-------------------

- Docstrings
- Tests

'''

class Parameter:
    '''
    ------------------------------
        Object/Model Parameter Class
    ------------------------------
    Parameter class that stores all values relating to a specific parameter.
    ------------------------------
        Attributes
    ------------------------------
    name : str
        The name of the parameter, a string containing letters, numbers and underscores/hyphens.
        It must be less than 101 characters in length.

    dtype : str, [bool, int, float, str]


    value_range : list


    default_value : 


    value : 


    attached_to_model : bool


    ------------------------------
        Methods
    ------------------------------
    
    ------------------------------
        Class Methods
    ------------------------------
    
    ------------------------------
        Examples/Usage
    ------------------------------
    '''

    allowed_dtypes = ['bool', 'int', 'float', 'str']
    keys           = ['name', 'dtype', 'value_range', 'default_value', 'value']

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
        
        temp_dict = {
            'name'          : old_parameter.name,
            'dtype'         : old_parameter.dtype,
            'value_range'   : old_parameter.value_range,
            'default_value' : old_parameter.default_value,
            'value'         : new_value
        }

        return cls.load_from_dict(temp_dict)


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
            value         = data_dict['value']
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

        # Check keys in dict
        if any([key not in data_dict for key in cls.keys]):
            return False

        # Check name is str
        if not isinstance(data_dict['name'], str):
            return False

        # Check name is valid
        if not cls.validate_new_parameter_name(data_dict['name'])[0]:
            return False

        # Check datatype is str and is a valid type
        if (not isinstance(data_dict['dtype'], str)) or (not cls.validate_new_parameter_dtype(data_dict['dtype'])[0]):
            return False

        # Check value_range is a list and has a length of 2
        if (not isinstance(data_dict['value_range'], list)) or (len(data_dict['value_range']) != 2):
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

            # Check default_value within value_range
            if (data_dict['default_value'] < data_dict['value_range'][0]) or (data_dict['default_value'] > data_dict['value_range'][1]):
                return False

            # Check value within value_range
            if (data_dict['value'] < data_dict['value_range'][0]) or (data_dict['value'] > data_dict['value_range'][1]):
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

            # Check default_value within value_range
            if (data_dict['default_value'] < data_dict['value_range'][0]) or (data_dict['default_value'] > data_dict['value_range'][1]):
                return False

            # Check value within value_range
            if (data_dict['value'] < data_dict['value_range'][0]) or (data_dict['value'] > data_dict['value_range'][1]):
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

            # Check default_value within value_range
            if len(data_dict['default_value']) > data_dict['value_range'][1]:
                return False

            # Check value within value_range
            if len(data_dict['value']) > data_dict['value_range'][1]:
                return False

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
            raise FileNotFoundError(f'Could not load file: "{os.path.join(fpath, parameter_file_name)}".')

        return cls.load_from_dict(data_dict)


    def convert_to_dict(self) -> dict:
        '''Converts the parameter to a dictionary representation'''
        return {
            'name'          : self.name,
            'dtype'         : self.dtype,
            'value_range'   : list(self.value_range),
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


    def change_parameter_name(self, new_name) -> tuple[bool, str]:
        ''''''
        name_valid, message = self.validate_new_parameter_name(new_name)

        if name_valid:
            old_name = self.name
            self.name = new_name
            return True, f'Parameter "{old_name}" name changed to: "{self.name}"'
        else:
            return False, message
    

    def change_parameter_dtype(self, new_dtype) -> tuple[bool, str]:
        ''''''
        parameter_dtype, message = self.validate_new_parameter_dtype(new_dtype)

        if parameter_dtype:

            self.dtype         = new_dtype
            self.value_range   = None
            self.value         = None
            self.default_value = None

            return True, f'Parameter "{self.name}" dtype changed to: "{self.dtype}"'
        else:
            return False, message


    def change_parameter_value_range(self, new_value_range) -> tuple[bool, str]:
        ''''''
        parameter_value_range, message = self.validate_new_parameter_value_range(new_value_range)

        if parameter_value_range:

            self.value_range   = new_value_range
            self.value         = None
            self.default_value = None

            return True, f'Parameter "{self.name}" value range changed to: "{self.value_range}"'
        else:
            return False, message


    def change_parameter_default_value(self, new_default_value) -> tuple[bool, str]:
        ''''''
        parameter_valid, message = self.validate_new_parameter_default_value(new_default_value)

        if parameter_valid:
            self.default_value = new_default_value
            return True, f'Parameter "{self.name}" default value changed to: "{self.default_value}"'
        else:
            return False, message


    def change_parameter_value(self, new_value) -> tuple[bool, str]:
        ''''''
        parameter_valid, message = self.validate_new_parameter_value(new_value)

        if parameter_valid:
            self.value = new_value
            return True, f'Parameter "{self.name}" value changed to: "{self.value}"'
        else:
            return False, message


    @classmethod
    def validate_new_parameter_name(cls, test_name: str) -> tuple[bool, str]:
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
    def validate_new_parameter_dtype(cls, test_dtype: str) -> tuple[bool, str]:
        
        if test_dtype in cls.allowed_dtypes:
            return True, ''
        else:
            return False, 'Supplied dtype was not valid'

    
    def validate_new_parameter_value_range(self, test_value_range: list) -> tuple[bool, str]:
        
        if self.dtype == 'bool':
            return False, 'Bool value range cannot be altered'
        
        
        if len(test_value_range) != 2:
            return False, 'Invalid value range length'

        elif self.dtype == 'int':
            if isinstance(test_value_range[0], int) and isinstance(test_value_range[1], int):
                if test_value_range[0] < test_value_range[1]:
                    return True, ''
                else:
                    return False, 'First value in range is greater than second'
            else:
                return False, 'Provided values do not match dtype'

        elif self.dtype == 'float':
            if isinstance(test_value_range[0], float) and isinstance(test_value_range[1], float):
                if test_value_range[0] < test_value_range[1]:
                    return True, ''
                else:
                    return False, 'First value in range is greater than second'
            else:
                return False, 'Provided values do not match dtype'

        elif self.dtype == 'str':
            if isinstance(test_value_range[0], int) and isinstance(test_value_range[1], int):
                if (test_value_range[0] == 0) and (test_value_range[1] > 0):
                    return True
                else:
                    return False, 'Provided value range is not valid'
            else:
                return False, 'Provided values do not match dtype'

        else:
            raise ValueError(f'Current dtype "{self.dtype}" is invalid.')


    def validate_new_parameter_default_value(self, test_default_value) -> tuple[bool, str]:
        '''Validate that default_value provided meets the requirements.'''

        if self.dtype == 'bool':
            if isinstance(test_default_value, bool):
                return True, ''
            else:
                return False, 'Supplied value was not a boolean'


        elif self.dtype == 'int':
            if isinstance(test_default_value, int):
                if (test_default_value >= self.value_range[0]) and (test_default_value <= self.value_range[1]):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not an integer'


        elif self.dtype == 'float':
            if isinstance(test_default_value, float):
                if (test_default_value >= self.value_range[0]) and (test_default_value <= self.value_range[1]):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not a float'


        elif self.dtype == 'str':
            if isinstance(test_default_value, str):
                if (len(test_default_value) <= self.value_range[1]) and (len(test_default_value) != 0):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not a string'


        else:
            raise TypeError(f'The datatype "{self.dtype}" specified in parameter "{self.name}" is not supported.')


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
                if (len(test_value) <= self.value_range[1]) and (len(test_value) != 0):
                    return True, ''
                else:
                    return False, 'Supplied value was not within value range.'
            else:
                return False, 'Supplied value was not a string'


        else:
            raise TypeError(f'The datatype "{self.dtype}" specified in parameter "{self.name}" is not supported.')