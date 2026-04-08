from __future__ import annotations
import os
import json
import re
import warnings

'''
-------------------
    TODO
-------------------

- Docstrings

'''


def save_parameter_dict_to_file(parameter_dict: dict, fpath: str, fname: str) -> None:
    '''Save a dictionary containing parameters to a .json file'''
    dict_to_save = {}

    if not os.path.exists(fpath):
        raise FileNotFoundError(f'Directory "{fpath}" does not exist.')
    
    if os.path.exists(os.path.join(fpath, fname)):
        warnings.warn(f'The file: "{os.path.join(fpath, fname)}" was overwritten when saving.')

    for name,parameter in parameter_dict.items():
        dict_to_save[name] = parameter.convert_to_dict()

    try:
        with open(os.path.join(fpath,fname),'w') as parameter_file:
            json.dump(dict_to_save, parameter_file)
    except:
        raise FileNotFoundError(f'Parameter file could not be saved.')


def load_parameter_dict_from_file(fpath: str, fname: str) -> dict:
    '''Load a dictionary containing parameters from a .json file'''

    output_dict = {}

    if not os.path.exists(fpath):
        raise FileNotFoundError(f'Directory "{fpath}" does not exist.')
    
    if not os.path.exists(os.path.join(fpath, fname)):
        raise FileNotFoundError(f'File "{fname}" does not exist in directory "{fpath}".')

    if not fname.endswith('.json'):
        raise FileNotFoundError(f'File: "{fname}"is not a .json file.')

    try:
        with open(os.path.join(fpath,fname), 'r') as parameter_file:
            loaded_dict = json.load(parameter_file)
    except:
        raise FileNotFoundError(f'Could not load file "{fname}".')

    if not loaded_dict:
        raise ValueError(f'Parameter: "{fname}" could not be loaded.')

    for name,parameter_dict in loaded_dict.items():
        if Parameter.validate_dict(parameter_dict) and (name == parameter_dict['name']):
            output_dict[name] = Parameter.load_from_dict(parameter_dict)
        else:
            raise ValueError(f'Parameter: "{name}" could not be loaded.')
    

    return output_dict



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
        The name of the parameter, a string containing upper/lowercase letters, numbers, spaces and underscores/hyphens.
        It must be less than 101 characters in length.

    dtype : str, [bool, int, float, str]
        Datatype of the parameter.

    solvers : list[str]
        List of solvers the parameter modifies.
        Currently only abaqus, fluent and mpcci are supported

    value_range : list[bool, int, float, str]
        Lower and upper bounds on the values the parameter can take.
        bool: has no effect
        int, float: value_range[0] = lower bound, value_range[1] = upper bound
        str: value_range[0] = 0, value_range[1] = maximum string length

    default_value : bool, int, float, str
        The default value a parameter is assigned. When an object is defined this is the value it will be assigned. Modifying the value of the parameter at this point will modify the default value.

    value : bool, int, float, str
        The value a parameter is assigned. When an object is used to build a model either the default value will be used, or a new value will be assigned. Once the parameter is part of a model modifying its value will modify the value.

    attached_to_model : bool
        True if parameter is attached to a model instead of an object, False otherwise
    ------------------------------
        Examples/Usage
    ------------------------------

    >>> parameter_1 = Parameter.load_from_dict(valid_par_dict)

    >>> parameter_2 = Parameter.load_from_file(fpath, fname)

    >>> paramter_dict = parameter_1.convert_to_dict()
    
    >>> parameter_2.save_to_file(new_fpath, fname)

    '''

    allowed_dtypes = ['bool', 'int', 'float', 'str']
    keys = ['name', 'dtype', 'value_range', 'default_value', 'value']
    supported_softwares = ['abaqus', 'fluent', 'mpcci']

    def __init__(
        self,
        name: str,
        dtype: str,
        solvers: list[str],
        value_range: list,
        default_value,
        value
    ) -> None:
        
        self.name              = name
        self.dtype             = dtype
        self.solvers           = solvers
        self.value_range       = value_range
        self.default_value     = default_value
        self.value             = value
        self.attached_to_model = False


    @classmethod 
    def load_from_dict(cls, data_dict: dict) -> Parameter:
        '''Load a parameter instance from a dictionary'''

        if not cls.validate_dict(data_dict):
            raise ValueError('A parameter could not be created from the data dictionary provided')

        return cls(
            name          = data_dict['name'],
            dtype         = data_dict['dtype'],
            solvers       = data_dict['solvers'],
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
        if not cls.validate_name(data_dict['name'])[0]:
            return False

        # Check datatype is str and is a valid type
        if (not isinstance(data_dict['dtype'], str)) or (not cls.validate_dtype(data_dict['dtype'])[0]):
            return False

        # Check solvers is list
        if (not isinstance(data_dict['solvers'], list)):
            return False

        # Check solvers all entries are strings and all entries valid
        if (any([not isinstance(solver, str) for solver in data_dict['solvers']])) or (not cls.validate_solvers(data_dict['solvers'])[0]):
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
        '''Load a parameter instance from a .json file'''

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        if not parameter_file_name.endswith('.json'):
            raise FileNotFoundError(f'File: "{parameter_file_name}"is not a .json file.')

        if not os.path.exists(os.path.join(fpath, parameter_file_name)):
            raise FileNotFoundError(f'File: "{parameter_file_name}" does not exist.')

        try:
            with open(os.path.join(fpath, parameter_file_name), 'r') as parameter_file:
                data_dict = json.load(parameter_file)

        except:
            raise FileNotFoundError(f'Could not load file: "{os.path.join(fpath, parameter_file_name)}".')

        return cls.load_from_dict(data_dict)


    def convert_to_dict(self) -> dict:
        '''Converts the parameter to a dictionary representation'''

        dict_representation = {
            'name'          : self.name,
            'dtype'         : self.dtype,
            'solvers'       : list(self.solvers),
            'value_range'   : list(self.value_range),
            'default_value' : self.default_value,
            'value'         : self.value
        }

        assert self.validate_dict(dict_representation)

        return dict_representation


    def clone_with_new_value(self, new_value) -> Parameter:
        '''Create a new parameter with all attributes identical, except for a new value'''
        
        temp_dict = {
            'name'          : self.name,
            'dtype'         : self.dtype,
            'solvers'       : list(self.solvers),
            'value_range'   : list(self.value_range),
            'default_value' : self.default_value,
            'value'         : new_value
        }

        return self.load_from_dict(temp_dict)


    def save_to_file(self, fpath: str, fname: str) -> None:
        '''Save the parameter to a .json file'''

        data_dict = self.convert_to_dict()

        if not os.path.exists(fpath):
            raise FileNotFoundError(f'Directory: "{fpath}" does not exist.')

        if os.path.exists(os.path.join(fpath, fname)):
            warnings.warn(f'The file: "{os.path.join(fpath, fname)}" was overwritten when saving.')

        try:
            with open(os.path.join(fpath, fname), 'w') as file_to_save:
                json.dump(data_dict, file_to_save, indent = 4)
        except:
            raise FileExistsError('Could not save json file of Parameter: "{self.name}".')


    def change_name(self, new_name) -> tuple[bool, str]:
        '''Change the name of the parameter'''
        name_valid, message = self.validate_name(new_name)

        if name_valid:
            old_name = self.name
            self.name = new_name
            return True, f'Parameter "{old_name}" name changed to: "{self.name}"'
        else:
            return False, message
    

    def change_dtype(self, new_dtype) -> tuple[bool, str]:
        '''
        Change the dtype of a parameter. 
        
        Note: sets value_range, value and default_value to None
        '''
        parameter_dtype, message = self.validate_dtype(new_dtype)

        if parameter_dtype:

            self.dtype         = new_dtype
            self.value_range   = None
            self.value         = None
            self.default_value = None

            return True, f'Parameter "{self.name}" dtype changed to: "{self.dtype}"'
        else:
            return False, message


    def change_solvers(self, new_solvers: list[str]) -> tuple[bool, str]:
        '''Change the solvers that the parameter modifies'''

        valid_solvers, message = self.validate_solvers(new_solvers)

        if valid_solvers:

            self.solvers = new_solvers
            return True, f'Parameter "{self.name}" modified software solvers changed to: "{self.solvers}".'

        else:
            return False, message


    def change_value_range(self, new_value_range) -> tuple[bool, str]:
        '''
        Change the value range of the parameter
        Note: sets value and default_value to None
        '''
        parameter_value_range, message = self.validate_value_range(new_value_range)

        if parameter_value_range:

            self.value_range   = new_value_range
            self.value         = None
            self.default_value = None

            return True, f'Parameter "{self.name}" value range changed to: "{self.value_range}"'
        else:
            return False, message


    def change_default_value(self, new_default_value) -> tuple[bool, str]:
        '''Change the default value of the parameter'''
        parameter_valid, message = self.validate_default_value(new_default_value)

        if parameter_valid:
            self.default_value = new_default_value
            return True, f'Parameter "{self.name}" default value changed to: "{self.default_value}"'
        else:
            return False, message


    def change_value(self, new_value) -> tuple[bool, str]:
        '''Change the value of the parameter'''
        parameter_valid, message = self.validate_value(new_value)

        if parameter_valid:
            self.value = new_value
            return True, f'Parameter "{self.name}" value changed to: "{self.value}"'
        else:
            return False, message


    @classmethod
    def validate_name(cls, test_name: str) -> tuple[bool, str]:
        '''
        Validate that the provided name meets the following requirements:
            - String
            - Length is less than 101
            - Only contains upper/lowercase letters, numbers, spaces and hyphens/underscores
        '''
        
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
    def validate_dtype(cls, test_dtype: str) -> tuple[bool, str]:
        '''
        Validates that provided datatype is in list of allowed dtypes.
        Currently: bool, int, float, str
        '''
        
        if test_dtype in cls.allowed_dtypes:
            return True, ''
        else:
            return False, 'Supplied dtype was not valid'


    @classmethod
    def validate_solvers(cls, test_solvers: list[str]) -> tuple[bool, str]:
        '''Validates that provided solvers are supported and that parameter modifies at least one solver'''

        if len(test_solvers) != 0:
            if all([(solver in cls.supported_softwares) for solver in test_solvers]):
                return True, ''
            else:
                return False, 'Unsupported software solver included'
        else:
            return False, 'Parameter solvers cannot be empty'

    
    def validate_value_range(self, test_value_range: list) -> tuple[bool, str]:
        '''Validates that provided value range is valid for current dtype'''
        
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
                    return True, ''
                else:
                    return False, 'Provided value range is not valid'
            else:
                return False, 'Provided values do not match dtype'

        else:
            raise ValueError(f'Current dtype "{self.dtype}" is invalid.')


    def validate_default_value(self, test_default_value) -> tuple[bool, str]:
        '''Validate that default_value provided meets the requirements'''

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
            raise ValueError(f'The datatype "{self.dtype}" specified in parameter "{self.name}" is not supported.')


    def validate_value(self, test_value) -> tuple[bool, str]:
        '''Validate that value provided meets the requirements'''

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
            raise ValueError(f'The datatype "{self.dtype}" specified in parameter "{self.name}" is not supported.')