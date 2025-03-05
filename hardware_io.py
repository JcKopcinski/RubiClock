import pyvisa
import time
import sys
import re

class Instr:
    def __init__(self, resource, baud_rate, setup_commands, term_commands, instr_command_settings, timeout=1000) -> None:
        self.name = resource #sets the name of the resource, ie port
        self.setup_commands = setup_commands #sets the setup commands
        self.term_commands = term_commands #sets the termination commands
        self.query_mode = instr_command_settings["QUERY_MODE"] #sets the instrument settings

        try: #open the resource/device in pyVISA
            rm = pyvisa.ResourceManager() 
            self.instr = rm.open_resource(resource)
            self.instr.baud_rate = baud_rate #set the instrument baud rate
            self.instr.timeout = timeout #set the instrument timeout value. this is the number of ms pyvisa
                                         #will wait before generating an exception
        except Exception: #resource failed to connect
            self.instr = None
            print(self.name + " cannot be initalized.")

    def setup_config(self): #write the setup commands to the device
        if self.instr is None:
            print(self.name + " cannot be setup. Exiting Program", file=sys.stderr)

        for command, value in self.setup_commands.items(): #enumerate each command and the value associated with it
            self.write_and_verify(command, value) #write command to the device

    def term_config(self): #write the terminal/termination commands to the device
        if self.instr is not None:
            for command, value in self.term_commands.items(): #enumerate each command and the value associated with it
                self.write_and_verify(command, value) #write command to the device


    # returns value read from hardware //unused in main
    def query(self, command):
        if self.instr is None:
            print("instrument is not defined or cannot extablish communication")
            return
        
        if type(command) is not str:
            print("command must be of type string")
            return

        return self.instr.query(command)

    # prints and returns value read from hardware //unused in main
    def query_and_print(self, command):
        response = self.query(command)
        print(response)
        return response

    # writes to hardware
    def write(self, command, value): #TODO need to account for ZSWEEP
        self.instr.write(command + str(value)) #writes the string representtion of the command

    # writes to hardware and checks if hardware agrees
    def write_and_verify(self, command, value): #TODO need to account for ZSWEEP
        self.write(command, value)

        if self.query_mode == 1:
            print(f"Command '{command}'")
            if "OUTP" in command:

                response = self.instr.query("SYST:STAT?")
                print(self.name, "response ->", command, ": ", response)
                return response
            else:
                response = self.instr.query(command.strip() + "?") #get response. The ? appended to the command tells the device we are trying to query, not write
                print(self.name, "response ->", command, ": ", response) 
                return response

        response = self.instr.query(command + "?") #get response. The ? appended to the command tells the device we are trying to query, not write
        print(self.name, "response ->", command, ": ", response) 
        return response