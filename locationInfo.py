import numpy as np

def get_next_location(boardLocationInfo, quene):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    nextWidth = round(boardWidth/4)
    nextHeight = round(boardHeight/16)
    nextX = boardX + boardWidth + round(boardWidth/8.75)
    nextY = boardY + round(boardHeight/18.7) + ((quene-1) * round(boardHeight/7.7))

    return np.array([nextX, nextY, nextWidth, nextHeight])

def get_hold_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    holdWidth = round(boardWidth/4)
    holdHeight = round(boardHeight/16)
    holdX = boardX - round(boardWidth/2.6)
    holdY = boardY + round(boardHeight/18.7)

    return np.array([holdX, holdY, holdWidth, holdHeight])

def get_tspin_indicator_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    tSpinIndicatorWidth = round(boardWidth/23)
    tSpinIndicatorHeight = round(boardHeight/27)
    tSpinIndicatorX = boardX - round(boardWidth/3.45)
    tSpinIndicatorY = boardY + round(boardHeight/2.73)

    return np.array([tSpinIndicatorX, tSpinIndicatorY, tSpinIndicatorWidth, tSpinIndicatorHeight])

def get_mini_indicator_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    miniWidth = round(boardWidth/21)
    miniHeight = round(boardHeight/27)
    miniX = boardX - round(boardWidth/1.58)
    miniY = boardY + round(boardHeight/3.1)

    return np.array([miniX, miniY, miniWidth, miniHeight])

def get_zone_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    zoneWidth = round(boardWidth/22)
    zoneHeight = round(boardHeight/60)
    zoneX = boardX + round(boardWidth / 2.1)
    zoneY = boardY + boardHeight + round(boardHeight/400)

    return np.array([zoneX, zoneY, zoneWidth, zoneHeight])

# Currently only supports two digits
def get_attack_location(boardLocationInfo, digitLocation):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    atkWidth = round(boardWidth/15.4)
    atkHeight = round(boardHeight/21)
    atkY = round(boardY) + round(boardHeight/1.87)
    if (digitLocation == "doubleLeft"):
        atkX = round(boardX) + round(boardWidth/6) 
    elif (digitLocation == "doubleRight"):
        atkX = round(boardX) + round(boardWidth/4.1)
    else:
        atkX = round(boardX) + round(boardWidth/4.9)

    return np.array([atkX, atkY, atkWidth, atkHeight])

def get_text_apm_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    apmTextX = boardX + boardWidth + round(boardWidth/12)
    apmTextY = boardY + round(boardHeight/1.3)
    return (apmTextX, apmTextY)

def get_actual_apm_location(boardLocationInfo):
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    apmTextX = boardX + boardWidth + round(boardWidth/13)
    apmTextY = boardY + round(boardHeight/1.2)
    return (apmTextX, apmTextY)