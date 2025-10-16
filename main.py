from Modular_Abaqus_Builder import Modular_Abaqus_Builder

def main():

    # Instantiate class
    builder = Modular_Abaqus_Builder(delete_database=False, delete_all_models=True)
    
    builder.main_loop()


''' 
*****************************************************************************************************************************
****************************************************TODO*********************************************************************
*****************************************************************************************************************************

IMPORTANT STUFF
--------------------------

- licence shit guhh
- help/print/verbose print method so same code not repeated 3 times in diff loops
- create small commandline launcher for script
- look at better way to layout imports
- interpreter themes ***IN PROGRESS***
- validate functions for interpreters ***IN PROGRESS***
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