package RM_201_Indoor_Air_Quality_Control {
  part def OutdoorAirSource {
    attribute outdoor_co2_mass_fraction_kgkg : ScalarValues::Real = 0.0004557;
    attribute source_m_flow_command_kg_s : ScalarValues::Real;
    doc /* Canonical source SRC_OA_201 alias freshAir. Baseline outdoor concentration fixed at 300 ppm absolute represented internally as 0.0004557 kg/kg. Modelica source sign convention requires negative command for physical inflow. */
  }

  part def Duct {
    doc /* Generic duct part used for DUCT_IN_201 and DUCT_OUT_201. */
  }

  part def Boundary {
    doc /* Pressure boundary BND_201 alias boundary4 alias exhaust boundary. */
  }

  part def OccupancySchedule {
    attribute occupants_person : ScalarValues::Integer = 0;
    attribute schedule_is_piecewise_constant : ScalarValues::Boolean = true;
    doc /* SCH_OCC_201 alias NumberOfPeople alias OCC_SCH_04 Rev C. Approved weekday occupancy schedule used by the approved 24 h reference run. */
  }

  part def OccupancyGain {
    attribute actual_co2_generation_kg_s : ScalarValues::Real;
    doc /* GAIN_PEO_201 alias gain. Implements G_CO2 = occupants * 8.18E-6 kg/s per person. */
  }

  part def PeopleSource {
    attribute C_source_kgkg : ScalarValues::Real = 100.0;
    attribute people_source_carrier_m_flow_kg_s : ScalarValues::Real;
    doc /* SRC_CO2_201 alias peopleSource alias Occupants. Trace injection uses numerical source concentration 100 kg/kg and carrier mass flow G_CO2/100. Multiple notes explicitly prohibit interpreting C_source = 100 kg/kg as a physical room or outdoor concentration. */
  }

  part def RoomCO2Sensor {
    attribute room_co2_mass_fraction_kgkg : ScalarValues::Real = 0.0004557;
    attribute signal_valid : ScalarValues::Boolean = true;
    attribute invalid_duration_s : ScalarValues::Real = 0.0;
    attribute sensor_fault_indication : ScalarValues::Boolean = false;
    doc /* SEN_CO2_201 alias traceVolume alias room CO2 measurement. Internal simulation/controller signal is kg/kg mass fraction, not ppm. Physical device datasheet characteristics are not used as internal interface units. */
  }

  part def NormalizationGain {
    attribute C_nominal_kgkg : ScalarValues::Real = 0.001519;
    attribute normalized_co2_feedback : ScalarValues::Real;
    doc /* GAIN_NORM_201 alias gainSensor. normalized_CO2 = C_room / C_nominal. */
  }

  part def SetpointSource {
    attribute setpoint_normalized_1 : ScalarValues::Real = 1.0;
    doc /* SET_CO2_201 alias CO2Set. */
  }

  part def OutdoorCO2Constant {
    attribute outdoor_co2_ppm : ScalarValues::Real = 300.0;
    attribute MW_CO2_kg_per_kmol : ScalarValues::Real = 44.01;
    attribute MW_air_kg_per_kmol : ScalarValues::Real = 28.97;
    doc /* SET_OA_201 alias CAtm. IAQ_DAT_001 conversion basis uses MW_CO2 44.01 kg/kmol and MW_air 28.97 kg/kmol. Baseline demonstration uses fixed 300 ppm outdoor concentration corresponding to approximately 4.557E-4 kg/kg. */
  }

  part def AirflowConversionGain {
    attribute room_volume_m3 : ScalarValues::Real = 100.0;
    attribute air_density_kg_m3 : ScalarValues::Real = 1.2;
    attribute kg_s_per_ACH : ScalarValues::Real = 0.0333333333;
    attribute physical_supply_m_flow_kg_s : ScalarValues::Real;
    attribute source_m_flow_command_kg_s : ScalarValues::Real;
    doc /* GAIN_AIR_201 alias gain1. m_supply_physical = ACH_command * V * rho / 3600 with V = 100 m3 and rho = 1.2 kg/m3, giving 0.0333333333 kg/s per ACH. Source command equals negative of physical supply flow per Modelica source-port sign convention. */
  }

  part def RoomVolume {
    attribute room_volume_m3 : ScalarValues::Real = 100.0;
    attribute room_co2_mass_fraction_kgkg : ScalarValues::Real = 0.0004557;
    attribute room_co2_ppm : ScalarValues::Real;
    doc /* ZON_201 alias room alias volume. BIM export is authoritative for room volume only. Room is modeled as one well-mixed air volume. CP-23 requires a well-mixed zone trace-substance balance; supplied notes do not write the full differential equation explicitly. */
  }

  part def Controller {
    attribute Kp_ACH_per_normalized_error : ScalarValues::Real = 6.0;
    attribute output_bias_ACH : ScalarValues::Real = 3.5;
    attribute lower_limit_ACH : ScalarValues::Real = 0.2;
    attribute upper_limit_ACH : ScalarValues::Real = 6.0;
    attribute sensor_fault_output_ACH : ScalarValues::Real = 4.0;
    attribute integral_enabled : ScalarValues::Boolean = false;
    attribute requested_ach_1_per_h : ScalarValues::Real = 0.0;
    attribute ach_command_1_per_h : ScalarValues::Real = 0.2;
    attribute controller_mode : ScalarValues::Integer = 0;
    doc /* CTL_CO2_201 alias PID. Current approved tuning after CR_IAQ_007 is proportional only with integral disabled. Numeric mode encoding follows the merged assumption used by the acceptance checks: AUTO_MIN = 0, AUTO_CO2 = 1, AUTO_MAX = 2, SENSOR_FAULT = 3. */
  }

  part RM_201_System {
    part SRC_OA_201 : OutdoorAirSource;
    part DUCT_IN_201 : Duct;
    part ZON_201 : RoomVolume;
    part DUCT_OUT_201 : Duct;
    part BND_201 : Boundary;
    part SRC_CO2_201 : PeopleSource;
    part SEN_CO2_201 : RoomCO2Sensor;
    part GAIN_NORM_201 : NormalizationGain;
    part CTL_CO2_201 : Controller;
    part SET_CO2_201 : SetpointSource;
    part GAIN_AIR_201 : AirflowConversionGain;
    part SET_OA_201 : OutdoorCO2Constant;
    part SCH_OCC_201 : OccupancySchedule;
    part GAIN_PEO_201 : OccupancyGain;

    attribute time_s : ScalarValues::Real = 0.0;
    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 86400.0;
    attribute logging_interval_s : ScalarValues::Real = 60.0;
    attribute controller_evaluation_step_max_s : ScalarValues::Real = 1.0;
    attribute output_rows_count : ScalarValues::Integer = 1441;
    attribute normalized_co2_feedback : ScalarValues::Real = 0.3;
    attribute occupants_person : ScalarValues::Integer = 0;
    attribute outdoor_co2_ppm : ScalarValues::Real = 300.0;
    attribute outdoor_co2_mass_fraction_kgkg : ScalarValues::Real = 0.0004557;
    attribute room_co2_mass_fraction_kgkg : ScalarValues::Real = 0.0004557;
    attribute room_co2_ppm : ScalarValues::Real;
    attribute ach_command_1_per_h : ScalarValues::Real = 0.2;
    attribute source_m_flow_command_kg_s : ScalarValues::Real;
    attribute physical_supply_m_flow_kg_s : ScalarValues::Real;
    attribute people_source_carrier_m_flow_kg_s : ScalarValues::Real;
    attribute actual_co2_generation_kg_s : ScalarValues::Real;
    attribute controller_mode : ScalarValues::Integer = 0;
    attribute sensor_fault_indication : ScalarValues::Boolean = false;

    connect SRC_OA_201 to DUCT_IN_201;
    connect DUCT_IN_201 to ZON_201;
    connect ZON_201 to DUCT_OUT_201;
    connect DUCT_OUT_201 to BND_201;
    connect SRC_CO2_201 to ZON_201;
    connect SEN_CO2_201 to GAIN_NORM_201;
    connect GAIN_NORM_201 to CTL_CO2_201;
    connect SET_CO2_201 to CTL_CO2_201;
    connect CTL_CO2_201 to GAIN_AIR_201;
    connect GAIN_AIR_201 to SRC_OA_201;
    connect SET_OA_201 to SRC_OA_201;
    connect SCH_OCC_201 to GAIN_PEO_201;
    connect GAIN_PEO_201 to SRC_CO2_201;

    requirement RQ_IAQ_Interlock_SensorFault {
      doc /* Source: 04_04_control_sequence_and_modeling_notes.txt and human-confirmed clarify_sensor_fault_reset_logic. If the room CO2 sensor signal is invalid continuously for more than 60 s, the controller shall enter SENSOR_FAULT, force 4.0 ACH output, and raise sensor fault indication. Exit from SENSOR_FAULT occurs immediately when sensor validity is restored, then the controller returns to the applicable automatic mode according to the requested ACH and output limits. */
    }

    requirement RQ_IAQ_SignConvention_Distinction {
      doc /* Source: owner requirement correspondence and resolved clarify answer resolve_supply_flow_sign. Physical outdoor-air supply flow into the room shall remain positive by physical meaning, while the Modelica outdoor-air source mass-flow command shall be equal magnitude and negative. This implementation sign convention shall not be interpreted as a negative physical ventilation requirement. */
    }

    requirement RQ_IAQ_KgKg_Internal_Interface {
      doc /* Source: ICD_IAQ_03 and resolved clarify answer resolve_sensor_interface_units. The internal simulation and controller CO2 signal interface shall use kg/kg mass fraction followed by normalization gain 1/0.001519. Archived ppm-internal-interface architecture notes are superseded. */
    }

    state OccupancyProgram {
      entry; then Unoccupied_0000_0700;
      state Unoccupied_0000_0700;
      state TwoPersons_0700_0800;
      state EightPersons_0800_1000;
      state TwelvePersons_1000_1200;
      state FourPersons_1200_1300;
      state FifteenPersons_1300_1500;
      state TenPersons_1500_1700;
      state ThreePersons_1700_1800;
      state Unoccupied_1800_2400;

      transition Unoccupied_0000_0700_to_TwoPersons_0700_0800
        first Unoccupied_0000_0700
        if time_s >= 25200.0
        do action { assign occupants_person := 2; }
        then TwoPersons_0700_0800;

      transition TwoPersons_0700_0800_to_EightPersons_0800_1000
        first TwoPersons_0700_0800
        if time_s >= 28800.0
        do action { assign occupants_person := 8; }
        then EightPersons_0800_1000;

      transition EightPersons_0800_1000_to_TwelvePersons_1000_1200
        first EightPersons_0800_1000
        if time_s >= 36000.0
        do action { assign occupants_person := 12; }
        then TwelvePersons_1000_1200;

      transition TwelvePersons_1000_1200_to_FourPersons_1200_1300
        first TwelvePersons_1000_1200
        if time_s >= 43200.0
        do action { assign occupants_person := 4; }
        then FourPersons_1200_1300;

      transition FourPersons_1200_1300_to_FifteenPersons_1300_1500
        first FourPersons_1200_1300
        if time_s >= 46800.0
        do action { assign occupants_person := 15; }
        then FifteenPersons_1300_1500;

      transition FifteenPersons_1300_1500_to_TenPersons_1500_1700
        first FifteenPersons_1300_1500
        if time_s >= 54000.0
        do action { assign occupants_person := 10; }
        then TenPersons_1500_1700;

      transition TenPersons_1500_1700_to_ThreePersons_1700_1800
        first TenPersons_1500_1700
        if time_s >= 61200.0
        do action { assign occupants_person := 3; }
        then ThreePersons_1700_1800;

      transition ThreePersons_1700_1800_to_Unoccupied_1800_2400
        first ThreePersons_1700_1800
        if time_s >= 64800.0
        do action { assign occupants_person := 0; }
        then Unoccupied_1800_2400;
    }

    state ControllerOperatingMode {
      entry; then AUTO_MIN;
      state AUTO_MIN;
      state AUTO_CO2;
      state AUTO_MAX;
      state SENSOR_FAULT;

      transition AUTO_MIN_to_AUTO_CO2
        first AUTO_MIN
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h > CTL_CO2_201.lower_limit_ACH and CTL_CO2_201.requested_ach_1_per_h < CTL_CO2_201.upper_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign CTL_CO2_201.controller_mode := 1; assign ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign controller_mode := 1; assign sensor_fault_indication := false; }
        then AUTO_CO2;

      transition AUTO_MIN_to_AUTO_MAX
        first AUTO_MIN
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h >= CTL_CO2_201.upper_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign CTL_CO2_201.controller_mode := 2; assign ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign controller_mode := 2; assign sensor_fault_indication := false; }
        then AUTO_MAX;

      transition AUTO_MIN_to_SENSOR_FAULT
        first AUTO_MIN
        if not SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s > 60.0
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign CTL_CO2_201.controller_mode := 3; assign SEN_CO2_201.sensor_fault_indication := true; assign ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign controller_mode := 3; assign sensor_fault_indication := true; }
        then SENSOR_FAULT;

      transition AUTO_CO2_to_AUTO_MIN
        first AUTO_CO2
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h <= CTL_CO2_201.lower_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign CTL_CO2_201.controller_mode := 0; assign ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign controller_mode := 0; assign sensor_fault_indication := false; }
        then AUTO_MIN;

      transition AUTO_CO2_to_AUTO_MAX
        first AUTO_CO2
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h >= CTL_CO2_201.upper_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign CTL_CO2_201.controller_mode := 2; assign ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign controller_mode := 2; assign sensor_fault_indication := false; }
        then AUTO_MAX;

      transition AUTO_CO2_to_SENSOR_FAULT
        first AUTO_CO2
        if not SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s > 60.0
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign CTL_CO2_201.controller_mode := 3; assign SEN_CO2_201.sensor_fault_indication := true; assign ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign controller_mode := 3; assign sensor_fault_indication := true; }
        then SENSOR_FAULT;

      transition AUTO_MAX_to_AUTO_CO2
        first AUTO_MAX
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h < CTL_CO2_201.upper_limit_ACH and CTL_CO2_201.requested_ach_1_per_h > CTL_CO2_201.lower_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign CTL_CO2_201.controller_mode := 1; assign ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign controller_mode := 1; assign sensor_fault_indication := false; }
        then AUTO_CO2;

      transition AUTO_MAX_to_AUTO_MIN
        first AUTO_MAX
        if SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s <= 60.0 and CTL_CO2_201.requested_ach_1_per_h <= CTL_CO2_201.lower_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign CTL_CO2_201.controller_mode := 0; assign ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign controller_mode := 0; assign sensor_fault_indication := false; }
        then AUTO_MIN;

      transition AUTO_MAX_to_SENSOR_FAULT
        first AUTO_MAX
        if not SEN_CO2_201.signal_valid and SEN_CO2_201.invalid_duration_s > 60.0
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign CTL_CO2_201.controller_mode := 3; assign SEN_CO2_201.sensor_fault_indication := true; assign ach_command_1_per_h := CTL_CO2_201.sensor_fault_output_ACH; assign controller_mode := 3; assign sensor_fault_indication := true; }
        then SENSOR_FAULT;

      transition SENSOR_FAULT_to_AUTO_MIN
        first SENSOR_FAULT
        if SEN_CO2_201.signal_valid and CTL_CO2_201.requested_ach_1_per_h <= CTL_CO2_201.lower_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign CTL_CO2_201.controller_mode := 0; assign SEN_CO2_201.sensor_fault_indication := false; assign ach_command_1_per_h := CTL_CO2_201.lower_limit_ACH; assign controller_mode := 0; assign sensor_fault_indication := false; }
        then AUTO_MIN;

      transition SENSOR_FAULT_to_AUTO_CO2
        first SENSOR_FAULT
        if SEN_CO2_201.signal_valid and CTL_CO2_201.requested_ach_1_per_h > CTL_CO2_201.lower_limit_ACH and CTL_CO2_201.requested_ach_1_per_h < CTL_CO2_201.upper_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign CTL_CO2_201.controller_mode := 1; assign SEN_CO2_201.sensor_fault_indication := false; assign ach_command_1_per_h := CTL_CO2_201.requested_ach_1_per_h; assign controller_mode := 1; assign sensor_fault_indication := false; }
        then AUTO_CO2;

      transition SENSOR_FAULT_to_AUTO_MAX
        first SENSOR_FAULT
        if SEN_CO2_201.signal_valid and CTL_CO2_201.requested_ach_1_per_h >= CTL_CO2_201.upper_limit_ACH
        do action { assign CTL_CO2_201.ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign CTL_CO2_201.controller_mode := 2; assign SEN_CO2_201.sensor_fault_indication := false; assign ach_command_1_per_h := CTL_CO2_201.upper_limit_ACH; assign controller_mode := 2; assign sensor_fault_indication := false; }
        then AUTO_MAX;
    }

    doc /* System title: RM-201 Indoor Air Quality Control. Seminar / Project Room 201 alias RM-201 with zone alias ZON-201. Initial condition required by commissioning procedure: at time 00:00 room concentration equals outdoor concentration and occupancy is zero. Simulation runs continuously from 0 s to 86400 s. Logging interval 60 s yields 1441 rows including both endpoints. Baseline reference run observed AUTO_MIN and AUTO_CO2 only; AUTO_MAX and SENSOR_FAULT are modeled because the engineering notes establish them, not because the baseline run exercised them. Later modeling stages must implement the well-mixed room trace-substance balance using the established inflow, outflow, and source terms. Reported variables contract for later stages: time_s, occupants_person, outdoor_co2_ppm, outdoor_co2_mass_fraction_kgkg, room_co2_ppm, room_co2_mass_fraction_kgkg, normalized_co2_feedback, ach_command_1_per_h, source_m_flow_command_kg_s, physical_supply_m_flow_kg_s, people_source_carrier_m_flow_kg_s, actual_co2_generation_kg_s, controller_mode, sensor_fault_indication. */
  }
}
