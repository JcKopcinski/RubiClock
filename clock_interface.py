import time
from tqdm import tqdm
import file_io

class ClockInterface:
    def __init__(self, freq_inst, intensity_inst, power_supply_inst, clock_settings):
        self.freq_inst = freq_inst #frequency modulator (inst->instrument)
        self.intensity_inst = intensity_inst #lock in amplifier
        self.power_supply_inst = power_supply_inst #power supply

        self.is_mocking = clock_settings["MOCKING"] #defines if we are using a mock data set | type: bool
        self.is_mock_save = clock_settings["MOCK_SAVE"] #defines if live data will be used as a mock save | type: bool
        self.is_mock_rand = clock_settings["MOCK_RAND"] #defines if we are going to use a random mock file | type: bool
        self.mock_filepath = clock_settings["MOCKING_FILE"] #defines the filename/path of them mock data | type: str
        self.mock_dir = clock_settings["MOCK_DIR"] #defines the directory for all mock data sets | type: str
        self.warmup_time = clock_settings["WARMUP_TIME"]  #defines the hardware warmup time | type: int
        self.zsweep = clock_settings["ZSWEEP"] #defines the operation (or not) of a zayman sweep
        self.setup() #set up the instruments
    
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """

    # setup instruments, if needed
    def setup(self):
        if not self.is_mocking: #live data set
            self.freq_inst.setup_config() #calls setup_config in Class Instr (set up commands sent to modulator here)
            self.intensity_inst.setup_config() #calls setup_config on lock in amplifier
            self.power_supply_inst.setup_config() #calls setup_config on power supply
            time.sleep(self.warmup_time) #sleeps for the warmup duration to buffer for commands

    # terminate instruments, if needed
    def terminate(self):
        if not self.is_mocking: #live data set
            self.freq_inst.term_config() #send termination commands to modulator
            self.intensity_inst.term_config() #send termination commands to lock in amplifier
            self.power_supply_inst.term_config() #send termination commands to power supply

    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """

    # wrapper for getting data (mocking or live)
    def get_data(self, freq_base, freq_low, freq_high):
        if self.is_mocking: #we are using a preset mock file
            if self.is_mock_rand: #if we are selecting a random mock file:
                file = self.mock_dir + file_io.get_random_file(self.mock_dir)
                return self.get_mocking_data(file, freq_base, freq_low, freq_high)
            return self.get_mocking_data(self.mock_filepath, freq_base, freq_low, freq_high)
        
        x_data, y_data = self.get_live_data(freq_base, freq_low, freq_high) #obtains the live data and saves into x and y lists
        if self.is_mock_save: #if we are saving the live run as a mock data set, save here
            file_io.save_data_csv(dir=self.mock_dir, x_data=x_data, y_data=y_data)
        return x_data, y_data #return the live data lists


    # use sample data saved locally
    def get_mocking_data(self, file, freq_base, freq_low, freq_high):
        x_data, y_data = file_io.read_data_csv(file) #reads csv data
        low = x_data.index(freq_low - freq_base) 
        high = x_data.index(freq_high - freq_base)
        return x_data[low:high], y_data[low:high]


    # use clock hardware to get data
    def get_live_data(self, freq_base, freq_low, freq_high):
        freq_data = []
        intensity_data = []
    
        for f in tqdm(range(freq_low, freq_high, 1), desc="scanning clock..."): #tqdm provides a progress bar
            self.freq_inst.write('FREQ', f) #save freq value into f
            measured_intensity = self.intensity_inst.query('OUTP?3') #save intensity value into measure intensity
            freq_data.append(f - freq_base) #append f - freq_base
            intensity_data.append(float(measured_intensity)) #append measure intensity data

        return freq_data, intensity_data #return the live data lists

    #currently unused
    def get_live_data_at(self, freq):
        self.freq_inst.write('FREQ', freq)
        measured_intensity = self.intensity_inst.query('OUTP?3')
        return float(measured_intensity)