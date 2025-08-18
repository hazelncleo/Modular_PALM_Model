from Modular_Abaqus_Builder import Modular_Abaqus_Builder
from inquirer import list_input


def main():
    

    model = Modular_Abaqus_Builder()
    
    model.main_loop()


            

if __name__ == '__main__':
    main()