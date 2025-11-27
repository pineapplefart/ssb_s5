from opentrons import simulate
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "Serial Dilutions",
    "description": "This protocol is the outcome of the iGEM Serial Dilution Standard Protocol",
    "author": "Robin Blackwell et al"
    }

def run(protocol: protocol_api.ProtocolContext):
    protocol = simulate.get_protocol_api('2.15')

    # 96-well flat-bottom plate in deck slot 1
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)

    # 300 µL tip rack in deck slot 2
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

    # 12-channel reservoir (for fluorescein + PBS + optional waste) in slot 3
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 3)

    # Single-channel P300 GEN2 on the right
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1])

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


        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        #Fluorescein
        p300.pick_up_tip()
        p300.aspirate(fluorescein_volume, fluorescein_src(res_asp_height), rate=slow)
        p300.dispense(fluorescein_volume, plate['A1'], rate=slow, blow_out=True)
        
        #PBS Alloquot
        for col in range(2, 13):  

                dest = plate[f'{col}1']

                p300.pick_up_tip()

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



        start_column = 1
        last_source_column = 10  

        #Dilutions
        for col in range(start_column, last_source_column + 1):
                p300.pick_up_tip()
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
                        push_out=1
                )
                p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=20)
                p300.drop_tip()
        for line in protocol.commands():
                print(line)
