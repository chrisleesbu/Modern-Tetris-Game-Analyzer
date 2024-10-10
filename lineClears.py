import numpy as np
from attackData import *

lineTypeHistory = []
attackTotal = 0
miniDetectFrameCount = 0
DEBUG = {
    "PRINT": True # Prints out line type history
}

def printHistory():
    print("Frame Count: \tLine Clear Type: \tCurrent Piece: \tCombo: \tB2B Bonus: \tFixedT:")
    for storedInfo in lineTypeHistory:
        storedFrame, storedType, storedPiece, storedCombo, storedb2b, fixedT = storedInfo
        print(str(storedFrame) + "\t\t" + str(storedType) + "\t\t" + str(storedPiece) + "\t\t" + str(storedCombo) + "\t" + str(storedb2b) + "\t\t" + str(fixedT))
    print()

def calculateLineType(prevBoardState, activeBoardState):
    # NOTE: Checking only up to 19 height for now 
    prevBoardState = prevBoardState[5:]
    activeBoardState = activeBoardState[5:]

    # Calculate Height Difference 
    linesRemoved = checkHeight(prevBoardState) - checkHeight(activeBoardState)
    match linesRemoved:
        case 1: 
            return LineType.SINGLE
        case 2: 
            return LineType.DOUBLE
        case 3:
            return LineType.TRIPLE
        case 4:
            return LineType.TETRIS
    return None
        
def checkHeight(boardState):
    height = 19
    for row in boardState:
        if (np.any(row == "■")):
            return height
        height -= 1
    return 0

"""
This function will first fix anomilies then calculate the attack and add it to the total
"""
def addLineType(frameCount, lineType, pieceUsed, combo):
    global attackTotal
    global lineTypeHistory

    lineTypeInfo = [frameCount, lineType, pieceUsed, combo, False, False]
    fixedLineType = fixLineType(lineTypeInfo)
    
    if (len(lineTypeHistory) > 5):
        lineTypeHistory.pop(0)

    if (fixedLineType is not None):
        lineTypeHistory.append(fixedLineType)

    if DEBUG["PRINT"]:
        printHistory()

"""
This function will attempt to fix stats in the line clear type history
"""
def fixLineType(givenInfo):
    global lineTypeHistory
    global attackTotal

    givenFrame, givenType, givenPiece, givenCombo, givenb2b, fixedT = givenInfo

    if (givenPiece == 'T' and (givenType == LineType.SINGLE or givenType == LineType.DOUBLE or givenType == LineType.TRIPLE)):
        # Check for T-spins
        for index, storedInfo in enumerate(lineTypeHistory):
            storedFrame, storedType, storedPiece, storedCombo, storedb2b, fixedT = storedInfo
            if (fixedT == False):
                # Found T-spin before line clear check
                if (givenFrame - storedFrame <= 10):
                    if (((storedType == LineType.TSS or storedType == LineType.MTSS) and givenType == LineType.SINGLE) or 
                    ((storedType == LineType.TSD or storedType == LineType.MTSD) and givenType == LineType.DOUBLE) or 
                    (storedType == LineType.TST and givenType == LineType.TRIPLE)):
                        lineTypeHistory[index][3] = givenCombo
                        lineTypeHistory[index][5] = True
                        attackTotal += LineType.get_total_garbage(storedType, givenCombo, storedb2b)
                        return None
                
    # Check for Back-to-Back
    if (len(lineTypeHistory) == 0):
        givenb2b = False
    elif (LineType.can_b2b(lineTypeHistory[-1][1]) and LineType.can_b2b(givenType)):
        givenb2b = True
    else:
        givenb2b = False

    attackTotal += LineType.get_total_garbage(givenType, givenCombo, givenb2b)              
    return [givenFrame, givenType, givenPiece, givenCombo, givenb2b, False]

"""
T-spins are mostly detected before the line clear type is checked (after can also occur)
Add the attack first and if there is combo or b2b, adjust the attack later
"""
def storeTSpinAttack(tSpinFoundFrameCount, tSpinType):
    global lineTypeHistory

    if (len(lineTypeHistory) == 0):
        givenb2b = False
    elif (LineType.can_b2b(lineTypeHistory[-1][1])):
        givenb2b = True
    else:
        givenb2b = False
        
    frameDifference = tSpinFoundFrameCount - miniDetectFrameCount
    if (frameDifference <= 30):
        if tSpinType == "TSS":
            tSpinType = "MTSS"
        elif tSpinType == "TSD":
            tSpinType = "MTSD"
        
    lineTypeConvert = None
    match tSpinType:
        case "TSS":
            lineTypeConvert = LineType.TSS
        case "TSD":
            lineTypeConvert = LineType.TSD
        case "TST":
            lineTypeConvert = LineType.TST
        case "MTSS":
            lineTypeConvert = LineType.MTSS
        case "MTSD":
            lineTypeConvert = LineType.MTSD
        case _:
            print("This shouldn't be printed")

    lineTypeHistory.append([tSpinFoundFrameCount, lineTypeConvert, 'T', '?', givenb2b, False])

    if (len(lineTypeHistory) >= 2):
        for index, storedInfo in enumerate(lineTypeHistory):
            storedFrame, storedType, storedPiece, storedCombo, storedb2b, fixedT = storedInfo
            frameDifference = tSpinFoundFrameCount - storedFrame
            # Found T-spin AFTER line clear check
            if (frameDifference <= 45 and frameDifference != 0):
                if (storedPiece == 'T'):
                    if (fixedT == False):
                        if (((tSpinType == "TSS" or tSpinType == "MTSS") and storedType == LineType.SINGLE) or 
                        ((tSpinType == "TSD" or tSpinType == "MTSD") and storedType == LineType.DOUBLE) or 
                        (tSpinType == "TST" and storedType == LineType.TRIPLE)):
                            del lineTypeHistory[index]
                            lineTypeHistory[-1][3] = storedCombo

                            global attackTotal
                            attackTotal -= LineType.get_total_garbage(storedType, storedCombo, storedb2b)
                            attackTotal += LineType.get_total_garbage(lineTypeConvert, storedCombo, givenb2b)

    if DEBUG["PRINT"]:
        printHistory()

def storeMini(miniFoundFrameCount):
    global miniDetectFrameCount
    miniDetectFrameCount = miniFoundFrameCount

def get_Attack_Total():
    return attackTotal

def add_Attack_Total(zone_attack):
    global attackTotal
    attackTotal += zone_attack





        
        
