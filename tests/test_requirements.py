from src.modularbuilder.requirements import DatabaseRequirements, ObjectRequirements
import pytest
import json
import os


class TestDatabaseRequirements:
    def test_load_from_dict(self): # TODO
        
        test_dict = {
            'software' : ['abaqus'],
            'analysis' : ['rigid_vibration'],
            'geometry' : ['submodel']
        }

        test_reqs = DatabaseRequirements.load_from_dict(test_dict)

        assert test_reqs.__dict__ == test_dict


    def test_load_from_file(self):
        ''''''

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')

        with pytest.raises(FileNotFoundError):
            DatabaseRequirements.load_from_file('fpath_does_not_exist', 'file.json')
        
        with pytest.raises(FileNotFoundError):
            DatabaseRequirements.load_from_file(fpath, 'not_json.txt')

        with pytest.raises(FileNotFoundError):
            DatabaseRequirements.load_from_file(fpath, 'nonexistent.json')

        with pytest.raises(FileNotFoundError):
            DatabaseRequirements.load_from_file(fpath, 'empty.json')

        with pytest.raises(ValueError):
            DatabaseRequirements.load_from_file(fpath, 'empty_dict.json')

        with pytest.raises(ValueError):
            DatabaseRequirements.load_from_file(fpath, 'load_test_str.json')

        reqs = DatabaseRequirements.load_from_file(fpath, 'load_test_req.json')
        assert reqs.software == ['abaqus', 'fluent', 'mpcci']
        assert reqs.analysis == ['model_1', 'model_2']
        assert reqs.geometry == ['grid', 'straight']


    def test_validate_dict(self):

        assert not DatabaseRequirements.validate_dict(1)

        assert not DatabaseRequirements.validate_dict(1.0)

        assert not DatabaseRequirements.validate_dict('wrong dtype')
        
        test_dict = {}
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict[1] = 'key wrong type'
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict.pop(1)
        test_dict['wrong key'] = 'test'
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict.pop('wrong key')
        test_dict['software'] = 'abaqus'
        assert not DatabaseRequirements.validate_dict(test_dict)
        
        test_dict['software'] = ['abaqus']
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict['software'] = []
        test_dict['analysis'] = []
        test_dict['geometry'] = []
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict['software'] = ['software']
        test_dict['analysis'] = ['analysis']
        test_dict['geometry'] = ['geometry']
        assert DatabaseRequirements.validate_dict(test_dict)

        test_dict['software'] = ['&invalid character']
        assert not DatabaseRequirements.validate_dict(test_dict)

        test_dict['software'] = [101*'A']
        assert not DatabaseRequirements.validate_dict(test_dict)
        test_dict['software'] = ['']
        assert not DatabaseRequirements.validate_dict(test_dict)


    def test_add_requirements_from_dict(self):
        ''''''

        test_dict = {
            'software' : [
                'abaqus'
            ],
            'analysis' : [
                'rigid_vibration'
            ],
            'geometry' : [
                'submodel'
            ]
        }

        test_reqs = DatabaseRequirements.load_from_dict(test_dict)

        add_dict = {}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = 'wrong type'
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'wrong key' : 'wrong'}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : 25}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : [1], 'analysis' : ['new']}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : ['']}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : [' ']}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : ['&']}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : [101*'A']}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : ['new']}
        test_reqs.add_requirements_from_dict(add_dict)

        add_dict = {'software' : ['epic'], 'analysis' : []}
        test_reqs.add_requirements_from_dict(add_dict)

        assert test_reqs.software == ['abaqus', 'epic']
        assert test_reqs.analysis == ['rigid_vibration', 'new']
        assert test_reqs.geometry == ['submodel']

        add_dict = {'geometry' : ['woah', 'cool_beans', 'epic']}
        test_reqs.add_requirements_from_dict(add_dict)
        assert test_reqs.geometry == ['submodel', 'woah', 'cool_beans', 'epic']

        add_dict = {'analysis' : ['correct', 'right', 1]}
        with pytest.raises(ValueError):
            test_reqs.add_requirements_from_dict(add_dict)
        assert test_reqs.analysis == ['rigid_vibration', 'new']