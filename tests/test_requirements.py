from src.modularbuilder.requirements import Requirements
import pytest
import json
import os


class TestRequirements:
    def test_load_from_dict(self):
        
        test_dict = {
            'software' : ['abaqus'],
            'analysis' : ['rigid_vibration'],
            'geometry' : ['submodel']
        }

        test_reqs = Requirements.load_from_dict(test_dict)

        assert test_reqs.__dict__ == test_dict

        database_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'rigid_vibration_noisy',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_50um',
                'submodel_40um'
                'submodel_30um'
            ]
        }

        test_reqs = Requirements.load_from_dict(database_dict)

        assert test_reqs.__dict__ == database_dict


    def test_load_from_file(self):
        ''''''

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')

        with pytest.raises(FileNotFoundError):
            Requirements.load_from_file('fpath_does_not_exist', 'file.json')
        
        with pytest.raises(FileNotFoundError):
            Requirements.load_from_file(fpath, 'not_json.txt')

        with pytest.raises(FileNotFoundError):
            Requirements.load_from_file(fpath, 'nonexistent.json')

        with pytest.raises(FileNotFoundError):
            Requirements.load_from_file(fpath, 'empty.json')

        with pytest.raises(ValueError):
            Requirements.load_from_file(fpath, 'empty_dict.json')

        with pytest.raises(ValueError):
            Requirements.load_from_file(fpath, 'load_test_str.json')

        reqs = Requirements.load_from_file(fpath, 'load_test_req.json')
        assert reqs.software == ['abaqus', 'fluent', 'mpcci']
        assert reqs.analysis == ['model_1', 'model_2']
        assert reqs.geometry == ['grid', 'straight']


    def test_validate_dict(self):

        assert not Requirements.validate_dict(1)

        assert not Requirements.validate_dict(1.0)

        assert not Requirements.validate_dict('wrong dtype')
        
        test_dict = {}
        assert not Requirements.validate_dict(test_dict)

        test_dict[1] = 'key wrong type'
        assert not Requirements.validate_dict(test_dict)

        test_dict.pop(1)
        test_dict['wrong key'] = 'test'
        assert not Requirements.validate_dict(test_dict)

        test_dict.pop('wrong key')
        test_dict['software'] = 'abaqus'
        assert not Requirements.validate_dict(test_dict)
        
        test_dict['software'] = ['abaqus']
        assert not Requirements.validate_dict(test_dict)

        test_dict['software'] = []
        test_dict['analysis'] = []
        test_dict['geometry'] = []
        assert not Requirements.validate_dict(test_dict)

        test_dict['software'] = ['software']
        test_dict['analysis'] = ['analysis']
        test_dict['geometry'] = ['geometry']
        assert Requirements.validate_dict(test_dict)

        test_dict['software'] = ['&invalid character']
        assert not Requirements.validate_dict(test_dict)

        test_dict['software'] = [101*'A']
        assert not Requirements.validate_dict(test_dict)
        test_dict['software'] = ['']
        assert not Requirements.validate_dict(test_dict)


    def test_save_to_file(self):
        ''''''

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')
        fname = 'test_save.json'

        test_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'rigid_vibration_noisy',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_50um',
                'submodel_40um'
                'submodel_30um'
            ]
        }

        test_reqs = Requirements.load_from_dict(test_dict)
        test_reqs.save_to_file(fpath, fname)

        assert os.path.exists(fpath)
        assert os.path.exists(os.path.join(fpath, fname))

        with open(os.path.join(fpath, fname), 'r') as test_file:
            loaded_dict = json.load(test_file)

        assert test_dict == loaded_dict

        with pytest.warns(Warning):
            test_reqs.save_to_file(fpath, fname)

        os.remove(os.path.join(fpath, fname))


    def test_convert_to_dict(self):
        ''''''

        database_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'rigid_vibration_noisy',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_50um',
                'submodel_40um'
                'submodel_30um'
            ]
        }

        database_reqs = Requirements.load_from_dict(database_dict)
        converted_dict = database_reqs.convert_to_dict()

        assert database_reqs.__dict__ == converted_dict
        assert converted_dict == database_dict


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

        test_reqs = Requirements.load_from_dict(test_dict)

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

        add_dict = {'software' : ['epic'], 'analysis' : ['+']}
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


    def test_add_requirements_from_file(self):
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

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')
        fname = 'load_test_req.json'

        test_reqs = Requirements.load_from_dict(test_dict)
        test_reqs.add_requirements_from_file(fpath, fname)

        final_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'model_1',
                'model_2'
            ],
            'geometry' : [
                'submodel',
                'grid',
                'straight'
            ]
        }

        assert final_dict == test_reqs.__dict__


    def test_add_requirements_from_requirements(self):
        
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

        cwd = os.getcwd()
        fpath = os.path.join(cwd, 'tests', 'test_data')
        fname = 'load_test_req.json'

        test_reqs = Requirements.load_from_dict(test_dict)
        new_reqs = Requirements.load_from_file(fpath, fname)

        test_reqs.add_requirements_from_requirements(new_reqs)

        final_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'model_1',
                'model_2'
            ],
            'geometry' : [
                'submodel',
                'grid',
                'straight'
            ]
        }

        assert final_dict == test_reqs.__dict__


    def test_remove_requirements_from_dict(self):
        ''''''

        database_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'rigid_vibration_noisy',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_50um',
                'submodel_40um',
                'submodel_30um'
            ]
        }

        database_reqs = Requirements.load_from_dict(database_dict)

        reqs_to_remove = {
            'software' : [
                'abaqus'
            ],
            'analysis' : [
                'rigid_vibration_noisy'
            ],
            'geometry' : [
                'submodel_50um',
                'submodel_40um'
            ]
        }

        final_dict = {
            'software' : [
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_30um'
            ]
        }

        database_reqs.remove_requirements_from_dict(reqs_to_remove)
        assert final_dict == database_reqs.__dict__


    def test_requirement_is_subset(self):
        ''''''

        database_dict = {
            'software' : [
                'abaqus',
                'fluent',
                'mpcci'
            ],
            'analysis' : [
                'rigid_vibration',
                'rigid_vibration_noisy',
                'solid_coupled'
            ],
            'geometry' : [
                'submodel_60um',
                'submodel_50um',
                'submodel_40um'
                'submodel_30um'
            ]
        }

        database_reqs = Requirements.load_from_dict(database_dict)

        requirement_dict = {
            'software' : [
                'abaqus'
            ],
            'analysis' : [
                'rigid_vibration'
            ],
            'geometry' : [
                'submodel_50um'
            ]
        }

        requirement_reqs = Requirements.load_from_dict(requirement_dict)
        assert database_reqs.requirements_is_subset(requirement_reqs)

        requirement_dict = {
            'software' : [
                'not software'
            ]
        }
        requirement_reqs.add_requirements_from_dict(requirement_dict)
        assert not database_reqs.requirements_is_subset(requirement_reqs)