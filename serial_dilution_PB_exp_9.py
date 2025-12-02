
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "Serial Dilutions (PB exp 9)",
    "description": "Serial dilution with parameters from PB experiment 9",
    "author": "Wilson et al"
}

PARAMS = {'asp_rate': 2.0, 'disp_rate': 2.0, 'disp_height': 10.0, 'touch_speed': 10.0, 'mix_reps': 1, 'mix_fraction': 0.1}

def run(protocol: protocol_api.ProtocolContext):

    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1])
    reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)

    p300.flow_rate.aspirate = 80
    p300.flow_rate.dispense = 40
    p300.flow_rate.blow_out = 150

    fluorescein_volume = 200
    pbs_volume         = 100
    dilution_volume    = 100

    res_asp_height    = 1.5
    plate_asp_height  = 1.0
    plate_disp_height = PARAMS["disp_height"]

    asp_rate     = PARAMS["asp_rate"]
    disp_rate    = PARAMS["disp_rate"]
    touch_speed  = PARAMS["touch_speed"]
    mix_reps     = PARAMS["mix_reps"]
    mix_fraction = PARAMS["mix_fraction"]

    base_mix_volume = dilution_volume + pbs_volume  
    mix_volume = base_mix_volume * mix_fraction

    fluorescein_src = reservoir['A1']
    pbs_src         = reservoir['A2']
    waste           = reservoir['A12']

    p300.pick_up_tip()
    p300.aspirate(
        fluorescein_volume,
        fluorescein_src.bottom(res_asp_height),
        rate=asp_rate
    )
    p300.dispense(
        fluorescein_volume,
        plate['A1'].bottom(plate_disp_height),
        rate=disp_rate
    )
    p300.blow_out(plate['A1'].top())
    p300.drop_tip()

    p300.pick_up_tip()
    for col in range(2, 13):
        dest = plate[f'A{col}']
        p300.aspirate(
            pbs_volume,
            pbs_src.bottom(res_asp_height),
            rate=asp_rate
        )
        p300.dispense(
            pbs_volume,
            dest.bottom(plate_disp_height),
            rate=disp_rate
        )
        p300.blow_out(dest.top())
    p300.drop_tip()

    p300.pick_up_tip()
    for col in range(1, 11):
        source = plate[f'A{col}']
        dest   = plate[f'A{col + 1}']

        p300.aspirate(
            dilution_volume,
            source.bottom(plate_asp_height),
            rate=asp_rate
        )

        p300.dispense(
            dilution_volume,
            dest.bottom(plate_disp_height),
            rate=disp_rate
        )

        for i in range(mix_reps):
            p300.aspirate(
                mix_volume,
                dest.bottom(plate_asp_height),
                rate=asp_rate
            )
            p300.dispense(
                mix_volume,
                dest.bottom(plate_disp_height),
                rate=disp_rate
            )

        p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=touch_speed)

    p300.aspirate(100, plate['A11'], rate=asp_rate)
    p300.dispense(150, waste.bottom(), rate=2)
    p300.drop_tip()
