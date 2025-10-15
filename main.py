from Modular_Abaqus_Builder import Modular_Abaqus_Builder


def main():

    # Instantiate class
    builder = Modular_Abaqus_Builder(overwrite=False, overwrite_models=False)
    
    builder.main_loop()


''' 
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------

- create small commandline launcher for script
- look at better way to layout imports
- suppress warnings on pyfluent import
- verbose database print and non verbose
- interpreter themes
- validate functions for interpreters
- if cant delete directories on reset prompt user
- modify model parameters
- postprocess model
- run postprocessing python scripts
- run model


NICE TO HAVE STUFF
-------------------------------
- __repr__
- __str__
- docstrings you dumbass
- main help message
- object help message
- model help message
- run model progress?? :o
'''



if __name__ == '__main__':
    main()    