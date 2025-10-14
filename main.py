from Modular_Abaqus_Builder import Modular_Abaqus_Builder

def main():
    
    # Instantiate class
    builder = Modular_Abaqus_Builder(overwrite=True, overwrite_models=False)
    
    builder.main_loop()


''' 
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------

- if cant delete directories on reset prompt user
- validate database
- model class (pogging off)
- model loop
- parameters
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