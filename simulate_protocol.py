import opentrons.simulate

#protocol_file = open('c:/users/geoff/github/DNA-BOT/dnabot/template_ot2_scripts/simple_protocol_test.py')
protocol_file = open('/Users/wilsonporteus/Documents/GitHub/ssb_s5/main.py')
#protocol_file = open('c:/a_n_other_protocol.py')
opentrons.simulate.simulate(protocol_file) 