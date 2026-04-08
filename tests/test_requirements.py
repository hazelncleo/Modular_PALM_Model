from src.modularbuilder.requirements import DatabaseRequirements, ObjectRequirements
import pytest
import json
import os


class TestDatabaseRequirements:
    def test_load_from_dict(self):
        
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

        assert test_reqs.__dict__ == test_dict


    def test_load_from_file(self): # TODO
        pass


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


    def test_add_requirements_from_dict(self): # TODO
        pass