import ansys.fluent.core as pyfluent

def fluent_setup(file_name = 'fluent_model.cas.h5', 
                 mesh_file_name = 'fluent_whole-chip_fluid.msh', 
                 fluent_wd = '',
                 total_time = 0.001):
    '''
    
    '''

    # Calculate Total Time and other time stepping parameters
    TOTAL_TIME = total_time
    MINIMUM_STEP_SIZE = total_time*1e-6
    MAXIMUM_STEP_SIZE = total_time*1e-3
    INITIAL_STEP_SIZE = total_time*1e-4
    SAVE_FREQUENCY = total_time*1e-3

    # ----------------------------------------------------------------
    # Setup of Model
    # ----------------------------------------------------------------

    # Instantiate fluent launcher
    if fluent_wd:
        solver = pyfluent.launch_fluent(mode='solver', show_gui=False, precision='double', processor_count=16, cwd=fluent_wd)
    else:
        solver = pyfluent.launch_fluent(mode='solver', show_gui=False, precision='double', processor_count=16)

    # Import mesh
    solver.file.read(file_type='case', file_name=mesh_file_name)

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

    # Save frequency controls
    solver.file.auto_save.save_data_file_every = {"frequency_type" : "flow-time"}
    solver.file.auto_save.data_frequency = SAVE_FREQUENCY

    # Save to .cas file
    solver.tui.file.write_case(file_name)