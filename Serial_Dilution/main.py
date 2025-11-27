#from opentrons import simulate
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "Serial Dilutions",
    "description": "This protocol is the outcome of the iGEM Serial Dilution Standard Protocol",
    "author": "Wilson et al"
    }

def run(protocol: protocol_api.ProtocolContext):
        #protocol = simulate.get_protocol_api('2.15')

        plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3)
        tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
        p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks = [tiprack_1])
        reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)

        high = 1.8     
        normal = 1.0  
        slow = 0.5     
        vslow = 0.25   

        p300.flow_rate.aspirate = 80
        p300.flow_rate.dispense = 40
        p300.flow_rate.blow_out = 150

        fluorescein_volume = 200     
        pbs_volume = 100             


        dilution_volume = 100        
        mix_volume = 150             

        res_asp_height = 1.5

        plate_asp_height = 1.0
        plate_disp_height = 1.0

        mix_low_height = 0.8
        mix_mid_height = 1.5
        mix_high_height = 2.5


        fluorescein_src = reservoir['A1']   
        pbs_src = reservoir['A2']           
        waste = reservoir['A12']   
                


        #rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        #Fluorescein
        p300.pick_up_tip()
        p300.aspirate(fluorescein_volume, fluorescein_src.bottom(res_asp_height), rate=slow)
        p300.dispense(fluorescein_volume, plate['A1'], rate=slow)
        p300.blow_out(plate['A1'].top())
        p300.drop_tip()
        #PBS Alloquot

        p300.pick_up_tip()
        for col in range(2,13):  
                #top_row=plate.rows()[0]
                dest = plate[f'A{col}']

               

                p300.aspirate(
                pbs_volume,
                pbs_src.bottom(res_asp_height),
                rate=slow
                )

                p300.dispense(
                pbs_volume,
                dest.bottom(plate_disp_height),
                rate=normal
                )

                p300.blow_out(dest.top())
        p300.drop_tip()



       

        #Dilutions
        p300.pick_up_tip()
        for col in range(1,11):
                
                source = plate[f'A{col}']       
                dest = plate[f'A{col + 1}']     


                p300.aspirate(
                        dilution_volume,
                        source.bottom(plate_asp_height),
                        rate= p300.flow_rate.aspirate
                )


                p300.dispense(
                        dilution_volume,
                        dest.bottom(plate_disp_height),
                        rate=p300.flow_rate.dispense,
                        
                )

                p300.aspirate(mix_volume,dest.bottom(mix_low_height),rate=normal)
                p300.dispense(mix_volume,dest.bottom(mix_low_height),rate=high)
                p300.aspirate(mix_volume,dest.bottom(mix_low_height),rate=high)
                p300.dispense(mix_volume,dest.bottom(mix_low_height),rate=high)
                p300.aspirate(mix_volume,dest.bottom(mix_low_height),rate=high)
                p300.dispense(mix_volume,dest.bottom(mix_low_height),rate=slow)
                p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=20)
        p300.aspirate(
                100, 
                plate['A11'],
                rate=slow
                )
        p300.dispense(
                150,
                waste.bottom(),
                rate=high
        )
        p300.drop_tip()
        for line in protocol.commands():
                print(line)
