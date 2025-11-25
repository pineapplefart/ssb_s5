from opentrons import simulate

metadata = {'apiLevel': '2.19'}
protocol = simulate.get_protocol_api('2.19')

# -----------------------
# Labware and pipette
# -----------------------
plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1])

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

# Columns for the serial dilution
# We dilute from column 1 -> 2 -> 3 ... -> 11
# Column 12 remains PBS only (blank control)
start_column = 1
last_source_column = 10  # 1→2, 2→3, ..., 10→11

rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# --------------------------------------------
# Serial dilution across columns, row by row
# --------------------------------------------

for row in rows:
    # One tip per row to reduce tip usage
    p300.pick_up_tip()

    for col in range(start_column, last_source_column + 1):
        source = plate[f'{row}{col}']       # e.g. A1, A2, ...
        dest = plate[f'{row}{col + 1}']     # e.g. A2, A3, ...

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

        # Mix the destination well to homogenise the dilution
        # (mix_reps times, using mix_volume at mix_height)
        p300.mix(
            mix_reps,
            mix_volume,
            dest.bottom(mix_height),
            rate=mix_rate
        )

        # Optional: gently touch tip to reduce droplets on outside of tip
        p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=20)

    # After finishing the row, clear any residual liquid at the top of the last used well
    p300.blow_out(dest.top())

    # Drop the tip (we don't return it, to avoid cross-contamination)
    p300.drop_tip()

# --------------------------------------------
# Simulation log output
# --------------------------------------------
for line in protocol.commands():
    print(line)