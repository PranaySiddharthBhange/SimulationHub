package Fan_spinup_with_viscous_and_quadratic_aerodynamic_losses {
  part def RotationalInertiaElement {
    attribute J_kg_m2 : ScalarValues::Real = 0.02;
  }

  part def MotorElement {
    attribute motor_on_cmd : ScalarValues::Boolean = false;
    attribute motor_torque_Nm : ScalarValues::Real = 0.0;
    attribute torque_magnitude_Nm : ScalarValues::Real = 0.5;
    attribute motor_start_time_s : ScalarValues::Real = 5.0;
  }

  part def BearingFrictionElement {
    attribute b_Nm_s_per_rad : ScalarValues::Real = 0.01;
  }

  part def AerodynamicLoadElement {
    attribute k_fan_Nm_s2_per_rad2 : ScalarValues::Real = 0.0004;
  }

  part def FanRotorAssembly {
    doc /* Fan wheel and shaft rotate together as the fan's single rotational degree of freedom. */
    attribute fan_speed_rad_s : ScalarValues::Real = 0.0;
    attribute initial_fan_speed_rad_s : ScalarValues::Real = 0.0;
    attribute rated_nameplate_speed_rad_s : ScalarValues::Real = 30.0;
    attribute steady_state_speed_required_rad_s : ScalarValues::Real = 25.0;
    part fan_wheel;
    part shaft;
    part rotational_inertia : RotationalInertiaElement;
  }

  part Fan_system {
    attribute time_s : ScalarValues::Real;
    attribute simulation_duration_s : ScalarValues::Real = 60.0;

    part fan_rotor_assembly : FanRotorAssembly;
    part motor : MotorElement;
    part bearing_friction : BearingFrictionElement;
    part aerodynamic_load : AerodynamicLoadElement;

    connect motor to fan_rotor_assembly;
    connect bearing_friction to fan_rotor_assembly;
    connect aerodynamic_load to fan_rotor_assembly;

    doc /* Explicit continuous relationships from 01_fan_nonideal_spinup.txt: T_friction = b * omega, T_aero = k_fan * omega^2, and J * domega_dt = T_motor - b*omega - k_fan*omega^2. Unit check stated in source: b*omega gives N*m and k_fan*omega^2 gives N*m, so the torque balance is dimensionally consistent. Derived consequence from stated equations and steady state condition domega_dt = 0: 0.5 = 0.01*omega + 0.0004*omega^2, whose exact positive solution is omega = 25 rad/s. */

    state MotorCommandSequence {
      entry; then Motor_Off;
      state Motor_Off;
      state Motor_On;

      transition Motor_Off_to_Motor_On
        first Motor_Off
        if time_s >= 5.0
        do action { assign motor.motor_on_cmd := true; assign motor.motor_torque_Nm := 0.5; }
        then Motor_On;
    }

    requirement Motor_turn_on_schedule {
      doc /* Source: 01_fan_nonideal_spinup.txt. The only scheduled command is a single motor turn-on at t = 5 s. Before t = 5 s motor_on_cmd is 0 and from t = 5 s onward motor_on_cmd is 1. */
    }

    requirement Fixed_torque_when_on {
      doc /* Source: 01_fan_nonideal_spinup.txt and Merge assumption. The motor applies a fixed, constant driving torque. motor_torque_Nm is 0 N*m while motor_on_cmd is false and 0.5 N*m while motor_on_cmd is true. */
    }

    requirement Single_degree_of_freedom_rotation {
      doc /* Source: 01_fan_nonideal_spinup.txt. The fan wheel and shaft rotate together as the fan's single rotational degree of freedom. */
    }

    requirement No_additional_discrete_behavior {
      doc /* Source: 01_fan_nonideal_spinup.txt. No additional states, modes, pause_resume behavior, abort_reset logic, or scheduled commands beyond the single motor turn-on at t = 5 s are established by the brief. */
    }
  }
}