

# ## Opentrons - Serial Dilution
# ---

# ### Opentrons Protocol format



from opentrons import protocol_api

metadata = {'apiLevel': '2.13'}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 2)
    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 3)

    # Pipettes
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks = [tips])
    p300.flow_rate.aspirate = 50
    p300.flow_rate.dispense = 50

    # PBS loading
    p300.pick_up_tip()

    for i in range(11):
        top_row = plate.rows()[0]
        p300.transfer(100, reservoir['A2'], top_row[i+1], mix_before = (3, 50), blow_out = True, new_tip = 'never')

    p300.drop_tip()

    # Fluorescein loading
    p300.transfer(200, reservoir['A1'], top_row[0], mix_before = (3, 50), blow_out = True, new_tip = 'once')

    # Serial dilutions
    p300.pick_up_tip()
    
    for i in range(10):
        p300.transfer(100, top_row[i], top_row[i+1], mix_before = (3, 50), mix_after = (3, 50), blow_out = True, new_tip = 'never')

    p300.transfer(100, top_row[10], reservoir['A12'], mix_before = (3, 50), new_tip = 'never')
    p300.drop_tip()
