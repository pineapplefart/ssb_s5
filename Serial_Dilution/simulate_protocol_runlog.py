import opentrons.simulate
from opentrons.simulate import format_runlog 


# read the file 

protocol_file = open('/Users/wilsonporteus/Documents/GitHub/ssb_s5/Serial_Dilution/main.py') 

# simulate() the protocol, keeping the runlog 
#opentrons.simulate.simulate(protocol_file) 

runlog, _bundle = opentrons.simulate.simulate(protocol_file) 

# print the runlog 

print(format_runlog(runlog)) 