import ansys.fluent.core as pyfluent

def fluent_setup(file_name = 'fluent_model.cas.h5', 
                 mesh_file_name = 'fluent_submodel_fluid.msh', 
                 fluent_wd = '',
                 parameters = {'x_grid_position' : {'default_value' : 3},
                               'y_grid_position' : {'default_value' : 3},
                               'vibration_frequency' : {'default_value' : 1.63e6},
                               'n_cycles' : {'default_value' : 50}}):
    '''
    
    '''

    # Get parameter values
    x_grid_position = parameters['x_grid_position']['default_value']
    y_grid_position = parameters['y_grid_position']['default_value']
    vibration_frequency = parameters['vibration_frequency']['default_value']
    n_cycles = parameters['n_cycles']['default_value']

    print('Parameter Values: ')
    print('x_grid_position = "{}"'.format(x_grid_position))
    print('y_grid_position = "{}"'.format(y_grid_position))
    print('vibration_frequency = "{}"'.format(vibration_frequency))
    print('n_cycles = "{}"'.format(n_cycles))

    # Grid spacing between each section
    GRID_SPACING = 0.5e-3

    # Calculate translation coordinates of Fluid Mesh
    X_TRANSLATION = GRID_SPACING*(x_grid_position-3)
    Y_TRANSLATION = GRID_SPACING*(y_grid_position-3)

    # Calculate Total Time and other time stepping parameters
    TOTAL_TIME = n_cycles / vibration_frequency
    MINIMUM_STEP_SIZE = 1/(1000*vibration_frequency)
    MAXIMUM_STEP_SIZE = 1/(50*vibration_frequency)
    INITIAL_STEP_SIZE = 1/(50*vibration_frequency)
    SAVE_FREQUENCY = 1/(10*vibration_frequency)

    # ----------------------------------------------------------------
    # Setup of Model
    # ----------------------------------------------------------------

    print('Instantiating Fluent session, Note: this can take a while.')
    print('----------------------------------------------------------------')
    # Instantiate fluent launcher
    if fluent_wd:
        solver = pyfluent.launch_fluent(mode='solver', ui_mode='hidden_gui', precision='double', processor_count=16, cwd=fluent_wd, start_transcript=False)
    else:
        solver = pyfluent.launch_fluent(mode='solver', ui_mode='hidden_gui', precision='double', processor_count=16, start_transcript=False)

    print('----------------------------------------------------------------')
    print('Fluent session instantiated')

    # Import mesh
    solver.file.read(file_type='case', file_name=mesh_file_name)
    print('Imported mesh file: "{}"'.format(mesh_file_name))

    print('Beginning model setup')
    # Copy fluid materials from database
    solver.settings.setup.materials.database.copy_by_name(type="fluid", name="water-liquid")

    # Set gravity
    solver.setup.general.operating_conditions.gravity = {"enable" : True, 'components' : [0., 0., -9.81]}

    # Set Transient time stepping
    solver.setup.general.solver.time = 'unsteady-1st-order'

    # Set viscosity model to laminar 
    solver.setup.models.viscous.model = 'laminar'

    # Enable VoF model and set related parameters
    solver.setup.models.multiphase = {"models" : "vof"}
    solver.tui.define.models.multiphase.number_of_phases('2')
    solver.tui.define.phases.set_domain_properties.change_phases_names('water', 'air')
    solver.tui.define.models.multiphase.body_force_formulation('yes')
    solver.tui.define.models.multiphase.volume_fraction_parameters.formulation('explicit')
    solver.tui.define.models.multiphase.interface_modeling_options('0', 'no')
    solver.tui.define.phases.set_domain_properties.phase_domains.air.material('yes', 'air')
    solver.tui.define.phases.set_domain_properties.phase_domains.water.material('yes', 'water-liquid')

    # Define phase interactions
    solver.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension.sfc_tension_coeff('yes', 'constant', '0.072')
    solver.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension.sfc_modeling('yes')
    solver.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension.wall_adhesion('yes')
    solver.tui.define.phases.set_domain_properties.interaction_domain.forces.surface_tension.sfc_model_type('yes')

    # Dynamic Meshing
    solver.tui.define.dynamic_mesh.dynamic_mesh('yes', 'no', 'no', 'no', 'no')
    solver.tui.define.dynamic_mesh.controls.smoothing('yes')
    solver.tui.define.dynamic_mesh.zones.create('outlet', 'deforming', 'faceted', 'no', 'yes', 'no', 'no', '0', '0', '0.7', 'no', 'yes')
    solver.tui.define.dynamic_mesh.zones.create('symmetry', 'deforming', 'faceted', 'no', 'yes', 'no', 'no', '0', '0', '0.7', 'no', 'yes')

    # Enable remeshing for highly skewed cells and very small elements
    solver.tui.define.dynamic_mesh.controls.remeshing('yes')
    solver.tui.define.dynamic_mesh.controls.remeshing_parameters.unified_remeshing('no')
    solver.tui.define.dynamic_mesh.controls.remeshing_parameters.remeshing_methods('yes', 'no', 'no', 'no')
    solver.tui.define.dynamic_mesh.controls.remeshing_parameters.length_min('5e-07')
    solver.tui.define.dynamic_mesh.controls.remeshing_parameters.cell_skew_max('0.65')
    
    # Boundary Conditions 
    solver.setup.boundary_conditions.wall['solid_coupling'] = {"phase" : {"mixture" : {"multiphase" : {"contact_angles" : {"water-air" : {"value" : 1.5707961}}}}}}

    # Adaptive Meshing
    solver.tui.mesh.adapt.predefined_criteria.multiphase.vof('1e-08')
    solver.mesh.adapt.set.adaption_method = "hanging-node"
    solver.file.convert_hanging_nodes_during_read = False
    solver.mesh.adapt.set.maximum_refinement_level = 3
    solver.tui.mesh.adapt.manage_criteria.edit('vof_0', 'frequency', '1', 'quit')

    # Methods and Stabilisation
    solver.solution.methods.p_v_coupling.flow_scheme = "PISO"
    solver.solution.methods.discretization_scheme = {"mp" : "geo-reconstruct"}
    solver.solution.methods.vof_numerics = {"unstructured_var_presto_scheme" : False} # this might need to be changed
    solver.solution.methods.multiphase_numerics.solution_stabilization.velocity_limiting_treatment.enable_velocity_limiting = True
    solver.solution.methods.multiphase_numerics.solution_stabilization.velocity_limiting_treatment.set_velocity_cutoff = 500

    # Residuals
    solver.solution.monitor.residual.equations['continuity'].absolute_criteria = 1e-05
    solver.solution.monitor.residual.equations['x-velocity'].absolute_criteria = 1e-05
    solver.solution.monitor.residual.equations['y-velocity'].absolute_criteria = 1e-05
    solver.solution.monitor.residual.equations['z-velocity'].absolute_criteria = 1e-05

    # Translate to position
    print('Translating Mesh by: [x = {}m, y = {}m, z = 0.0m]'.format(X_TRANSLATION,Y_TRANSLATION))
    solver.mesh.translate(offset = [X_TRANSLATION, Y_TRANSLATION, 0])

    # Time stepping controls
    solver.solution.run_calculation.transient_controls.mp_specific_time_stepping = {'enabled' : True,
                                                                                    'global_courant_number' : 1,
                                                                                    'initial_time_step_size' : INITIAL_STEP_SIZE,
                                                                                    'fixed_time_step_size' : 1,
                                                                                    'min_time_step_size' : MINIMUM_STEP_SIZE,
                                                                                    'max_time_step_size' : MAXIMUM_STEP_SIZE,
                                                                                    'min_step_change_factor' : 0.001,
                                                                                    'max_step_change_factor' : 1.2,
                                                                                    'update_interval' : 1}
    solver.solution.run_calculation.transient_controls.duration_specification_method = "total-time"
    solver.solution.run_calculation.transient_controls.total_time = TOTAL_TIME
    solver.solution.run_calculation.transient_controls.max_iter_per_time_step = 65
    solver.solution.run_calculation.transient_controls.multiphase_specific_time_constraints.moving_mesh_cfl_constraint = {"moving_mesh_constraint" : True, "mesh_courant_number" : 1}
    solver.solution.run_calculation.transient_controls.multiphase_specific_time_constraints.physics_based_constraint = True

    # Save frequency controls
    solver.file.auto_save.save_data_file_every = {"frequency_type" : "flow-time"}
    solver.file.auto_save.data_frequency = SAVE_FREQUENCY
    print('Model setup completed successfully')

    # Save to .cas file
    solver.file.write_case(file_name = file_name)
    print('Case file saved as: "{}"'.format(file_name))