#Available Parameters:
Default_Params = {"Aspiration_Rate": 1.0,               # Global parameter for aspiration rate.
                  "Aliquot_Aspiration_Rate": None,      # Controls aspiration rate of liquid from resevoir.
                  "Dilution_Aspiration_Rate": None,     # Controls aspiration rate of liquid prior to transfer to adjacent wells.
                  "Mix_Aspiration_Rate": None,          # Controls aspiration rate during mixing within one well.
                  
                  "Aspiration_Height": 1.0,             # Global parameter for aspiration height.
                  "Aliquot_Aspiration_Height": None,    # Controls height of aspiration of liquid from resevoir.
                  "Dilution_Aspiration_Height": None,   # Controls height of aspiration of liquid prior to transfer to adjacent wells.
                  "Mix_Aspiration_Height": None,        # Controls height of aspiration during mixing within one well.
                  
                  "Mix_Aspiration_Height_Min": None,    # A range of different apsiration heights can be used during mixing.
                  "Mix_Aspiration_Height_Max": None,    # The height is chosen as a random number within the range defined by these Min and Max values. If no range is desired, leave as None.  

                  "Dispense_Rate": 1.0,                 # Global parameter for dispense rate.
                  "Aliquot_Dispense_Rate": None,        # Controls dispense rate of liquid from resevoir into plate.
                  "Dilution_Dispense_Rate": None,       # Controls dispense rate of liquid when transferring to adjacent wells.
                  "Mix_Dispense_Rate": None,            # Controls dispense rate during mixing within one well.
                  "Final_Mix_Dispense_Rate": None,      # Controls dispense rate during the final mixing step.

                  "Dispense_Height": 1.0,               # Global parameter for dispense height.
                  "Aliquot_Dispense_Height": None,      # Controls height of dispensing of liquid from resevoir into the plates.
                  "Dilution_Dispense_Height": None,     # Controls height of dispensing of liquid into adjacent wells.
                  "Mix_Dispense_Height": None,          # Controls height of dispensing during mixing within one well.
                  
                  "Mix_Dispense_Height_Min": None,      # A range of different dispense heights can be used during mixing.
                  "Mix_Dispense_Height_Max": None,      # The height is chosen as a random number within the range defined by these Min and Max values. If no range is desired, leave as None. 

                  "Mixing_Repetitions": 3,              # Determines the number of repetitions of the mix step between each dilution step.
                  "Mixing_Fraction": 0.7,               # Determines the fraction of the total volume within each well which is pipetted up and down during mixing.

                  "Touch_Tip_Speed": 20,                # These three parameters determine the properties of the touch tip function which removes droplets from pipette tips following mixing and prior to dilution.
                  "Touch_Tip_Radius": 0.8,              
                  "Touch_Tip_V_Offset": -1.0,           # Determines the height of the tip during the touch tips step.
                  }

import csv
from textwrap import dedent

DESIGN_CSV = "/Users/mattgroves/Documents/GitHub/ssb_s5/Main Assesment/Full Factorial.txt"  # Loads the CSV file of the JMP design 

def make_protocol_code(params: dict, experiment_id: str): # Defines the protocol-maker function
    
    params_literal = repr(params) # Converts params dictionary to a string called params_literal

# The following is the template code which is described as Code B in the pseudo code. This is returned by the function with the correct params dictionary.

    return dedent(f""" 
    
    import random
    from opentrons import protocol_api

    metadata = {{
        "apiLevel": "2.15",
        "protocolName": "Serial Dilutions (PB exp {experiment_id})",
        "description": "Serial dilution with parameters from PB experiment {experiment_id}",
        "author": "Wilson et al"
    }}

    PARAMS = {params_literal}

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
        mix_volume = base_mix_volume * mix_fraction

        fluorescein_src = reservoir['A1']
        pbs_src         = reservoir['A6']
        waste           = reservoir['A12']

        fluor_tip_start = f"A{{start_col}}"
        pbs_tip_start   = f"A{{start_col + 1}}"
        dilution_tip_start   = f"A{{start_col + 2}}"

        fluor_tip    = tiprack_1.wells_by_name()[fluor_tip_start]
        pbs_tip      = tiprack_1.wells_by_name()[pbs_tip_start]
        dilution_tip = tiprack_1.wells_by_name()[dilution_tip_start]

        p300.pick_up_tip(fluor_tip)
        p300.aspirate(
            fluorescein_volume,
            fluorescein_src.bottom(aliquot_asp_height),
            rate=aliquot_asp_rate
        )
        p300.dispense(
            fluorescein_volume,
            plate['A1'].bottom(aliquot_disp_height),
            rate=aliquot_disp_rate
        )
        p300.blow_out(plate['A1'].top())
        p300.drop_tip()

        p300.pick_up_tip(pbs_tip)
        for col in range(2, 13):
            dest = plate[f'A{{col}}']
            p300.aspirate(
                pbs_volume,
                pbs_src.bottom(aliquot_asp_height),
                rate=aliquot_asp_rate
            )
            p300.dispense(
                pbs_volume,
                dest.bottom(aliquot_disp_height),
                rate=aliquot_disp_rate
            )
            p300.blow_out(dest.top())
        p300.drop_tip()

        p300.pick_up_tip(dilution_tip)
        for col in range(1, 11):
            source = plate[f'A{{col}}']
            dest   = plate[f'A{{col + 1}}']

            p300.aspirate(
                dilution_volume,
                source.bottom(dilution_asp_height),
                rate=dilution_asp_rate
            )

            p300.dispense(
                dilution_volume,
                dest.bottom(dilution_disp_height),
                rate=dilution_disp_rate
            )

            for i in range(mix_reps):
                
                mix_height = random.uniform(
                mix_asp_height_min,
                mix_asp_height_max
                )
                
                p300.aspirate(
                    mix_volume,
                    dest.bottom(mix_height),
                    rate=mix_asp_rate
                )
                
                mix_height = random.uniform(
                mix_disp_height_min,
                mix_disp_height_max
                )

                p300.dispense(
                    mix_volume,
                    dest.bottom(mix_height),
                    rate=mix_disp_rate
                )

            p300.touch_tip(dest, radius=touch_radius, v_offset=touch_voffset, speed=touch_speed)

        p300.aspirate(100, plate['A11'], rate=dilution_asp_rate)
        p300.dispense(150, waste.bottom(), rate=2)
        p300.drop_tip()
    """)

