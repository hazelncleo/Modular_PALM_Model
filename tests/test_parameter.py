from src.modularbuilder.parameter import Parameter
import pytest

class TestParameter: # TODO

    eps = 1e-6

    def test_clone_parameter_with_new_name(self): # TODO
        pass


    def test_load_from_dict(self):
        
        test_dict_bool = {
            'name'          : 'Test_1',
            'dtype'         : 'bool',
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : True
        }

        test_param_bool = Parameter.load_from_dict(test_dict_bool)

        assert test_param_bool.name == 'Test_1'
        assert test_param_bool.dtype == 'bool'
        assert test_param_bool.value_range == [False, True]
        assert test_param_bool.default_value == False
        assert test_param_bool.value == True


        test_dict_int = {
            'name'          : 'Test_2',
            'dtype'         : 'int',
            'value_range'   : [-5, 23],
            'default_value' : 8,
            'value'         : 15
        }

        test_param_int = Parameter.load_from_dict(test_dict_int)

        assert test_param_int.name == 'Test_2'
        assert test_param_int.dtype == 'int'
        assert test_param_int.value_range == [-5, 23]
        assert test_param_int.default_value == 8
        assert test_param_int.value == 15

        
        test_dict_float = {
            'name'          : 'Test_3',
            'dtype'         : 'float',
            'value_range'   : [-1.6, 23.5],
            'default_value' : 8.5,
            'value'         : 12.6
        }

        test_param_float = Parameter.load_from_dict(test_dict_float)

        assert test_param_float.name == 'Test_3'
        assert test_param_float.dtype == 'float'
        assert (test_param_float.value_range[0] + 1.6)  < self.eps
        assert (test_param_float.value_range[1] - 23.5) < self.eps
        assert (test_param_float.default_value - 8.5) < self.eps
        assert (test_param_float.value - 12.6) < self.eps


        test_dict_str = {
            'name'          : 'Test_4',
            'dtype'         : 'str',
            'value_range'   : [0, 25],
            'default_value' : 'test string',
            'value'         : 'second test string'
        }

        test_param_str = Parameter.load_from_dict(test_dict_str)

        assert test_param_str.name == 'Test_4'
        assert test_param_str.dtype == 'str'
        assert test_param_str.value_range == [0, 25]
        assert test_param_str.default_value == 'test string'
        assert test_param_str.value == 'second test string'


    def test_validate_dict(self):
        
        test_dict = {}
        assert not Parameter.validate_dict(test_dict)

        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }

        assert Parameter.validate_dict(test_dict)

        test_dict['name'] = 1
        assert not Parameter.validate_dict(test_dict)

        test_dict['name'] = 101 * 'A'
        assert not Parameter.validate_dict(test_dict)

        test_dict['name'] = '****'
        assert not Parameter.validate_dict(test_dict)

        test_dict['name'] = 'Test Name'
        test_dict['dtype'] = 5.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['dtype'] = 'not dtype'
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [False]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [False, True, False]
        assert not Parameter.validate_dict(test_dict)

        # Bool tests
        test_dict['dtype'] = 'bool'
        test_dict['value_range'] = 'wrong type'
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [False, True]
        test_dict['default_value'] = 5.6
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = True
        test_dict['value'] = 25
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = True
        assert Parameter.validate_dict(test_dict)

        # Int tests
        test_dict['dtype'] = 'int'
        test_dict['value_range'] = [0, 100]
        test_dict['default_value'] = 25
        test_dict['value'] = 20
        assert Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0.0, 100]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0, 100.0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [100, 0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0, 100]
        test_dict['default_value'] = 5.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = -25
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 125
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 0
        assert Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 100
        assert Parameter.validate_dict(test_dict)

        test_dict['value'] = 5.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = -25
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = 125
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = 0
        assert Parameter.validate_dict(test_dict)

        test_dict['value'] = 100
        assert Parameter.validate_dict(test_dict)

        # Float tests
        test_dict['dtype'] = 'float'
        test_dict['value_range'] = [0.0, 100.0]
        test_dict['default_value'] = 25.0
        test_dict['value'] = 20.0
        assert Parameter.validate_dict(test_dict)
        
        test_dict['value_range'] = [0.0, 100]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0, 100.0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [100.0, 0.0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0.0, 100.0]
        test_dict['default_value'] = 5
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = -25.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 125.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 0.0
        assert Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 100.0
        assert Parameter.validate_dict(test_dict)

        test_dict['value'] = 5
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = -25.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = 125.0
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = 0.0
        assert Parameter.validate_dict(test_dict)

        test_dict['value'] = 100.0
        assert Parameter.validate_dict(test_dict)

        # String tests
        test_dict['dtype'] = 'str'
        test_dict['value_range'] = [0, 25]
        test_dict['default_value'] = 'Test string'
        test_dict['value'] = 'Second Test String'
        assert Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0.0, 25]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0, 25.0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [25, 0]
        assert not Parameter.validate_dict(test_dict)

        test_dict['value_range'] = [0, 25]
        test_dict['default_value'] = 1
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 26 * 'A'
        assert not Parameter.validate_dict(test_dict)

        test_dict['default_value'] = ''
        assert Parameter.validate_dict(test_dict)

        test_dict['default_value'] = 'Test'
        test_dict['value'] = 1
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = 26 * 'A'
        assert not Parameter.validate_dict(test_dict)

        test_dict['value'] = ''
        assert Parameter.validate_dict(test_dict)

        test_dict['value'] = 'Test'
        assert Parameter.validate_dict(test_dict)


    def test_load_from_file(self): # TODO
        pass

    
    def test_convert_to_dict(self): # TODO
        pass


    def test_save_to_json(self): # TODO
        pass

    
    def test_change_parameter_name(self): # TODO
        pass
    

    def test_change_parameter_dtype(self): # TODO
        pass
    
    
    def test_change_parameter_value_range(self): # TODO
        pass
    
    
    def test_change_parameter_default_value(self): # TODO
        pass
    
    
    def test_change_parameter_value(self): # TODO
        pass

    
    def test_validate_parameter_name(self): # TODO
        pass
    

    def test_validate_parameter_dtype(self): # TODO
        pass
    
    
    def test_validate_parameter_value_range(self): # TODO
        pass
    
    
    def test_validate_parameter_default_value(self): # TODO
        pass
    
    
    def test_validate_parameter_value(self): # TODO
        pass