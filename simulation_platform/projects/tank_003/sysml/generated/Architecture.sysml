package Architecture {
    part def TK_101;
    part def TK_102;
    part def XV_101;
    part def XV_102;
    part def XV_103;
    part def PLC_101;
    part def LT_101;
    part def LT_102;
    part def Tank_Filling_Emptying_System;
    part def PB_START;
    part def PB_STOP;
    part def PB_SHUT;
    part def SRC_101;
    part def DRN_101;
    part def source;
    part def valve1;
    part def tank1;
    part def valve2;
    part def tank2;
    part def valve3;
    part def ambient1;
    part def tankController;
    part def SRC;
    part def V1;
    part def T1;
    part def V2;
    part def T2;
    part def V3;
    part def DRN;
    part def Two_Tank_Fill_Transfer_Drain_Controller;
    part def STOP;
    part def START;
    part def SHUT;
    part def Drain_valve;
    part def TankDemo_Rev12;
    part def VXS_24_spring_return_two_position_liquid_isolation_valve;
    part def _24_VDC_actuator;
    part def Controller;
    part tK_101 : TK_101;
    part tK_102 : TK_102;
    part xV_101 : XV_101;
    part xV_102 : XV_102;
    part xV_103 : XV_103;
    part plC_101 : PLC_101;
    part lT_101 : LT_101;
    part lT_102 : LT_102;
    part tank_Filling_Emptying_System : Tank_Filling_Emptying_System;
    part pB_START : PB_START;
    part pB_STOP : PB_STOP;
    part pB_SHUT : PB_SHUT;
    part srC_101 : SRC_101;
    part drN_101 : DRN_101;
    part source : source;
    part valve1 : valve1;
    part tank1 : tank1;
    part valve2 : valve2;
    part tank2 : tank2;
    part valve3 : valve3;
    part ambient1 : ambient1;
    part tankController : tankController;
    part src : SRC;
    part v1 : V1;
    part t1 : T1;
    part v2 : V2;
    part t2 : T2;
    part v3 : V3;
    part drn : DRN;
    part two_Tank_Fill_Transfer_Drain_Controller : Two_Tank_Fill_Transfer_Drain_Controller;
    part stop : STOP;
    part start : START;
    part shut : SHUT;
    part drain_valve : Drain_valve;
    part tankDemo_Rev12 : TankDemo_Rev12;
    part vxS_24_spring_return_two_position_liquid_isolation_valve : VXS_24_spring_return_two_position_liquid_isolation_valve;
    part _24_VDC_actuator : _24_VDC_actuator;
    part controller : Controller;
    connect plC_101 to lT_101;  // requires
    connect plC_101 to lT_102;  // requires
    connect xV_101 to tK_101;  // serves
    connect xV_102 to tK_101;  // serves
    connect xV_102 to tK_102;  // serves
    connect xV_103 to tK_102;  // serves
    connect plC_101 to xV_101;  // controls
    connect plC_101 to xV_102;  // controls
    connect plC_101 to xV_103;  // controls
    connect lT_101 to tK_101;  // serves
    connect lT_102 to tK_102;  // serves
    connect tank_Filling_Emptying_System to plC_101;  // contains
    connect tank_Filling_Emptying_System to tK_101;  // contains
    connect tank_Filling_Emptying_System to tK_102;  // contains
    connect tank_Filling_Emptying_System to xV_101;  // contains
    connect tank_Filling_Emptying_System to xV_102;  // contains
    connect tank_Filling_Emptying_System to xV_103;  // contains
    connect tank_Filling_Emptying_System to lT_101;  // contains
    connect tank_Filling_Emptying_System to lT_102;  // contains
    connect tank_Filling_Emptying_System to pB_START;  // contains
    connect tank_Filling_Emptying_System to pB_STOP;  // contains
    connect tank_Filling_Emptying_System to pB_SHUT;  // contains
    connect tank_Filling_Emptying_System to srC_101;  // contains
    connect tank_Filling_Emptying_System to drN_101;  // contains
    connect tK_101 to lT_101;  // connected_to
    connect tK_102 to lT_102;  // connected_to
    connect srC_101 to xV_101;  // connected_to
    connect xV_101 to tK_101;  // connected_to
    connect tK_101 to xV_102;  // connected_to
    connect xV_102 to tK_102;  // connected_to
    connect tK_102 to xV_103;  // connected_to
    connect xV_103 to drN_101;  // connected_to
    connect lT_101 to plC_101;  // connected_to
    connect lT_102 to plC_101;  // connected_to
    connect pB_START to plC_101;  // connected_to
    connect pB_STOP to plC_101;  // connected_to
    connect pB_SHUT to plC_101;  // connected_to
    connect plC_101 to xV_101;  // connected_to
    connect plC_101 to xV_102;  // connected_to
    connect plC_101 to xV_103;  // connected_to
    connect xV_101 to tK_101;  // supplies
    connect xV_102 to tK_102;  // supplies
    connect xV_103 to drN_101;  // supplies
    connect srC_101 to xV_101;  // supplies
    connect plC_101 to xV_101;  // controls
    connect plC_101 to xV_102;  // controls
    connect plC_101 to xV_103;  // controls
    connect pB_START to plC_101;  // signal_flow
    connect pB_STOP to plC_101;  // signal_flow
    connect pB_SHUT to plC_101;  // signal_flow
    connect lT_101 to plC_101;  // signal_flow
    connect lT_102 to plC_101;  // signal_flow
    connect plC_101 to xV_101;  // signal_flow
    connect plC_101 to xV_102;  // signal_flow
    connect plC_101 to xV_103;  // signal_flow
    connect xV_101 to tK_101;  // depends_on
    connect xV_102 to tK_102;  // depends_on
    connect xV_103 to drN_101;  // depends_on
    connect pB_START to plC_101;  // triggers
    connect pB_STOP to plC_101;  // triggers
    connect pB_SHUT to plC_101;  // triggers
    connect lT_101 to plC_101;  // responds_to
    connect lT_102 to plC_101;  // responds_to
    connect plC_101 to xV_101;  // controls
    connect plC_101 to xV_102;  // controls
    connect plC_101 to xV_103;  // controls
    connect source to valve1;  // connected_to
    connect valve1 to tank1;  // connected_to
    connect tank1 to valve2;  // connected_to
    connect valve2 to tank2;  // connected_to
    connect tank2 to valve3;  // connected_to
    connect ambient1 to valve3;  // connected_to
    connect tankController to valve1;  // connected_to
    connect tankController to valve2;  // connected_to
    connect tankController to valve3;  // connected_to
    connect src to v1;  // connected_to
    connect v1 to t1;  // connected_to
    connect t1 to v2;  // connected_to
    connect v2 to t2;  // connected_to
    connect t2 to v3;  // connected_to
    connect v3 to drn;  // connected_to
    connect src to drn;  // connected_to
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0039 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0031 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0032 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0033 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0034 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0035 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0036 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0037 (state def)
    // not rendered as connect() -- ENT-0030 (part def) contains ENT-0038 (state def)
    // not rendered as connect() -- ENT-0031 (state def) connected_to ENT-0032 (state def)
    // not rendered as connect() -- ENT-0032 (state def) connected_to ENT-0033 (state def)
    // not rendered as connect() -- ENT-0033 (state def) connected_to ENT-0034 (state def)
    // not rendered as connect() -- ENT-0034 (state def) connected_to ENT-0035 (state def)
    // not rendered as connect() -- ENT-0035 (state def) connected_to ENT-0036 (state def)
    // not rendered as connect() -- ENT-0036 (state def) connected_to ENT-0031 (state def)
    // not rendered as connect() -- ENT-0039 (state def) triggers ENT-0031 (state def)
    // not rendered as connect() -- ENT-0032 (state def) triggers ENT-0033 (state def)
    // not rendered as connect() -- ENT-0034 (state def) triggers ENT-0035 (state def)
    // not rendered as connect() -- ENT-0036 (state def) triggers ENT-0031 (state def)
    // not rendered as connect() -- ENT-0038 (state def) connected_to ENT-0039 (state def)
    connect v1 to v2;  // regulates
    connect v2 to v3;  // regulates
    // not rendered as connect() -- ENT-0007 (part def) controls ENT-0031 (state def)
    // not rendered as connect() -- ENT-0007 (part def) controls ENT-0033 (state def)
    // not rendered as connect() -- ENT-0008 (part def) controls ENT-0035 (state def)
    // not rendered as connect() -- ENT-0024 (part def) controls ENT-0031 (state def)
    // not rendered as connect() -- ENT-0026 (part def) controls ENT-0033 (state def)
    // not rendered as connect() -- ENT-0028 (part def) controls ENT-0035 (state def)
    connect t1 to lT_101;  // depends_on
    connect t2 to lT_102;  // depends_on
    connect stop to start;  // depends_on
    connect stop to shut;  // depends_on
    connect stop to start;  // requires
    connect shut to v1;  // controls
    connect shut to v2;  // controls
    connect shut to v3;  // controls
    // not rendered as connect() -- ENT-0043 (state def) responds_to ENT-0040 (part def)
    // not rendered as connect() -- ENT-0043 (state def) responds_to ENT-0041 (part def)
    // not rendered as connect() -- ENT-0043 (state def) responds_to ENT-0042 (part def)
    connect lT_101 to t1;  // connected_to
    connect lT_102 to tank2;  // connected_to
    // not rendered as connect() -- ENT-0043 (state def) controls ENT-0024 (part def)
    // not rendered as connect() -- ENT-0043 (state def) controls ENT-0026 (part def)
    // not rendered as connect() -- ENT-0043 (state def) controls ENT-0028 (part def)
    connect xV_101 to tK_101;  // serves
    connect xV_102 to tK_102;  // serves
    connect xV_103 to tK_101;  // serves
    // not rendered as connect() -- ENT-0044 (requirement def) connected_to ENT-0019 (part def)
    // not rendered as connect() -- ENT-0045 (part def) regulates ENT-0044 (requirement def)
    connect shut to stop;  // controls
    connect shut to v2;  // controls
    connect shut to v3;  // controls
    connect start to shut;  // controls
    connect tankDemo_Rev12 to tankDemo_Rev12;  // contains
    connect vxS_24_spring_return_two_position_liquid_isolation_valve to _24_VDC_actuator;  // composed_of
    connect xV_101 to vxS_24_spring_return_two_position_liquid_isolation_valve;  // part_of
    connect xV_102 to vxS_24_spring_return_two_position_liquid_isolation_valve;  // part_of
    connect xV_103 to vxS_24_spring_return_two_position_liquid_isolation_valve;  // part_of
    connect _24_VDC_actuator to vxS_24_spring_return_two_position_liquid_isolation_valve;  // serves
    connect _24_VDC_actuator to xV_101;  // controls
    connect _24_VDC_actuator to xV_102;  // controls
    connect _24_VDC_actuator to xV_103;  // controls
    connect xV_101 to _24_VDC_actuator;  // depends_on
    connect xV_102 to _24_VDC_actuator;  // depends_on
    connect xV_103 to _24_VDC_actuator;  // depends_on
    connect plC_101 to v1;  // controls
    connect plC_101 to v2;  // controls
    connect plC_101 to v3;  // controls
    connect plC_101 to t1;  // serves
    connect plC_101 to t2;  // serves
    connect v2 to v3;  // mutually_exclusive
    connect controller to valve1;  // controls
    connect controller to valve2;  // controls
    connect controller to valve3;  // controls
    connect tank1 to valve1;  // connected_to
    connect tank1 to valve2;  // connected_to
    connect tank2 to valve2;  // connected_to
    connect tank2 to valve3;  // connected_to
}
