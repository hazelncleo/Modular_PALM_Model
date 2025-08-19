from Modular_Abaqus_Builder import Modular_Abaqus_Builder

def main():

    # Instantiate class
    model = Modular_Abaqus_Builder()
    
    # Run Command line program
    model.main_loop()


if __name__ == '__main__':
    main()