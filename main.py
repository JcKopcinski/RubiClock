import time
from hardware_io import Instr
from clock_interface import ClockInterface
from data_analysis import FreqAnalysis


''' ~~~~~~~~~~ SETTINGS ~~~~~~~~~~ '''
clock_settings = {
    "WARMUP_TIME": 10, # time given for the hardware to warmup
    "MOCK_DIR": "./mock_data/",
    "MOCKING_FILE": "./mock_data/mock_run_2023-02-15 14:32:16.415189.csv",
    "MOCKING": False, # if true, use data from mock file to simulate experiment
    "MOCK_RAND": False, # if true, a random file from the mock_data directory will be chosen for data
    "MOCK_SAVE": False, # if true, the live scan will be saved as a mock file
    "ZSWEEP": True, #if true, zaymans sweep is being operated. If false, zayman sweep is not present, commands do not need to be sent to Power supply
}

instr_settings = {
    "ZSWEEP": False, #TODO continue adding to instr settings. This also needs to be passed into every instrument and the class
}

#add instrument settings command, how will setup read commands that are different from eachother | TODO
SPD3303X_setup_commands = { #settings for DC power supply
    'SYS:STAT ': "VOLTAGE", #command likely wrong, FIX | TODO
    'SYS:STAT ': "VOLAGE", #fix, | TODO
    'CH1:VOLT ': 1,
    'CH2:VOLT ': 1,
    'OUTP CH1,': "ON", #turn on both ch1 and ch2
    'OUTP CH2,': "ON"
}

SPD3303X_term_commands = {
    'OUTP CH1': "OFF",
    'OUTP CH2': "OFF"
}

SR830_setup_commands = { #settings for the lockin amplifier
    'SENS': 8, #sets the sensitivity 8 = 1uV/pA
    'ILIN': 3, #sets or queries the input line notch filter status (3 = both notch filters active)
    'RMOD': 1, #sets or queries the reserve mode (1 = Normal)
    'OFLT': 10, #sets or queries the time constant (10 = 1s)
    'ISRC': 0, #sets or queries input configuration (A = 0)
    'ICPL': 0, #sets or queries input oupling (AC = 0)
    'IGND': 0 #sets or queries input shield grounding (Float = 0)
}

SR830_term_commands = {
    
}

SG386_setup_commands = {
    'ENBH': 1, #set the enable state of the rear RF doubler output (1= RF doubler enabled and operating at the programmed amplitude)
    'TYPE': 3, #sets the modulation type (3 = Sweep)
    'SRAT': 10, #sets the modulation rate for sweep type (val = rate in Hz. Here, rate is 10Hz)
    'SFNC': 0, #sets the modulation function for sweeps (0 = sin wave)
    'MODL': 1, # configure modulation before being turned on
    'AMPH': -10 #set the amplitude of the rear RF doubler(units defualt to dBm)
}

SG386_term_commands = {
    'ENBH': 0 #set the enable state of the rear RF doubler (0 = RF doubler disabled)
}


''' <--- initalize devices ---> '''
SPD3303X = Instr(
    resource = 'USB0::0xF4EC::0x1430::SPD3XJEX6R3517::0::INSTR',
    baud_rate = 9600,
    setup_commands = SPD3303X_setup_commands,
    term_commands = SPD3303X_term_commands)

SR830 = Instr( #sets commands in buffers, does not send them to device
    resource = 'GPIB0::8::INSTR', 
    baud_rate = 9600, 
    setup_commands = SR830_setup_commands, 
    term_commands = SR830_term_commands)

SG386 = Instr( #sets the commands in buffers, does not send them to device
    resource = 'GPIB0::27::INSTR', 
    baud_rate = 11500, 
    setup_commands = SG386_setup_commands, 
    term_commands = SG386_term_commands)


''' <--- data analysis ---> '''
freq_base = 6_834_682_610 #base frequency
detune_low = 8000 #min frequency (will subtract from base)
detune_high = 8400 #max frequency (will add to base)


#this performs the setup for the commands set
clock_interface = ClockInterface(
    freq_inst=SG386, #passes the SG386 to ClockInterface | type: Class Instr
    intensity_inst=SR830, #passes the SR830 to ClockInterface | type: Class Instr
    power_supply_inst=SPD3303X, #passes the SPD3303X to ClockInterface | type: Class Instr
    clock_settings = clock_settings #passes the clock settings to ClockInterface | type: dict
)

freq_analysis = FreqAnalysis( #initializes the FreqAnalysis Class, does not perform scan action
    interface=clock_interface, #passes the ClockInterface
    freq_base=freq_base #passes base frequency
)


freq_analysis.single_scan(
    detune_low=detune_low,
    detune_high=detune_high)


''' <--- terminate devices ---> '''
clock_interface.terminate()

