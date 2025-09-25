from Modular_Abaqus_Builder import Modular_Abaqus_Builder
from Analysis_Object import Analysis_Object

def main():
    
    # Instantiate class
    model = Modular_Abaqus_Builder()
    try:
        a = Analysis_Object(model)
    except FileNotFoundError:
        print('error')
    

    #model.main_loop()


if __name__ == '__main__':
    main()