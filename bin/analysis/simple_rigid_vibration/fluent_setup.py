import ansys.fluent.core as pyfluent
from ansys.fluent.core.solver import ( 
    General,
    DynamicMesh,
    Materials,
    Initialization,
    Models
)
import os
from shutil import rmtree



def fluent_setup(
        file_name      = 'fluent_model', 
        mesh_file_name = 'fluent_submodel_fluid.msh', 
        fluent_wd      = '',
        parameters     = {
            'vibration_frequency' : {'default_value' : 1.63e6},
            'n_cycles'            : {'default_value' : 50},
            'amplitude'           : {'default_value' : 1e-6}
        }
    ):
    '''
    ----------------------------------------------------------------
        Builds the sinusoidal rigid body fluent model for a 
        given geometry and operating parameters
        
        Creates a .cas.h5 and .dat.h5 file in the fluent_wd directory
    ----------------------------------------------------------------
    INPUTS
    ----------------------------------------------------------------
    file_name : str
        The file name of the output case and data files
    
    mesh_file_name : str
        The name of mesh file specifying the geometry to be read in.
        
    fluent_wd : str
        The path to the working directory that pyfluent will be run in
    
    parameters : dict
        A dictionary specifying the operating parameters for the model to be built
    ----------------------------------------------------------------
    
    ----------------------------------------------------------------
    '''
    
    # Get parameter values
    vibration_amplitude = parameters['amplitude']['default_value']
    vibration_frequency = parameters['vibration_frequency']['default_value']
    n_cycles = parameters['n_cycles']['default_value']

    print('-'*60)
    print('Parameter Values: ')
    print('Vibration Amplitude                 = {:.1e} micron'.format(vibration_amplitude))
    print('Vibration Frequency                 = {:.2e} Hz'.format(vibration_frequency))
    print('Number of complete Vibration Cycles = {}'.format(n_cycles))
    print('-'*60)

    # Calculate Time stepping values from frequency and number of cycles
    TOTAL_TIME = (n_cycles / vibration_frequency)
    MINIMUM_STEP_SIZE = 1/(1000*vibration_frequency)
    MAXIMUM_STEP_SIZE = 1/(50*vibration_frequency)
    INITIAL_STEP_SIZE = 1/(50*vibration_frequency)
    SAVE_FREQUENCY = 1/(10*vibration_frequency)

    # ----------------------------------------------------------------
    # Setup of Model
    # ----------------------------------------------------------------

    print('Instantiating Fluent session, Note: this can take a while.')
    print('-'*60)
    # Instantiate fluent launcher
    if fluent_wd:
        solver = pyfluent.launch_fluent(
            mode             = 'solver', 
            ui_mode          = 'hidden_gui', 
            precision        = 'double',
            cwd              = fluent_wd, 
            start_transcript = False,
            cleanup_on_exit  = True
        )
    else:
        print('WARNING: No fluent working directory specified')
        solver = pyfluent.launch_fluent(
            mode             = 'solver', 
            ui_mode          = 'hidden_gui', 
            precision        = 'double',
            start_transcript = False,
            cleanup_on_exit  = True
        )

    print('-'*60)
    print('Fluent session instantiated')

    solver.settings.file.read(file_type='case', file_name=mesh_file_name)
    print('Imported mesh file: "{}"'.format(mesh_file_name))

    print('Beginning model setup')

    general_settings = General(solver)

    general_settings.operating_conditions.gravity.enable     = True
    general_settings.operating_conditions.gravity.components = [0., 0., -9.81]
    general_settings.solver.time                             = 'unsteady-1st-order'

    materials = Materials(solver)

    materials.database.copy_by_name(
        type = "fluid",
        name = "water-liquid"
    )

    solver.scheme.eval("(make-new-rpvar 'user/vibration_amplitude {:f} 'real)".format(vibration_amplitude))
    print('Defined rpvar: "user/vibration_amplitude" with value: "{:f}".'.format(vibration_amplitude))

    solver.scheme.eval("(make-new-rpvar 'user/vibration_frequency {:f} 'real)".format(vibration_frequency))
    print('Defined rpvar: "user/vibration_frequency" with value: "{:f}".'.format(vibration_frequency))
    
    model_setup = Models(solver)

    model_setup.viscous.model = 'laminar'

    model_setup.multiphase.models                                              = 'vof'
    model_setup.multiphase.number_of_phases.number_of_eulerian_phases          = 2
    model_setup.multiphase.advanced_formulation.implicit_body_force            = True
    model_setup.multiphase.vof_parameters.vof_formulation                      = 'explicit'
    model_setup.multiphase.phase_interaction.forces.surface_tension_model      = True
    model_setup.multiphase.phase_interaction.forces.surface_tension_model_type = 'Continuum Surface Force'
    model_setup.multiphase.phase_interaction.forces.wall_adhesion              = True

    solver.tui.define.phases.set_domain_properties.change_phases_names('water', 'air') # phase_1 = air, phase_2 = water
    solver.tui.define.phases.set_domain_properties.phase_domains.air.material('yes', 'air')
    solver.tui.define.phases.set_domain_properties.phase_domains.water.material('yes', 'water-liquid')
    
    solver.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension.sfc_tension_coeff(
        'yes', 
        'constant', 
        '0.072'
    )
    
    if os.path.isdir(os.path.join(fluent_wd,'libudf')):
        print('WARNING: Deleting old libudf folder.')
        rmtree(os.path.join(fluent_wd,'libudf'))


    solver.tui.define.user_defined.compiled_functions(
        'compile',
        'libudf',
        'yes',
        os.path.join(fluent_wd, 'simple_vibration.c'),
        '""',
        '""'
    )

    solver.tui.define.user_defined.compiled_functions(
        'load',
        'libudf'
    )

    dynamic_mesh = DynamicMesh(solver)

    dynamic_mesh.enabled                                               = True
    dynamic_mesh.methods.layering.enabled                              = False
    dynamic_mesh.methods.remeshing.enabled                             = False
    dynamic_mesh.methods.smoothing.enabled                             = True
    dynamic_mesh.methods.smoothing.method                              = 'radial'
    dynamic_mesh.methods.smoothing.radial_settings.local_smoothing     = True

    solver.tui.define.dynamic_mesh.zones.create(
        'outlet', 
        'deforming', 
        'faceted', 
        'no', 
        'yes', 
        'no', 
        'no', 
        '0', 
        '0', 
        '0.7', 
        'no', 
        'yes'
    ) 

    solver.tui.define.dynamic_mesh.zones.create(
        'symmetry', 
        'deforming', 
        'faceted', 
        'no', 
        'yes', 
        'no', 
        'no', 
        '0', 
        '0', 
        '0.7', 
        'no', 
        'yes'
    )

    solver.tui.define.dynamic_mesh.zones.create(
        'solid_coupling', 
        'rigid-body', 
        'simple_vibration::libudf', 
        'no', 
        'no', 
        '0', 
        '0', 
        '0', 
        '0', 
        '0', 
        '0', 
        '0', 
        'fluid', 
        'constant', 
        '0', 
        'no', 
        'no'
    )
    
    # Boundary Conditions 
    solver.settings.setup.boundary_conditions.wall['solid_coupling'] = {
        "phase" : {
            "mixture" : {
                "multiphase" : {
                    "contact_angles" : {"water-air" : {"value" : 1.5707961}}
                }
            }
        }
    }

    # Adaptive Meshing
    solver.tui.mesh.adapt.predefined_criteria.multiphase.vof('1e-08')

    solver.settings.mesh.adapt.set.adaption_method          = "hanging-node"
    solver.settings.file.convert_hanging_nodes_during_read  = False
    solver.settings.mesh.adapt.set.maximum_refinement_level = 5 # Base mesh has two elements, therefore 2 * 2^5 = 64 elements across from adaptive meshing.

    solver.tui.mesh.adapt.manage_criteria.edit('vof_0', 'frequency', '1', 'quit')

    # Methods and Stabilisation
    solver.settings.solution.methods.p_v_coupling.flow_scheme                     = "PISO"
    solver.settings.solution.methods.spatial_discretization.discretization_scheme = {"mp" : "geo-reconstruct"}
    solver.settings.solution.methods.vof_numerics                                 = {"unstructured_var_presto_scheme" : False} # this might need to be changed

    solver.settings.solution.methods.multiphase_numerics.solution_stabilization.velocity_limiting_treatment.enable_velocity_limiting = True
    solver.settings.solution.methods.multiphase_numerics.solution_stabilization.velocity_limiting_treatment.set_velocity_cutoff = 500

    # Residuals
    solver.settings.solution.monitor.residual.equations['continuity'].absolute_criteria = 1e-05
    solver.settings.solution.monitor.residual.equations['x-velocity'].absolute_criteria = 1e-05
    solver.settings.solution.monitor.residual.equations['y-velocity'].absolute_criteria = 1e-05
    solver.settings.solution.monitor.residual.equations['z-velocity'].absolute_criteria = 1e-05

    # Time stepping controls
    solver.settings.solution.run_calculation.transient_controls.mp_specific_time_stepping = {
        'enabled'                : True,
        'global_courant_number'  : 1,
        'initial_time_step_size' : INITIAL_STEP_SIZE,
        'fixed_time_step_size'   : 1,
        'min_time_step_size'     : MINIMUM_STEP_SIZE,
        'max_time_step_size'     : MAXIMUM_STEP_SIZE,
        'min_step_change_factor' : 0.001,
        'max_step_change_factor' : 1.2,
        'update_interval'        : 1
    }

    solver.settings.solution.run_calculation.transient_controls.duration_specification_method = "total-time"
    solver.settings.solution.run_calculation.transient_controls.total_time                    = TOTAL_TIME
    solver.settings.solution.run_calculation.transient_controls.max_iter_per_time_step        = 65

    solver.settings.solution.run_calculation.transient_controls.multiphase_specific_time_constraints.moving_mesh_cfl_constraint = {
        "moving_mesh_constraint" : True, 
        "mesh_courant_number"    : 1
    }

    solver.settings.solution.run_calculation.transient_controls.multiphase_specific_time_constraints.physics_based_constraint = True

    # Save frequency controls
    solver.settings.file.auto_save.save_data_file_every = {"frequency_type" : "flow-time"}
    solver.settings.file.auto_save.data_frequency       = SAVE_FREQUENCY
    print('Model setup completed successfully')

    print('Defining Initial Conditions')
    solution_initialization = Initialization(solver)

    solution_initialization.reference_frame = "absolute"

    solution_initialization.initialize()

    solution_initialization.patch.calculate_patch(
        domain                    = "water",
        cell_zones                = ['fluid'],
        registers                 = [],
        variable                  = "mp",
        reference_frame           = "Relative to Cell Zone",
        use_custom_field_function = False,
        value                     = 'IF(Position.z<493.75[micron],1,0)',
    )    

    print('Initial conditions defined successfully')

    # Save to .cas file
    solver.settings.file.write_case(file_name = file_name + '.cas.h5')
    print('Case file saved as: "{}"'.format(file_name + '.cas.h5'))

    solver.settings.file.write_data(file_name = file_name + '.dat.h5')
    print('Data file saved as: "{}"'.format(file_name + '.dat.h5'))
    