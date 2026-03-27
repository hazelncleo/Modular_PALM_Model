from Modular_Abaqus_Builder import Modular_Abaqus_Builder


def main():

    # Instantiate class
    builder = Modular_Abaqus_Builder(delete_database=True, delete_all_models=True)
    
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
- licence shit guhh, including uni signature
- create small commandline launcher for script
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