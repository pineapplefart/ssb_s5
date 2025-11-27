from opentrons import simulate
from opentrons import protocol_api
metadata = {
     'apiLevel': '2.19',
     'protocolName': 'Simple code test',
     'description': 'use to evaluate simple pipetting and coding commands'
}
def run(protocol: protocol_api.ProtocolContext):
    #Labware
    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 1)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

    #pipettes
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1])

    #Resevoir
    reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 3)



    # -----------------------
    # Global parameters
    # -----------------------

    # Volumes (in µL)
    dilution_volume = 100       # volume transferred each step of the dilution
    mix_volume = 150            # volume used for mixing in each destination well
    mix_reps = 3                # how many times to mix at each step

    # Heights (in mm from the bottom of the well)
    aspirate_height = 1.0       # aspirate slightly above bottom to avoid scraping
    dispense_height = 1.0       # dispense just above bottom to reduce splashing
    mix_height = 1.0            # mixing position inside the well

    # Speed modifiers (multipliers of base flow rates)
    aspirate_rate = 0.5         # slower aspiration helps avoid bubbles
    dispense_rate = 0.5         # slower dispense reduces splashing
    mix_rate = 0.7              # slightly slower mixing for gentle agitation

    # Base flow rates (µL/s) – these can be tuned as well
    p300.flow_rate.aspirate = 80
    p300.flow_rate.dispense = 40
    p300.flow_rate.blow_out = 150

    #speeds discussed in class
    high=1.8
    normal=1.0
    slow=0.5
    vslow=0.25

    #heigh parameters
    bottom = 1
    a = 0.5
    middle = bottom + a
    top = bottom + 2*a

    # Columns for the serial dilution
    # We dilute from column 1 -> 2 -> 3 ... -> 11
    # Column 12 remains PBS only (blank control)
    start_column = 1
    last_source_column = 10  # 1→2, 2→3, ..., 10→11

    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # -----------------------
    # Volumes (µL)
    # -----------------------

    # Prefill stage
    fluorescein_volume = 200     # col 1
    pbs_volume = 100             # cols 2–12

    # Serial dilution stage
    dilution_volume = 100        # transfer volume col n -> col n+1
    mix_volume = 150             # volume used in each mix cycle

    #Alliquots
    for row in rows:
        dest = plate[f'{row}1']  # A1, B1, ..., H1

        p300.pick_up_tip()

        # Aspirate fluorescein from reservoir at slow speed to avoid bubbles
        p300.aspirate(
            fluorescein_volume,
            fluorescein_src.bottom(res_asp_height),
            rate=slow
        )

        # Dispense into plate well at normal speed
        p300.dispense(
            fluorescein_volume,
            dest.bottom(plate_disp_height),
            rate=normal
        )

        # Blow out at top of well to clear residual liquid
        p300.blow_out(dest.top())

        p300.drop_tip()

# --- Fill columns 2–12 with PBS ---
    for col in range(2, 13):  # 2..12
        for row in rows:
            dest = plate[f'{row}{col}']

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

            p300.drop_tip()`


    #Dilutions
    for col in range(start_column, last_source_column + 1):
        p300.pick_up_tip()
        source = plate[f'A{col}']       # e.g. A1, A2, ...
        dest = plate[f'A{col + 1}']     # e.g. A2, A3, ...

        # Aspirate from source at a defined height and rate
        p300.aspirate(
            dilution_volume,
            source.bottom(aspirate_height),
            rate=aspirate_rate
        )

        # Dispense into destination at a defined height and rate
        p300.dispense(
            dilution_volume,
            dest.bottom(dispense_height),
            rate=dispense_rate,
            push_out=1
        )
        p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=20)
        p300.drop_tip()
    for line in protocol.commands():
        print(line)
