from Modular_Abaqus_Builder import Modular_Abaqus_Builder

def main():

    # Instantiate class
    builder = Modular_Abaqus_Builder(delete_database=False, delete_all_models=False)
    
    builder.main_loop()




''' 
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------

- look at validations
- write test suite
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