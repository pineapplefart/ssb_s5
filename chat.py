from opentrons import simulate

# Metadata for simulator
metadata = {'apiLevel': '2.19'}

# Create a simulated protocol context (virtual OT-2)
protocol = simulate.get_protocol_api('2.19')

# -----------------------
# Labware and pipette
# -----------------------

# 96-well flat-bottom plate in deck slot 1
plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)

# 300 µL tip rack in deck slot 2
tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

# 12-channel reservoir (for fluorescein + PBS + optional waste) in slot 3
reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 3)

# Single-channel P300 GEN2 on the right
p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1])

# -----------------------
# Speed presets (dimensionless multipliers)
# -----------------------

high = 1.8     # very fast
normal = 1.0   # default
slow = 0.5     # gentle
vslow = 0.25   # very gentle

# -----------------------
# Base flow rates (µL/s)
# -----------------------

p300.flow_rate.aspirate = 80
p300.flow_rate.dispense = 40
p300.flow_rate.blow_out = 150

# -----------------------
# Volumes (µL)
# -----------------------

# Prefill stage
fluorescein_volume = 200     # col 1
pbs_volume = 100             # cols 2–12

# Serial dilution stage
dilution_volume = 100        # transfer volume col n -> col n+1
mix_volume = 150             # volume used in each mix cycle

# -----------------------
# Heights (mm from well bottom)
# -----------------------

# Reservoir aspiration height
res_asp_height = 1.5

# Plate aspiration/dispense heights
plate_asp_height = 1.0
plate_disp_height = 1.0

# Mixing heights inside the destination well
mix_low_height = 0.8
mix_mid_height = 1.5
mix_high_height = 2.5

# -----------------------
# Sources in reservoir
# -----------------------

fluorescein_src = reservoir['A1']   # fluorescein working stock
pbs_src = reservoir['A2']           # PBS
waste = reservoir['A12']            # optional liquid waste (not on plate)

# Plate rows: use all 8; for strict iGEM you might restrict to ['A','B','C','D']
rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# ============================================================
# STEP 1 – PREFILL PLATE
#   Col 1: fluorescein (200 µL)
#   Col 2–12: PBS (100 µL)
# ============================================================

# --- Fill column 1 with fluorescein ---
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

        p300.drop_tip()

# ============================================================
# STEP 2 – SERIAL DILUTION ACROSS COLUMNS
#   For each row:
#       1 -> 2 -> 3 -> ... -> 11
#   Column 12 remains PBS-only blank (0% fluorescein)
# ============================================================

start_column = 1
last_source_column = 10  # 1→2, 2→3, ..., 10→11

for row in rows:
    # One tip per row (liquid only moves "forward" so cross-contam is controlled)
    p300.pick_up_tip()

    for col in range(start_column, last_source_column + 1):
        source = plate[f'{row}{col}']
        dest = plate[f'{row}{col + 1}']

        # --- Transfer 100 µL from source to dest ---

        # Aspirate slowly from source to avoid bubbles
        p300.aspirate(
            dilution_volume,
            source.bottom(plate_asp_height),
            rate=slow
        )

        # Dispense at normal speed into destination
        p300.dispense(
            dilution_volume,
            dest.bottom(plate_disp_height),
            rate=normal
        )

        # --- Mix dest 3× at different heights ---
        # Mix 1: low
        p300.aspirate(
            mix_volume,
            dest.bottom(mix_low_height),
            rate=slow
        )
        p300.dispense(
            mix_volume,
            dest.bottom(mix_low_height),
            rate=normal
        )

        # Mix 2: mid
        p300.aspirate(
            mix_volume,
            dest.bottom(mix_mid_height),
            rate=slow
        )
        p300.dispense(
            mix_volume,
            dest.bottom(mix_mid_height),
            rate=normal
        )

        # Mix 3: high
        p300.aspirate(
            mix_volume,
            dest.bottom(mix_high_height),
            rate=slow
        )
        p300.dispense(
            mix_volume,
            dest.bottom(mix_high_height),
            rate=normal
        )

        # Optional: touch tip to side of well to remove droplets
        p300.touch_tip(dest, radius=0.7, v_offset=-1, speed=20)

    # After finishing the serial dilution along this row,
    # blow out any remaining liquid into the last destination well (col 11)
    p300.blow_out(dest.top())

    p300.drop_tip()

for line in protocol.commands():
    print(line)
