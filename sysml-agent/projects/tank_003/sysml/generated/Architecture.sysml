package Architecture {
    part def TK_101;
    part def TK_102;
    part def XV_101;
    part def XV_102;
    part def XV_103;
    part def PLC_101_SequenceController;
    part def LT_101_LevelMeasurement;
    part def LT_102_LevelMeasurement;
    part def PLC_101_Controller;
    part def XV_101_OnOffValve;
    part def XV_102_OnOffValve;
    part def XV_103_OnOffValve;
    part def LT_101_LevelTransmitter;
    part def LT_102_LevelTransmitter;
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
    part def tankController;
    part def start;
    part def stop;
    part def shut;
    part def ambient1;
    part def level1;
    part def level2;
    part def valve3;
    part def SRC;
    part def V1;
    part def T1;
    part def V2;
    part def T2;
    part def V3;
    part def DRN;
    part def Two_Tank_Fill_Transfer_Drain_Controller;
    part def LT_101_LevelSensor;
    part def LT_102_LevelSensor;
    part def Two_Tank_Controller;
    part def STOP_Command;
    part def START_Command;
    part def SHUT_Command;
    part def Drain_valve;
    part def START_ControllerCommand;
    part def TankDemo_Rev12;
    part def startCmd;
    part def stopCmd;
    part def VXS_24_OnOffValve;
    part def controller;
    part tK_101 : TK_101;
    part tK_102 : TK_102;
    part xV_101 : XV_101;
    part xV_102 : XV_102;
    part xV_103 : XV_103;
    part plC_101_SequenceController : PLC_101_SequenceController;
    part lT_101_LevelMeasurement : LT_101_LevelMeasurement;
    part lT_102_LevelMeasurement : LT_102_LevelMeasurement;
    part plC_101_Controller : PLC_101_Controller;
    part xV_101_OnOffValve : XV_101_OnOffValve;
    part xV_102_OnOffValve : XV_102_OnOffValve;
    part xV_103_OnOffValve : XV_103_OnOffValve;
    part lT_101_LevelTransmitter : LT_101_LevelTransmitter;
    part lT_102_LevelTransmitter : LT_102_LevelTransmitter;
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
    part tankController : tankController;
    part start : start;
    part stop : stop;
    part shut : shut;
    part ambient1 : ambient1;
    part level1 : level1;
    part level2 : level2;
    part valve3 : valve3;
    part src : SRC;
    part v1 : V1;
    part t1 : T1;
    part v2 : V2;
    part t2 : T2;
    part v3 : V3;
    part drn : DRN;
    part two_Tank_Fill_Transfer_Drain_Controller : Two_Tank_Fill_Transfer_Drain_Controller;
    part lT_101_LevelSensor : LT_101_LevelSensor;
    part lT_102_LevelSensor : LT_102_LevelSensor;
    part two_Tank_Controller : Two_Tank_Controller;
    part stoP_Command : STOP_Command;
    part starT_Command : START_Command;
    part shuT_Command : SHUT_Command;
    part drain_valve : Drain_valve;
    part starT_ControllerCommand : START_ControllerCommand;
    part tankDemo_Rev12 : TankDemo_Rev12;
    part startCmd : startCmd;
    part stopCmd : stopCmd;
    part vxS_24_OnOffValve : VXS_24_OnOffValve;
    part controller : controller;
    connect plC_101_SequenceController to lT_101_LevelMeasurement;  // depends_on
    connect plC_101_SequenceController to lT_102_LevelMeasurement;  // depends_on
    connect xV_101 to tK_101;  // serves
    connect xV_102 to tK_101;  // serves
    connect xV_102 to tK_102;  // serves
    connect xV_103 to tK_102;  // serves
    connect plC_101_SequenceController to xV_101;  // controls
    connect plC_101_SequenceController to xV_102;  // controls
    connect plC_101_SequenceController to xV_103;  // controls
    connect lT_101_LevelMeasurement to tK_101;  // serves
    connect lT_102_LevelMeasurement to tK_102;  // serves
    connect plC_101_Controller to pB_START;  // depends_on
    connect plC_101_Controller to pB_STOP;  // depends_on
    connect plC_101_Controller to pB_SHUT;  // depends_on
    connect plC_101_Controller to lT_101_LevelTransmitter;  // depends_on
    connect plC_101_Controller to lT_102_LevelTransmitter;  // depends_on
    connect plC_101_Controller to xV_101_OnOffValve;  // controls
    connect plC_101_Controller to xV_102_OnOffValve;  // controls
    connect plC_101_Controller to xV_103_OnOffValve;  // controls
    connect tK_101 to lT_101_LevelTransmitter;  // connected_to
    connect tK_102 to lT_102_LevelTransmitter;  // connected_to
    connect xV_101_OnOffValve to srC_101;  // connected_to
    connect xV_101_OnOffValve to tK_101;  // connected_to
    connect tK_101 to xV_102_OnOffValve;  // connected_to
    connect xV_102_OnOffValve to tK_102;  // connected_to
    connect tK_102 to xV_103_OnOffValve;  // connected_to
    connect xV_103_OnOffValve to drN_101;  // connected_to
    connect pB_START to plC_101_Controller;  // signal_flow
    connect pB_STOP to plC_101_Controller;  // signal_flow
    connect pB_SHUT to plC_101_Controller;  // signal_flow
    connect lT_101_LevelTransmitter to plC_101_Controller;  // signal_flow
    connect lT_102_LevelTransmitter to plC_101_Controller;  // signal_flow
    connect plC_101_Controller to xV_101_OnOffValve;  // signal_flow
    connect plC_101_Controller to xV_102_OnOffValve;  // signal_flow
    connect plC_101_Controller to xV_103_OnOffValve;  // signal_flow
    connect pB_START to pB_STOP;  // controls
    connect pB_START to pB_SHUT;  // controls
    connect pB_STOP to pB_SHUT;  // controls
    connect lT_101_LevelTransmitter to tK_101;  // connected_to
    connect lT_102_LevelTransmitter to tK_102;  // connected_to
    connect source to valve1;  // connected_to
    connect valve1 to tank1;  // connected_to
    connect tank1 to valve2;  // connected_to
    connect valve2 to tank2;  // connected_to
    connect tankController to valve1;  // controls
    connect tankController to valve2;  // controls
    connect tankController to valve3;  // controls
    connect start to tankController;  // connected_to
    connect stop to tankController;  // connected_to
    connect shut to tankController;  // connected_to
    connect tank1 to tankController;  // connected_to
    connect tank2 to tankController;  // connected_to
    connect ambient1 to valve3;  // connected_to
    connect valve3 to tank2;  // connected_to
    connect src to v1;  // connected_to
    connect v1 to t1;  // connected_to
    connect t1 to v2;  // connected_to
    connect v2 to t2;  // connected_to
    connect t2 to v3;  // connected_to
    connect v3 to drn;  // connected_to
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0045 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0046 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0047 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0048 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0049 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0050 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0051 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0044 (state def)
    // not rendered as connect() -- ENT-0040 (part def) contains ENT-0043 (state def)
    connect v1 to v2;  // connected_to
    connect v2 to v3;  // connected_to
    connect lT_101_LevelSensor to t1;  // connected_to
    connect lT_102_LevelSensor to t2;  // connected_to
    // not rendered as connect() -- ENT-0046 (state def) controls ENT-0034 (part def)
    // not rendered as connect() -- ENT-0048 (state def) controls ENT-0036 (part def)
    // not rendered as connect() -- ENT-0050 (state def) controls ENT-0038 (part def)
    // not rendered as connect() -- ENT-0044 (state def) controls ENT-0034 (part def)
    // not rendered as connect() -- ENT-0044 (state def) controls ENT-0036 (part def)
    // not rendered as connect() -- ENT-0044 (state def) controls ENT-0038 (part def)
    // not rendered as connect() -- ENT-0043 (state def) controls ENT-0036 (part def)
    // not rendered as connect() -- ENT-0043 (state def) controls ENT-0038 (part def)
    // not rendered as connect() -- ENT-0047 (state def) triggers ENT-0048 (state def)
    // not rendered as connect() -- ENT-0049 (state def) triggers ENT-0050 (state def)
    // not rendered as connect() -- ENT-0051 (state def) triggers ENT-0046 (state def)
    // not rendered as connect() -- ENT-0045 (state def) triggers ENT-0046 (state def)
    // not rendered as connect() -- ENT-0044 (state def) triggers ENT-0045 (state def)
    // not rendered as connect() -- ENT-0043 (state def) triggers ENT-0045 (state def)
    connect lT_101_LevelSensor to t1;  // responds_to
    connect lT_102_LevelSensor to t2;  // responds_to
    // not rendered as connect() -- ENT-0046 (state def) depends_on ENT-0041 (part def)
    // not rendered as connect() -- ENT-0048 (state def) depends_on ENT-0041 (part def)
    // not rendered as connect() -- ENT-0050 (state def) depends_on ENT-0042 (part def)
    // not rendered as connect() -- ENT-0047 (state def) depends_on ENT-0048 (state def)
    // not rendered as connect() -- ENT-0049 (state def) depends_on ENT-0050 (state def)
    // not rendered as connect() -- ENT-0051 (state def) depends_on ENT-0046 (state def)
    connect two_Tank_Controller to stoP_Command;  // controls
    connect two_Tank_Controller to starT_Command;  // controls
    connect two_Tank_Controller to shuT_Command;  // controls
    connect two_Tank_Controller to v1;  // controls
    connect two_Tank_Controller to v2;  // controls
    connect two_Tank_Controller to v3;  // controls
    connect two_Tank_Controller to lT_101_LevelSensor;  // controls
    connect two_Tank_Controller to lT_102_LevelSensor;  // controls
    connect v1 to tank1;  // connected_to
    connect v2 to tank1;  // connected_to
    connect v3 to tank2;  // connected_to
    connect lT_101_LevelSensor to tank1;  // connected_to
    connect lT_102_LevelSensor to tank2;  // connected_to
    connect two_Tank_Controller to tank1;  // controls
    connect two_Tank_Controller to tank2;  // controls
    connect xV_101 to tK_101;  // serves
    connect xV_102 to tK_102;  // serves
    connect xV_103 to tK_101;  // serves
    connect xV_103 to tK_102;  // serves
    // not rendered as connect() -- ENT-0056 (constraint def) controls ENT-0057 (part def)
    // not rendered as connect() -- ENT-0058 (constraint def) controls ENT-0036 (part def)
    // not rendered as connect() -- ENT-0058 (constraint def) controls ENT-0038 (part def)
    // not rendered as connect() -- ENT-0059 (state def) depends_on ENT-0060 (state def)
    // not rendered as connect() -- ENT-0059 (state def) controls ENT-0036 (part def)
    // not rendered as connect() -- ENT-0059 (state def) controls ENT-0038 (part def)
    // not rendered as connect() -- ENT-0061 (part def) regulates ENT-0059 (state def)
    connect tankDemo_Rev12 to valve1;  // contains
    connect tankDemo_Rev12 to valve2;  // contains
    connect tankDemo_Rev12 to valve3;  // contains
    // not rendered as connect() -- ENT-0062 (part def) contains ENT-0063 (state def)
    // not rendered as connect() -- ENT-0062 (part def) contains ENT-0063 (state def)
    connect tankDemo_Rev12 to startCmd;  // contains
    connect tankDemo_Rev12 to stopCmd;  // contains
    connect startCmd to valve1;  // controls
    connect stopCmd to valve1;  // controls
    connect startCmd to valve2;  // controls
    connect stopCmd to valve2;  // controls
    connect startCmd to valve3;  // controls
    connect stopCmd to valve3;  // controls
    // not rendered as connect() -- ENT-0021 (part def) controls ENT-0063 (state def)
    // not rendered as connect() -- ENT-0023 (part def) controls ENT-0063 (state def)
    // not rendered as connect() -- ENT-0023 (part def) controls ENT-0063 (state def)
    // not rendered as connect() -- ENT-0032 (part def) controls ENT-0063 (state def)
    connect vxS_24_OnOffValve to xV_101;  // serves
    connect vxS_24_OnOffValve to xV_102;  // serves
    connect vxS_24_OnOffValve to xV_103;  // serves
    connect xV_101 to vxS_24_OnOffValve;  // depends_on
    connect xV_102 to vxS_24_OnOffValve;  // depends_on
    connect xV_103 to vxS_24_OnOffValve;  // depends_on
    connect xV_101 to xV_102;  // connected_to
    connect xV_101 to xV_103;  // connected_to
    connect xV_102 to xV_103;  // connected_to
    connect plC_101_Controller to v1;  // controls
    connect plC_101_Controller to v2;  // controls
    connect plC_101_Controller to v3;  // controls
    connect v1 to t1;  // supplies
    connect v2 to t1;  // connected_to
    connect v2 to t2;  // supplies
    connect v3 to t2;  // connected_to
    connect controller to valve1;  // controls
    connect controller to valve2;  // controls
    connect controller to valve3;  // controls
    connect valve1 to tank1;  // serves
    connect valve2 to tank2;  // serves
    connect valve3 to tank1;  // serves
    connect tank1 to tank2;  // connected_to
}
