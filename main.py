from opentrons import simulate
metadata = {'apiLevel': '2.19'}
protocol = simulate.get_protocol_api('2.19')

#Labware
plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

#pipettes
p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1])
#lines below set flow rates, without this would run at default speed
p300.flow_rate.aspirate = 80
p300.flow_rate.dispense = 40
p300.flow_rate.blow_out = 150

#complex commands
p300.transfer(100, plate['A1'], plate['B1'], mix_before=(2,50), touch_tip=True, blow_out=True, blowout_location='destination well', new_tip='always') 

#block commands
p300.pick_up_tip()
p300.aspirate(100, plate['A2'])
p300.dispense(100, plate['B2'])
#mix(repetitions, volume, location, rate)
p300.mix(3, 50, plate['B2'], 0.5)
p300.blow_out(plate['B2'].bottom(10))
p300.return_tip()
#print out commands so we can check the simulation
for line in protocol.commands(): 
        print(line)
#wuddup fam
#wuddup