def main(): #This is the main code-writer function.
    with open(DESIGN_CSV, newline='') as f: # This code opens the JMP table and reads each row as a new dictionary.
        reader = csv.DictReader(f) 

        for idx, row in enumerate(reader, start=1): # This for loop iterates through each row of the table.
            experiment_id = str(idx) # The experiment name is defined by the index of the row.
            block_index = (idx - 1) % 4 
            start_col = 1 + 3 * block_index # the index of the row assigns the start column to start taking tips from.
            
        
            params = Default_Params.copy() # Creates a parameters dictionary as a copy of the default parameters.

            for k in params: # Iterates through parameter names
                if k in reader.fieldnames: # If a parameter is in the table
                    value = row[k].strip()
                    if value == "": # As long as the parameter has a value
                        continue
                    elif isinstance(Default_Params[k], int): # Converts default value to the JMP value and store value in parameters dictionary.
                        params[k] = int(value)
                    elif isinstance(Default_Params[k], float):
                        params[k] = float(value)
                    else:
                        params[k] = str(value)

            params["start_col"] = start_col #Add the tip start column to the end of the parameters dictionary.
            
            #Inheritance rules: set unassigned step-specific parameters to global defualts.
            # Aspiration rates
            
            if params["Aliquot_Aspiration_Rate"] is None:
                params["Aliquot_Aspiration_Rate"] = params["Aspiration_Rate"]

            if params["Dilution_Aspiration_Rate"] is None:
                params["Dilution_Aspiration_Rate"] = params["Aspiration_Rate"]

            if params["Mix_Aspiration_Rate"] is None:
                params["Mix_Aspiration_Rate"] = params["Aspiration_Rate"]


        
            # Aspiration heights
            
            if params["Aliquot_Aspiration_Height"] is None:
                params["Aliquot_Aspiration_Height"] = params["Aspiration_Height"]

            if params["Dilution_Aspiration_Height"] is None:
                params["Dilution_Aspiration_Height"] = params["Aspiration_Height"]

            if params["Mix_Aspiration_Height"] is None:
                params["Mix_Aspiration_Height"] = params["Aspiration_Height"]

            if params["Mix_Aspiration_Height_Min"] is None:
                params["Mix_Aspiration_Height_Min"] = params["Mix_Aspiration_Height"] # Assign min and max heights to standard mix height if range is not specified

            if params["Mix_Aspiration_Height_Max"] is None:
                params["Mix_Aspiration_Height_Max"] = params["Mix_Aspiration_Height"]

            # Dispense rates
            
            if params["Aliquot_Dispense_Rate"] is None:
                params["Aliquot_Dispense_Rate"] = params["Dispense_Rate"]

            if params["Dilution_Dispense_Rate"] is None:
                params["Dilution_Dispense_Rate"] = params["Dispense_Rate"]

            if params["Mix_Dispense_Rate"] is None:
                params["Mix_Dispense_Rate"] = params["Dispense_Rate"]

            if params["Final_Mix_Dispense_Rate"] is None:
                params["Final_Mix_Dispense_Rate"] = params["Mix_Dispense_Rate"] # Final mix dispense rate is the same as the standard mix dispense rate if unspecified.

            # Dispense heights

            if params["Aliquot_Dispense_Height"] is None:
                params["Aliquot_Dispense_Height"] = params["Dispense_Height"]

            if params["Dilution_Dispense_Height"] is None:
                params["Dilution_Dispense_Height"] = params["Dispense_Height"]

            if params["Mix_Dispense_Height"] is None:
                params["Mix_Dispense_Height"] = params["Dispense_Height"]

            if params["Mix_Dispense_Height_Min"] is None:
                params["Mix_Dispense_Height_Min"] = params["Mix_Dispense_Height"] # Assign min and max heights to standard mix height if range is not specified

            if params["Mix_Dispense_Height_Max"] is None:
                params["Mix_Dispense_Height_Max"] = params["Mix_Dispense_Height"]
        
            code = make_protocol_code(params, experiment_id)                      # Protocol code is made using params from a specific JMP row and the corresponding experiment id.
            filename = f"serial_dilution_BB_exp_{experiment_id}.py"
            with open(filename, "w") as out:
                out.write(code)                                                   # The protocol code for the row is written as a separate .py file with the experiment ID in the name.
            print(f"Wrote {filename}")
