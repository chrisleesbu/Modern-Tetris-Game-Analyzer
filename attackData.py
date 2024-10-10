from enum import Enum

# Combo data
COMBO_NO_ZONE = [0,0,1,1,2,2,2,3,3,3,3,3,3]
COMBO_ZONE    = [0,0,1,1,2,2,2,2,2,2]

# Attack Bonus of each Zone
# https://twitter.com/enhance_exp/status/1461077132554035202
QUARTER_ZONE =          [1,2,2,3,4,4,5,6,6,7,8,8,9,10,10,11,12,12,13,18,24,32,40]
HALF_ZONE =             [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,24,30,38,48]
THREE_QUARTER_ZONE =    [1,2,3,4,6,7,8,9,10,12,13,14,15,16,18,19,20,21,22,28,34,46,60]
FULL_ZONE =             [1,3,4,6,7,9,11,12,13,15,16,18,19,21,22,24,25,27,28,34,46,62,80]

"""
All line clear types 
"""
class LineType(Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    TRIPLE = "Triple"
    TETRIS = "Tetris"
    TSS = "TSpin Single"
    TSD = "TSpin Double"
    TST = "TSpin Triple"
    MTSS = "Mini TSpin Single"
    MTSD = "Mini TSpin Double"

    """
    Returns how much garbage each line type sends
    """
    def garbage_sent(lineType):
        match lineType:
            case LineType.DOUBLE | LineType.MTSD:
                 return 1
            case LineType.TRIPLE | LineType.TSS:
                return 2
            case LineType.TETRIS | LineType.TSD:
                return 4
            case  LineType.TST:
                return 6
            case _:
                return 0
            
    """
    Returns True if the line type can back-to-back else False
    """
    def can_b2b(lineType):
        if lineType in [LineType.TETRIS, LineType.TSS, LineType.TSD, LineType.TST, LineType.MTSS, LineType.MTSD]:
            return True
        return False
                
    """
    Returns True if the line type can cleared a line else False
    This function is useless if TSpin Zeros are not implemented
    """
    def is_line_clear(lineType):
        if lineType in [LineType.SINGLE, LineType.DOUBLE, LineType.TRIPLE, LineType.TETRIS,
                        LineType.TSS, LineType.TSD, LineType.TST, LineType.MTSS, LineType.MTSD]:
            return True
        return False

    """
    Returns how much garbage is sent for each combo outside of zone
    """
    def get_combo_no_zone_garbage(combo: int):
        if (combo > len(COMBO_NO_ZONE)):
            return 4
        return COMBO_NO_ZONE[combo]
    
    """
    Returns how much garbage is sent for each combo in zone
    """
    def get_combo_zone_garbage(combo: int):
        if (combo > len(COMBO_NO_ZONE)):
            return 3
        return COMBO_NO_ZONE[combo]
    
    """
    Returns how much garbage is sent based off the charge of the zone and the number of lines
    """
    def get_zone_garbage(charge, lines):
        return charge[lines-1]
    
    """
    Returns how much garbage is sent based on line type, combo, zone duration, and zone lines (not finished)
    """
    def get_total_garbage(lineType, combo, b2bActive):
        return LineType.garbage_sent(lineType) + LineType.get_combo_no_zone_garbage(combo) + int(b2bActive)