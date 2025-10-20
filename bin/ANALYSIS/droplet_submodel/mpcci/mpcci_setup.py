import os
import xml.etree.ElementTree as ET

def mpcci_setup(fpath, name, parameters, fluent_cpus = 2, abaqus_cpus = 2):
    '''
    
    '''
    print('-'*60)
    print('"mpcci_setup.py" launched')

    # Get parameter values
    n_cycles = parameters['n_cycles']['default_value']
    vibration_frequency = parameters['vibration_frequency']['default_value']
    
    print('-'*60)
    print('Parameter Values: ')
    print('vibration_frequency = "{}"'.format(vibration_frequency))
    print('n_cycles = "{}"'.format(n_cycles))
    print('-'*60)

    # Calculate Parameter values
    total_time = n_cycles / vibration_frequency
    abaqus_constant_step_size = 1 / (10 * vibration_frequency)

    tree = ET.parse(os.path.join(fpath,'main.csp'))
    root = tree.getroot()

    # Change fluent parameters
    try:
        fluent_child = root.find('./code[@name="FLUENT"]')
        fluent_child.find('.//param[@name = "NumProcs"]').attrib['value'] = str(fluent_cpus)
        print('Fluent CPUS changed to: "{}"'.format(fluent_cpus))
    except:
        print('Fluent Parameters could not be changed.')

    # Chanage abaqus parameters
    try:
        abaqus_child = root.find('./code[@name="Abaqus"]')
        abaqus_child.find('.//param[@name = "CouplingSteps"]/param[@name = "StepSize"]').attrib['value'] = str(abaqus_constant_step_size)
        print('Abaqus constant step size changed to: "{}"'.format(abaqus_constant_step_size))
        abaqus_child.find('.//param[@name = "NumProcs"]').attrib['value'] = str(abaqus_cpus)
        abaqus_child.find('.//param[@name = "NumDomains"]').attrib['value'] = str(abaqus_cpus)
        print('Abaqus CPUS changed to: "{}"'.format(abaqus_cpus))
    except:
        print('Abaqus Parameters could not be changed.')

    # Change mpcci paramters
    try:
        mpcci_child = root.find('./mpcciserver')
        mpcci_child.find('.//param[@name = "TotalTime"]').attrib['value'] = str(total_time)
        print('Total Coupling Time changed to "{}"'.format(total_time))
        mpcci_child.find('.//param[@name = "Jobname"]').attrib['value'] = name
        print('MPCCI Job Name changed to "{}"'.format(name))
    except:
        print('MPCCI Parameters could not be changed.')

    # Write updated file
    tree.write(os.path.join(fpath, name+'.csp'))
    print('Saving update MPCCI .csp file as "{}"'.format(name+'.csp'))