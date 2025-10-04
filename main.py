from Modular_Abaqus_Builder import Modular_Abaqus_Builder
from Analysis_Object import Analysis_Object

def main():
    
    # Instantiate class
    model = Modular_Abaqus_Builder(overwrite=False, overwrite_models=False)
    
    model.main_loop()

'''
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------
- startup error
- finish add material to model

- validate database
- geometry object class
- model class
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