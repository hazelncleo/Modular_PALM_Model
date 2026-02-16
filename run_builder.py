from Modular_Abaqus_Builder import Modular_Abaqus_Builder
import argparse

def main():

    parser = argparse.ArgumentParser(
        description = 'Modular PALM model builder. Allows for PALM models to be built and modified easily.'
    )

    parser.add_argument('-d', '--delete', help='Deletes the entire database.', action='store_true')
    parser.add_argument('-r', '--reset', help='Deletes the models loaded in the database', action='store_true')
    parser.add_argument('-q', '--quit', help='Quits immediately after loading, useful for deleting/resetting.', action='store_true')

    args = parser.parse_args()

    # Instantiate class
    builder = Modular_Abaqus_Builder(delete_database=args.delete, delete_all_models=args.reset)
    
    if not args.quit:
        builder.main_loop()


''' 
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------

- look at validations (seems better)
- INVALID MODELS GET ARCHIVED
- write test suite (also update methods to call with )
- clean up model class and finish methods
- look at better way to layout imports
- if cant delete directories on reset prompt user
- modify model parameters
- postprocess model
- run postprocessing python scripts
- run model


NICE TO HAVE STUFF
-------------------------------
- parameter storage class and paramter class, requirements class etc.
- __repr__
- __str__
- docstrings you dumbass
- main help message
- object help message
- model help message
- run model progress?? :o
- documentation
- write paper

'''



if __name__ == '__main__':
    main()    