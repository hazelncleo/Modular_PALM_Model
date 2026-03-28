from src.modularbuilder.parameter import Parameter
import pytest
import json
import os

class TestParameter:

    eps = 1e-6

    def test_clone_parameter(self):
        ''''''

        # Bool test
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }
        
        test_param = Parameter.load_from_dict(test_dict)
        clone_param = test_param.clone_with_new_value(False)

        assert test_param.__dict__ == clone_param.__dict__
        assert test_param != clone_param

        with pytest.raises(ValueError):
            clone_param = test_param.clone_with_new_value('wrong dtype')

        clone_param = test_param.clone_with_new_value(True)
        assert (clone_param.value) and (not test_param.value)


        # Int test
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'int',
            'solvers'       : ['abaqus'],
            'value_range'   : [-25, 25],
            'default_value' : 10,
            'value'         : 10
        }

        test_param = Parameter.load_from_dict(test_dict)
        clone_param = test_param.clone_with_new_value(10)

        assert test_param.__dict__ == clone_param.__dict__
        assert test_param != clone_param

        with pytest.raises(ValueError):
            clone_param = test_param.clone_with_new_value('wrong dtype')

        clone_param = test_param.clone_with_new_value(15)
        assert (clone_param.value == 15) and (test_param.value == 10)


        # Float test
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'float',
            'solvers'       : ['abaqus'],
            'value_range'   : [-25.0, 25.0],
            'default_value' : 10.0,
            'value'         : 10.0
        }

        test_param = Parameter.load_from_dict(test_dict)
        clone_param = test_param.clone_with_new_value(10.0)

        assert test_param.__dict__ == clone_param.__dict__
        assert test_param != clone_param

        with pytest.raises(ValueError):
            clone_param = test_param.clone_with_new_value('wrong dtype')

        clone_param = test_param.clone_with_new_value(15.0)
        assert (clone_param.value - 15.0 < self.eps) and (test_param.value - 10 < self.eps)


        # Str test
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'str',
            'solvers'       : ['abaqus'],
            'value_range'   : [0, 20],
            'default_value' : 'test string',
            'value'         : 'test string'
        }

        test_param = Parameter.load_from_dict(test_dict)
        clone_param = test_param.clone_with_new_value('test string')

        assert test_param.__dict__ == clone_param.__dict__
        assert test_param != clone_param

        with pytest.raises(ValueError):
            clone_param = test_param.clone_with_new_value(15)

        clone_param = test_param.clone_with_new_value('clone string')
        assert (clone_param.value == 'clone string') and (test_param.value == 'test string')


    def test_load_from_dict(self):
        
        test_dict_bool = {
            'name'          : 'Test_1',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : True
        }

        test_param_bool = Parameter.load_from_dict(test_dict_bool)

        assert test_param_bool.name == 'Test_1'
        assert test_param_bool.dtype == 'bool'
        assert test_param_bool.solvers == ['abaqus']
        assert test_param_bool.value_range == [False, True]
        assert test_param_bool.default_value == False
        assert test_param_bool.value == True


        test_dict_int = {
            'name'          : 'Test_2',
            'dtype'         : 'int',
            'solvers'       : ['abaqus'],
            'value_range'   : [-5, 23],
            'default_value' : 8,
            'value'         : 15
        }

        test_param_int = Parameter.load_from_dict(test_dict_int)

        assert test_param_int.name == 'Test_2'
        assert test_param_int.dtype == 'int'
        assert test_param_int.solvers == ['abaqus']
        assert test_param_int.value_range == [-5, 23]
        assert test_param_int.default_value == 8
        assert test_param_int.value == 15

        
        test_dict_float = {
            'name'          : 'Test_3',
            'dtype'         : 'float',
            'solvers'       : ['abaqus'],
            'value_range'   : [-1.6, 23.5],
            'default_value' : 8.5,
            'value'         : 12.6
        }

        test_param_float = Parameter.load_from_dict(test_dict_float)

        assert test_param_float.name == 'Test_3'
        assert test_param_float.dtype == 'float'
        assert test_param_float.solvers == ['abaqus']
        assert (test_param_float.value_range[0] + 1.6)  < self.eps
        assert (test_param_float.value_range[1] - 23.5) < self.eps
        assert (test_param_float.default_value - 8.5) < self.eps
        assert (test_param_float.value - 12.6) < self.eps


        test_dict_str = {
            'name'          : 'Test_4',
            'dtype'         : 'str',
            'solvers'       : ['abaqus'],
            'value_range'   : [0, 25],
            'default_value' : 'test string',
            'value'         : 'second test string'
        }

        test_param_str = Parameter.load_from_dict(test_dict_str)

        assert test_param_str.name == 'Test_4'
        assert test_param_str.dtype == 'str'
        assert test_param_str.solvers == ['abaqus']
        assert test_param_str.value_range == [0, 25]
        assert test_param_str.default_value == 'test string'
        assert test_param_str.value == 'second test string'


    def test_validate_dict(self):
        
        test_dict = {}
        assert not Parameter.validate_dict(test_dict)

        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus'],
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

        test_dict['dtype'] = 'bool'
        test_dict['solvers'] = 1
        assert not Parameter.validate_dict(test_dict)

        test_dict['solvers'] = []
        assert not Parameter.validate_dict(test_dict)

        test_dict['solvers'] = [1]
        assert not Parameter.validate_dict(test_dict)

        test_dict['solvers'] = ['not solver']
        assert not Parameter.validate_dict(test_dict)

        test_dict['solvers'] = ['abaqus', 'not solver']
        assert not Parameter.validate_dict(test_dict)

        test_dict['solvers'] = ['abaqus', 'fluent']
        assert Parameter.validate_dict(test_dict)

        test_dict['solvers'] = ['abaqus', 'fluent', 'mpcci']
        assert Parameter.validate_dict(test_dict)

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


    def test_load_from_file(self):
        ''''''

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')

        with pytest.raises(FileNotFoundError):
            Parameter.load_from_file(fpath, 'file_does_not_exist.json')

        with pytest.raises(FileNotFoundError):
            Parameter.load_from_file(fpath, 'not_json.txt')

        with pytest.raises(ValueError):
            Parameter.load_from_file(fpath, 'load_test_wrong.json')
            

        fname = 'load_test_bool.json'        
        bool_param = Parameter.load_from_file(fpath, fname)

        assert bool_param.name == 'Test bool'
        assert bool_param.dtype == 'bool'
        assert bool_param.value_range == [False, True]
        assert bool_param.default_value == False
        assert bool_param.value == True

        fname = 'load_test_int.json'        
        bool_param = Parameter.load_from_file(fpath, fname)

        assert bool_param.name == 'Test int'
        assert bool_param.dtype == 'int'
        assert bool_param.value_range == [0, 15]
        assert bool_param.default_value == 10
        assert bool_param.value == 12

        fname = 'load_test_float.json'        
        bool_param = Parameter.load_from_file(fpath, fname)

        assert bool_param.name == 'Test float'
        assert bool_param.dtype == 'float'
        assert bool_param.value_range == [0.0, 15.0]
        assert bool_param.default_value - 10.0 < self.eps
        assert bool_param.value - 12.0 < self.eps

        fname = 'load_test_str.json'        
        bool_param = Parameter.load_from_file(fpath, fname)

        assert bool_param.name == 'Test str'
        assert bool_param.dtype == 'str'
        assert bool_param.value_range == [0, 15]
        assert bool_param.default_value == 'test string'
        assert bool_param.value == 'test string two'

    
    def test_convert_to_dict(self):
        ''''''

        # Bool test
        test_dict = {
            'name'          : 'Test',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : True
        }

        test_param = Parameter.load_from_dict(test_dict)

        new_dict = test_param.convert_to_dict()

        assert test_dict == new_dict

        # Int test
        test_dict = {
            'name'          : 'Test',
            'dtype'         : 'int',
            'solvers'       : ['abaqus', 'fluent'],
            'value_range'   : [-50, 50],
            'default_value' : 25,
            'value'         : 25
        }

        test_param = Parameter.load_from_dict(test_dict)

        new_dict = test_param.convert_to_dict()

        assert test_dict == new_dict

        # Float test
        test_dict = {
            'name'          : 'Test',
            'dtype'         : 'float',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [-50.0, 50.0],
            'default_value' : 25.0,
            'value'         : 25.0
        }

        test_param = Parameter.load_from_dict(test_dict)

        new_dict = test_param.convert_to_dict()

        assert test_dict == new_dict

        # Str test
        test_dict = {
            'name'          : 'Test',
            'dtype'         : 'str',
            'solvers'       : ['mpcci'],
            'value_range'   : [0, 25],
            'default_value' : 'wow',
            'value'         : 'wow'
        }

        test_param = Parameter.load_from_dict(test_dict)

        new_dict = test_param.convert_to_dict()

        assert test_dict == new_dict


    def test_save_to_file(self):
        ''''''
        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')
        fname = 'test_save.json'

        # Bool tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }

        test_param = Parameter.load_from_dict(test_dict)

        test_param.save_to_file(fpath, fname)

        assert os.path.exists(fpath)
        assert os.path.exists(os.path.join(fpath, fname))

        with open(os.path.join(fpath, fname), 'r') as test_file:
            loaded_dict = json.load(test_file)

        assert test_dict == loaded_dict

        with pytest.warns(Warning):
            test_param.save_to_file(fpath, fname)

        os.remove(os.path.join(fpath, fname))


        # Int tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'int',
            'solvers'       : ['fluent', 'mpcci'],
            'value_range'   : [0, 15],
            'default_value' : 10,
            'value'         : 10
        }

        test_param = Parameter.load_from_dict(test_dict)

        test_param.save_to_file(fpath, fname)

        assert os.path.exists(os.path.join(fpath, fname))

        with open(os.path.join(fpath, fname), 'r') as test_file:
            loaded_dict = json.load(test_file)

        assert test_dict == loaded_dict
        os.remove(os.path.join(fpath, fname))


        # Float tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'float',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [0.0, 15.0],
            'default_value' : 10.0,
            'value'         : 10.0
        }

        test_param = Parameter.load_from_dict(test_dict)

        test_param.save_to_file(fpath, fname)

        assert os.path.exists(os.path.join(fpath, fname))

        with open(os.path.join(fpath, fname), 'r') as test_file:
            loaded_dict = json.load(test_file)

        assert test_dict == loaded_dict
        os.remove(os.path.join(fpath, fname))


        # Str tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'str',
            'solvers'       : ['fluent'],
            'value_range'   : [0, 15],
            'default_value' : 'test string',
            'value'         : 'test string'
        }

        test_param = Parameter.load_from_dict(test_dict)

        test_param.save_to_file(fpath, fname)

        assert os.path.exists(os.path.join(fpath, fname))

        with open(os.path.join(fpath, fname), 'r') as test_file:
            loaded_dict = json.load(test_file)

        assert test_dict == loaded_dict
        os.remove(os.path.join(fpath, fname))
        
    
    def test_validate_parameter_name(self):
        
        assert not Parameter.validate_name('')[0]
        assert Parameter.validate_name('Wow')[0]
        assert Parameter.validate_name('Wow_-123- -123')[0]
        assert not Parameter.validate_name('Fail!')[0]
        assert not Parameter.validate_name('Fail again@')[0]
        assert not Parameter.validate_name(101 * 'A')[0]


    def test_validate_parameter_dtype(self):
        ''''''
        
        assert Parameter.validate_dtype('bool')[0]
        assert Parameter.validate_dtype('int')[0]
        assert Parameter.validate_dtype('float')[0]
        assert Parameter.validate_dtype('str')[0]

        assert not Parameter.validate_dtype(1)[0]
        assert not Parameter.validate_dtype('not_dtype')[0]
    
    
    def test_validate_parameter_solvers(self):
        ''''''

        solvers = []
        assert not Parameter.validate_solvers(solvers)[0]

        solvers = [12]
        assert not Parameter.validate_solvers(solvers)[0]

        solvers = ['not solver']
        assert not Parameter.validate_solvers(solvers)[0]

        solvers = ['abaqus']
        assert Parameter.validate_solvers(solvers)[0]

        solvers = ['abaqus', 'fluent']
        assert Parameter.validate_solvers(solvers)[0]

        solvers = ['abaqus', 'fluent', 'mpcci']
        assert Parameter.validate_solvers(solvers)[0]

        solvers = ['abaqus', 'not solver']
        assert not Parameter.validate_solvers(solvers)[0]

        solvers = ['abaqus', 12]
        assert not Parameter.validate_solvers(solvers)[0]


    def test_validate_parameter_value_range(self):
        
        # Bool tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value_range([False, True])[0]
        
        # Int tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'int',
            'solvers'       : ['mpcci'],
            'value_range'   : [0, 25],
            'default_value' : 10,
            'value'         : 10
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value_range([1, 2, 3])[0]
        assert not test_param.validate_value_range([0.1, 1])[0]
        assert not test_param.validate_value_range([1e-3, 1e3])[0]
        assert not test_param.validate_value_range([0, 'wrong'])[0]
        assert not test_param.validate_value_range([5, 0])[0]
        assert test_param.validate_value_range([0, 100])[0]
        assert test_param.validate_value_range([-1000, 1000])[0]
        assert test_param.validate_value_range([-250000, 250000])[0]

        test_param.dtype = 'wrong_dtype'
        with pytest.raises(ValueError):
            test_param.validate_value_range([1, 100])

        # Float tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'float',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [0.0, 25.0],
            'default_value' : 10.0,
            'value'         : 10.0
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value_range([1,2.5])[0]
        assert not test_param.validate_value_range([0.0, 5])[0]
        assert not test_param.validate_value_range([5.0, -5.0])[0]

        assert test_param.validate_value_range([-10.0, 10.0])[0]
        assert test_param.validate_value_range([-1e3, 1e3])[0]
        assert test_param.validate_value_range([-1e8, 1e8])[0]

        # Str tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'str',
            'solvers'       : ['abaqus'],
            'value_range'   : [0, 25],
            'default_value' : 'wow',
            'value'         : 'super'
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value_range([0.0, 10])[0]
        assert not test_param.validate_value_range([0, 10.0])[0]
        assert not test_param.validate_value_range([-5, 15])[0]
        assert not test_param.validate_value_range([0, -25])[0]

        assert test_param.validate_value_range([0, 5])[0]
        assert test_param.validate_value_range([0, 25])[0]
        assert test_param.validate_value_range([0, 300])[0]
        assert test_param.validate_value_range([0, 5000])[0]

    
    def test_validate_parameter_default_value(self):
        ''''''

        # Bool tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_default_value('wrong type')[0]
        assert test_param.validate_default_value(False)[0]
        assert test_param.validate_default_value(True)[0]

        test_param.dtype = 'wrong_type'
        with pytest.raises(ValueError):
            test_param.validate_default_value(False)

        # Int tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'int',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [-50, 50],
            'default_value' : 25,
            'value'         : 25
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_default_value('wrong type')[0]
        assert not test_param.validate_default_value(51)[0]
        assert not test_param.validate_default_value(-51)[0]
        assert test_param.validate_default_value(0)[0]
        assert test_param.validate_default_value(50)[0]
        assert test_param.validate_default_value(-50)[0]
        assert test_param.validate_default_value(25)[0]

        # Float tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'float',
            'solvers'       : ['abaqus', 'fluent'],
            'value_range'   : [-5e2, 5e2],
            'default_value' : 25.0,
            'value'         : 25.0
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_default_value('wrong type')[0]
        assert not test_param.validate_default_value(-500.1)[0]
        assert not test_param.validate_default_value(500.1)[0]
        assert test_param.validate_default_value(0.0)[0]
        assert test_param.validate_default_value(500.0)[0]
        assert test_param.validate_default_value(-500.0)[0]
        assert test_param.validate_default_value(25.0)[0]

        # Str tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'str',
            'solvers'       : ['abaqus'],
            'value_range'   : [0, 50],
            'default_value' : 'test',
            'value'         : 'test'
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_default_value(25)[0]
        assert not test_param.validate_default_value('')[0]
        assert not test_param.validate_default_value(51 * 'A')[0]
        assert test_param.validate_default_value('A')[0]
        assert test_param.validate_default_value('Wow this should work')[0]
        assert test_param.validate_default_value(50 * 'A')[0]

    
    def test_validate_parameter_value(self):
        ''''''
        
        # Bool tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'bool',
            'solvers'       : ['abaqus', 'fluent', 'mpcci'],
            'value_range'   : [False, True],
            'default_value' : False,
            'value'         : False
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value('wrong type')[0]
        assert test_param.validate_value(False)[0]
        assert test_param.validate_value(True)[0]

        test_param.dtype = 'wrong_type'
        with pytest.raises(ValueError):
            test_param.validate_default_value(False)

        # Int tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'int',
            'solvers'       : ['abaqus'],
            'value_range'   : [-50, 50],
            'default_value' : 25,
            'value'         : 25
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value('wrong type')[0]
        assert not test_param.validate_value(51)[0]
        assert not test_param.validate_value(-51)[0]
        assert test_param.validate_value(0)[0]
        assert test_param.validate_value(50)[0]
        assert test_param.validate_value(-50)[0]
        assert test_param.validate_value(25)[0]

        # Float tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'float',
            'solvers'       : ['fluent'],
            'value_range'   : [-5e2, 5e2],
            'default_value' : 25.0,
            'value'         : 25.0
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value('wrong type')[0]
        assert not test_param.validate_value(-500.1)[0]
        assert not test_param.validate_value(500.1)[0]
        assert test_param.validate_value(0.0)[0]
        assert test_param.validate_value(500.0)[0]
        assert test_param.validate_value(-500.0)[0]
        assert test_param.validate_value(25.0)[0]

        # Str tests
        test_dict = {
            'name'          : 'Test Name',
            'dtype'         : 'str',
            'solvers'       : ['abaqus'],
            'value_range'   : [0, 50],
            'default_value' : 'test',
            'value'         : 'test'
        }

        test_param = Parameter.load_from_dict(test_dict)

        assert not test_param.validate_value(25)[0]
        assert not test_param.validate_value('')[0]
        assert not test_param.validate_value(51 * 'A')[0]
        assert test_param.validate_value('A')[0]
        assert test_param.validate_value('Wow this should work')[0]
        assert test_param.validate_value(50 * 'A')[0]