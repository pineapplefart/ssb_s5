

import random
from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "Serial Dilutions (PB exp 1)",
    "description": "Serial dilution with parameters from PB experiment 1",
    "author": "Wilson et al"
}

# Below are the relevant parameters from the JMP table inputted by Code A.
PARAMS = {'Aspiration_Rate': 1.0, 'Aliquot_Aspiration_Rate': 1.0, 'Dilution_Aspiration_Rate': 1.0, 'Mix_Aspiration_Rate': 1.0, 'Aspiration_Height': 1.0, 'Aliquot_Aspiration_Height': 1.0, 'Dilution_Aspiration_Height': 1.0, 'Mix_Aspiration_Height': 1.0, 'Mix_Aspiration_Height_Min': 1.0, 'Mix_Aspiration_Height_Max': 1.0, 'Dispense_Rate': 1.0, 'Aliquot_Dispense_Rate': 1.0, 'Dilution_Dispense_Rate': 1.0, 'Mix_Dispense_Rate': 1.0, 'Final_Mix_Dispense_Rate': 1.0, 'Dispense_Height': 1.0, 'Aliquot_Dispense_Height': 1.0, 'Dilution_Dispense_Height': 1.0, 'Mix_Dispense_Height': 1.0, 'Mix_Dispense_Height_Min': 1.0, 'Mix_Dispense_Height_Max': 1.0, 'Mixing_Repetitions': 3, 'Mixing_Fraction': 1.0, 'Touch_Tip_Speed': 20, 'Touch_Tip_Radius': 0.8, 'Touch_Tip_V_Offset': -1.0, 'start_col': 1}

def run(protocol: protocol_api.ProtocolContext):

    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3) #Loads the labware and instrument
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1])
    reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)

    p300.flow_rate.aspirate = 80 
    p300.flow_rate.dispense = 40
    p300.flow_rate.blow_out = 150

    fluorescein_volume = 200 # Defines the constant aliquotting and dilution volumes
    pbs_volume         = 100
    dilution_volume    = 100

    # Reads all the parameters as constant variable names.
    aliquot_asp_rate   = PARAMS["Aliquot_Aspiration_Rate"] 
    dilution_asp_rate  = PARAMS["Dilution_Aspiration_Rate"]
    mix_asp_rate       = PARAMS["Mix_Aspiration_Rate"]

    aliquot_asp_height  = PARAMS["Aliquot_Aspiration_Height"]
    dilution_asp_height = PARAMS["Dilution_Aspiration_Height"]
    mix_asp_height_min  = PARAMS["Mix_Aspiration_Height_Min"]
    mix_asp_height_max  = PARAMS["Mix_Aspiration_Height_Max"]

    aliquot_disp_rate   = PARAMS["Aliquot_Dispense_Rate"]
    dilution_disp_rate  = PARAMS["Dilution_Dispense_Rate"]
    mix_disp_rate       = PARAMS["Mix_Dispense_Rate"]
    final_mix_disp_rate = PARAMS["Final_Mix_Dispense_Rate"]

    aliquot_disp_height  = PARAMS["Aliquot_Dispense_Height"]
    dilution_disp_height = PARAMS["Dilution_Dispense_Height"]
    mix_disp_height      = PARAMS["Mix_Dispense_Height"]
    mix_disp_height_min  = PARAMS["Mix_Dispense_Height_Min"]
    mix_disp_height_max  = PARAMS["Mix_Dispense_Height_Max"]

    mix_reps     = PARAMS["Mixing_Repetitions"]
    mix_fraction = PARAMS["Mixing_Fraction"]

    touch_speed   = PARAMS["Touch_Tip_Speed"]
    touch_radius  = PARAMS["Touch_Tip_Radius"]
    touch_voffset = PARAMS["Touch_Tip_V_Offset"]

    start_col = int(PARAMS["start_col"])

    base_mix_volume = dilution_volume + pbs_volume  
    mix_volume = base_mix_volume * mix_fraction # Computes the mix volume from the Mix_Fraction parameter.

    # Assigns resevoir wells to relevant pipetting steps.
    fluorescein_src = reservoir['A1'] 
    pbs_src         = reservoir['A6']
    waste           = reservoir['A12']

    # Ensures each step selects next available tips based on the start_col parameter.
    fluor_tip_start = f"A{start_col}" 
    pbs_tip_start   = f"A{start_col + 1}"
    dilution_tip_start   = f"A{start_col + 2}"
    fluor_tip    = tiprack_1.wells_by_name()[fluor_tip_start]
    pbs_tip      = tiprack_1.wells_by_name()[pbs_tip_start]
    dilution_tip = tiprack_1.wells_by_name()[dilution_tip_start]

    p300.pick_up_tip(fluor_tip) # Picks up tips for fluorescein aliquotting.
    p300.aspirate( 
        fluorescein_volume,
        fluorescein_src.bottom(aliquot_asp_height),
        rate=aliquot_asp_rate
    ) # Aspirates from fluorescein resevoir according to aliquot aspiration parameters.
    p300.dispense(
        fluorescein_volume,
        plate['A1'].bottom(aliquot_disp_height),
        rate=aliquot_disp_rate
    ) # Dispenses into plate column 1 according to aliquot dispense parameters.
    p300.blow_out(plate['A1'].top())
    p300.drop_tip()

    p300.pick_up_tip(pbs_tip) # Picks up tips for PBS aliquotting.
    for col in range(2, 13): # For columns 2-12 of the plate:
        dest = plate[f'A{col}']
        p300.aspirate(
            pbs_volume,
            pbs_src.bottom(aliquot_asp_height),
            rate=aliquot_asp_rate
        ) # Aspirates from PBS resevoir according to aliquot aspiration parameters.
        p300.dispense(
            pbs_volume,
            dest.bottom(aliquot_disp_height),
            rate=aliquot_disp_rate
        ) # Dispenses into plate columns according to aliquot dispense parameters.
        p300.blow_out(dest.top())
    p300.drop_tip()

    p300.pick_up_tip(dilution_tip) # Picks up tips for dilution and mixing.
    for col in range(1, 11): # For plate columns starting with 1 and ending at 10:
        source = plate[f'A{col}']
        dest   = plate[f'A{col + 1}']

        p300.aspirate(
            dilution_volume,
            source.bottom(dilution_asp_height),
            rate=dilution_asp_rate
        ) # Aspirate the dilution volume from one column according to dilution aspiration parameters.

        p300.dispense(
            dilution_volume,
            dest.bottom(dilution_disp_height),
            rate=dilution_disp_rate
        ) # Dispense into the next column according to dispense parameters.

        for i in range(mix_reps): # For a specified number of mixing repetitions:

            mix_height = random.uniform(
            mix_asp_height_min,
            mix_asp_height_max
            ) # Generates random apsiration height (constant if range not specified)

            p300.aspirate(
                mix_volume,
                dest.bottom(mix_height),
                rate=mix_asp_rate
            ) # Aspirates at that height according to parameters

            mix_height = random.uniform(
            mix_disp_height_min,
            mix_disp_height_max
            ) # Generates random dispense height (constant if range not specified)

            p300.dispense(
                mix_volume,
                dest.bottom(mix_height),
                rate=mix_disp_rate
            ) # Dispenses at that height according to parameters

        p300.touch_tip(dest, radius=touch_radius, v_offset=touch_voffset, speed=touch_speed) # Touches tips using specified speed, radius, offset

    p300.aspirate(100, plate['A11'], rate=dilution_asp_rate) # aspirates dilution volume from second-to-last column
    p300.dispense(150, waste.bottom(), rate=2) # Dispenses into waste
    p300.drop_tip() 
