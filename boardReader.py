from pyautogui import *
from pieceInformation import *
import numpy as np
import pyautogui
import cv2

BRIGHTNESS = 5 #zone.mp4 = 5
CONFIDENCE_LIMIT = 0.6
EXTRA_ROWS = 3 
DEBUG = {
    "GET_OUTLINE": False, 
    "LOCATE": False,
    "SCAN": False,
    "NEXT/HOLD": False,
    "TSPIN_DETECT" : False,
    "MINI_DETECT" : False,
    "ZONE": False,
    "ZONE_ATTACK": False
}

"""
Takes an image and finds the board
:return: An array of int which contains [boardX, boardY, boardWidth, boardHeight]
"""
def locate_board(image: np.array) -> np.array:
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_range = (20, 0, 150) # lower range of yellow color in HSV
    upper_range = (26, 255, 255) # upper range of yellow color in HSV
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    color_image = cv2.bitwise_and(image, image, mask=mask)

    if DEBUG["GET_OUTLINE"]:
        cv2.imshow("Image", color_image) 
        cv2.waitKey(0) 
        cv2.destroyAllWindows()  
 
    #Find the board with the given confidence value
    #If it cannot be found, drop the confidence value until you find something or until you fall below the confidence threshhold
    confidenceValue = 1
    while (confidenceValue >= CONFIDENCE_LIMIT):
        try:
            boardLocation = locate("outline.png", color_image, confidence=confidenceValue)
            if (boardLocation != None):
                break
            else: # The error below may not be caught on certain systems
                confidenceValue -= 0.01
        except pyautogui.ImageNotFoundException: 
            confidenceValue -= 0.01

    if (confidenceValue >= CONFIDENCE_LIMIT):
        # Coordinates start at the top left of the board
        boardX, boardY, boardWidth, boardHeight = boardLocation[0], boardLocation[1], boardLocation[2], boardLocation[3]

        # Estimate garbage meter width
        garbageMeterWidth = int(boardWidth/14)

        # Crop out the garbage meter then draw a rectangle with blue line borders around the board
        # Debug: Display board outline
        if DEBUG['LOCATE']:
            start_point = (boardX + garbageMeterWidth, boardY) 
            end_point = (boardX + boardWidth, boardY + boardHeight) 
            image = cv2.rectangle(image, start_point, end_point, color=(255, 0, 0) , thickness=2)  
            cv2.imshow("Image", image) 
            cv2.waitKey(0) 
            cv2.destroyAllWindows()  

        #Return coordinates of top left corner of the board with its width and height
        boardX = boardX + garbageMeterWidth
        boardWidth = boardWidth - garbageMeterWidth
        print("Board Location Found!")
        print("X:" + str(boardX) + " Y:" + str(boardY) + " Width:" + str(boardWidth) + " Height:" + str(boardHeight))
        return np.array([boardX, boardY, boardWidth, boardHeight])
    else:
        print("Unable to find board")
        return None
    
"""
Returns a string that represents a piece from the next queue
T PIECES ARE EXTREMELY IMPORTANT  (Color will be checked for it)
"""
def get_next_piece(nextLocationInfo: np.array, frame: np.array):
    # Obtain next location info
    nextX, nextY, nextWidth, nextHeight = nextLocationInfo 

    # Crop out everything but the next piece
    croppedNext = frame[nextY:nextY+nextHeight, nextX:nextX+nextWidth]  

    # Get rid of the background
    hsv_image = cv2.cvtColor(croppedNext, cv2.COLOR_BGR2HSV)
    lower_range = np.array([0,0,225]) 
    upper_range = np.array([179,255,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    croppedNext = cv2.bitwise_and(croppedNext, croppedNext, mask=mask)
    
    # Figure out the piece based on orientation 
    return get_piece_by_orientation(croppedNext)

"""
Returns a string that represents a piece from the hold queue
T PIECES ARE EXTREMELY IMPORTANT  (Color will be checked for it)
"""
def get_hold_piece(holdLocationInfo: np.array, frame: np.array):
    # Unbox board location info
    holdX, holdY, holdWidth, holdHeight = holdLocationInfo

    # Crop out everything but the next piece
    croppedNext = frame[holdY:holdY+holdHeight, holdX:holdX+holdWidth]  

    # Get rid of the background
    hsv_image = cv2.cvtColor(croppedNext, cv2.COLOR_BGR2HSV)
    lower_range = np.array([0,0,225]) 
    upper_range = np.array([179,255,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    croppedNext = cv2.bitwise_and(croppedNext, croppedNext, mask=mask)
    
    # Figure out the piece based on orientation 
    return get_piece_by_orientation(croppedNext)

"""
Grayscale and Sharpen Minos
"""
def grayscale_and_sharpen_blocks(image):
    # Gray Scale Image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

    # Median Blur to Sharpen Edges
    blurred = cv2.medianBlur(gray_image, 5)

    # Sharpen image
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(blurred, -1, sharpen_kernel)

    # Turn everything more square like
    morph_rect = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    sharpenImage = cv2.dilate(sharpen, kernel=morph_rect, iterations=1)

    return sharpenImage

"""
Uses two weights to check pieces
1. Orientation (100% weight)
2. Color of the piece (Only for T pieces)
"""
def get_piece_by_orientation(recievedPiece: np.array) -> str:
    # Calculate information about splitting the image 
    pieceX, pieceY = recievedPiece.shape[1], recievedPiece.shape[0]
    splitPieceY = round(pieceY/4)
    splitPieceX = round(pieceX/8)
    splitPieceArray = np.zeros([4,8])

    # Sharpen image
    pieceImageSharp = grayscale_and_sharpen_blocks(recievedPiece)

    # Depending on the piece with the highest confidence, it will return that one
    confidencePerPiece = np.zeros(7, np.float64)

    # Loop through each color   
    pieceImage = None
    for pieceType, pieceArray in enumerate([ZARRAY, LARRAY, OARRAY ,SARRAY, IARRAY, JARRAY, TARRAY]):

        # Initialize variables
        sumColoredPixels = 0

        # T-pieces are very important, color will be checked for them as well
        if (pieceType == 6):
            hsv_image = cv2.cvtColor(recievedPiece, cv2.COLOR_BGR2HSV)
            lower_range = np.array([100,0,230]) 
            upper_range = np.array([179,30,255])
            mask = cv2.inRange(hsv_image, lower_range, upper_range)
            pieceImage = cv2.bitwise_and(recievedPiece, recievedPiece, mask=mask)
            pieceImage = grayscale_and_sharpen_blocks(pieceImage)
        else:
            pieceImage = pieceImageSharp

        # Figure out the piece based on orientation 
        for yIndex in range(0,4):
            for xIndex in range(0,8):
                splitPiece = pieceImage[(splitPieceY*yIndex) : (splitPieceY*(yIndex+1)), 
                                  (splitPieceX*xIndex) :  (splitPieceX*(xIndex+1))]
            
                nonBlackPixels = np.count_nonzero(splitPiece)
                
                # If the number of non-black pixels is more than 40% of the cell, then mark that cell as filled
                if (nonBlackPixels/splitPiece.size > 0.40):
                    splitPieceArray[yIndex, xIndex] = 1

                # Double down on accuracy by counting the number of non-black pixels in the cell(relevant when zone is active)
                if (pieceArray[yIndex, xIndex] == 1):
                    if (pieceType == 6): # If T piece, increase confidence
                        sumColoredPixels += round(nonBlackPixels * 1.5)
                    else:
                        sumColoredPixels += nonBlackPixels

                if DEBUG['NEXT/HOLD']:
                    cv2.line(pieceImage, (splitPieceX * xIndex, 0), (splitPieceX * xIndex, pieceY), (0, 255, 0), thickness=1)
                    cv2.line(pieceImage, (0,splitPieceY * yIndex), (pieceX, splitPieceY * yIndex), (0, 255, 0), thickness=1)

        if DEBUG['NEXT/HOLD']:
            cv2.imshow("Next", pieceImage) 

        # How much of the piece overlaps with the expected layout (50% weight)
        matchingParts = np.sum((pieceArray == 1) & (splitPieceArray == 1))
        confidencePerPiece[pieceType] += (matchingParts/16) * 0.50

        # Same thing as above but uses the number of pixels instead (50% weight)
        confidencePerPiece[pieceType] += (sumColoredPixels / round(16 * splitPiece.size)) * 0.50

    # Returns index of the piece with the highest confidence value 
    indexMax = np.argmax(confidencePerPiece)

    # If the confidence is low, returns ?
    if confidencePerPiece[indexMax] < 0.55:
        return "?"
    
    # If the difference between the two highest confidence is too close, returns ?
    sorted_array = np.sort(confidencePerPiece)[::-1]
    highest = sorted_array[0]
    second_highest = sorted_array[1]
    difference = highest - second_highest
    if (difference < 0.05):
        return "?"

    return PIECE_NAMES[indexMax]

"""
Returns a 2D array of the board state (what part of the board is filled or not)
"""
def scan_board(boardLocationInfo: np.array, frame: int) -> np.array:
    # Unbox board location info
    boardX, boardY, boardWidth, boardHeight = boardLocationInfo

    # Calculate variables
    colPixels = round(boardHeight/20)
    rowPixels = round(boardWidth/10)
    pixelPerMino = rowPixels * colPixels
    boardState = np.full([20 + EXTRA_ROWS, 10], " ", dtype=object)

    if (EXTRA_ROWS != 0):
        boardHeight = boardHeight + (colPixels * EXTRA_ROWS)
        boardY = boardY - (colPixels * EXTRA_ROWS)
    
    croppedBoard = frame[boardY:boardY+boardHeight, boardX:boardX+boardWidth]
    croppedBoard = filter_image(croppedBoard)

    boardXShape, boardYShape = croppedBoard.shape[1], croppedBoard.shape[0]
    splitBoardY = round(boardYShape/(20 + EXTRA_ROWS))
    splitBoardX = round(boardXShape/10)

    #Iterate through all the minos on the board
    for colIndex in reversed(range(20 + EXTRA_ROWS)):
      for rowIndex in range(10):
        croppedMino = croppedBoard[(colPixels*colIndex) : (colPixels*(colIndex+1)), 
                                  (rowPixels*rowIndex) :  (rowPixels*(rowIndex+1))]
        
        # # Use number black pixels to check if there is a mino present
        blackPixels = np.sum(croppedMino == 0)

        # If the number of black pixels is more than 35% of the cell, then mark corresponding cell as filled
        if (blackPixels/pixelPerMino > 0.35):
            boardState[colIndex, rowIndex] = "■"

        if DEBUG["SCAN"]:
            cv2.line(croppedBoard, (splitBoardX * rowIndex, 0), (splitBoardX * rowIndex, boardYShape), (0, 255, 0), thickness=1)
            cv2.line(croppedBoard, (0,splitBoardY * colIndex), (boardXShape, splitBoardY * colIndex), (0, 255, 0), thickness=1)

    # Debug: Show cropped board
    if DEBUG['SCAN']:
        cv2.imshow("Cropped board", croppedBoard) 

    return(boardState)

"""
Filter out background, particles, and light coming from dropping pieces
"""
def filter_image(old_image: np.array) -> np.array: 
    # Attempt to get rid of the background
    hsv_image = cv2.cvtColor(old_image, cv2.COLOR_BGR2HSV)
    # Get values based off brightness
    HSVranges = get_brightness_settings(BRIGHTNESS)
    lower_range1, upper_range1, lower_range2, upper_range2, lower_range3, upper_range3 = HSVranges[0], HSVranges[1], HSVranges[2], HSVranges[3], HSVranges[4], HSVranges[5]

    # Lower mask
    lower_range = np.array(lower_range1) 
    upper_range = np.array(upper_range1)
    mask1 = cv2.inRange(hsv_image, lower_range, upper_range)
    # upper mask 
    lower_range = np.array(lower_range2)
    upper_range = np.array(upper_range2)
    mask2 = cv2.inRange(hsv_image, lower_range, upper_range)
    # Mask for specifically garbage 
    lower_range = np.array([0,0,0]) 
    upper_range = np.array([179,50,255])
    mask3 = cv2.inRange(hsv_image, lower_range, upper_range)
    # Join all masks to filter out most of the background 
    maskBackground = mask1+mask2+mask3
    new_image = cv2.bitwise_and(old_image, old_image, mask=maskBackground)

    # Get rid of light from placing pieces
    hsv_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2HSV)
    lower_range = np.array(lower_range3)
    upper_range = np.array(upper_range3)
    maskLight = cv2.inRange(hsv_image, lower_range, upper_range)
    maskLight = 255-maskLight
    new_image2 = cv2.bitwise_and(new_image, new_image, mask=maskLight)

    # Gray Scale
    gray_image = cv2.cvtColor(new_image2, cv2.COLOR_BGR2GRAY)

    # Median Blur to Sharpen Edges
    blurred = cv2.medianBlur(gray_image, 7)

    # Sharpen Image and Implement Threshold
    #https://stackoverflow.com/questions/55169645/square-detection-in-image
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(blurred, -1, sharpen_kernel)    
    thresh = cv2.threshold(sharpen, 85, 255, cv2.THRESH_BINARY_INV)[1]
    
    return thresh

"""
Check for TSpin Type by checking SI[N]GLE, DO[U]BLE, T[RI]PLE
"""
def identify_tspin_type(tSpinIndicatorLocationInfo, frame):
    tSpinIndicatorX, tSpinIndicatorY, tSpinIndicatorWidth, tSpinIndicatorHeight = tSpinIndicatorLocationInfo

    # Crop out everything but the letter
    croppedLetter = frame[tSpinIndicatorY:tSpinIndicatorY+tSpinIndicatorHeight, tSpinIndicatorX:tSpinIndicatorX+tSpinIndicatorWidth]  

    # Get rid of the background
    hsv_image = cv2.cvtColor(croppedLetter, cv2.COLOR_BGR2HSV)
    lower_range = np.array([25,150,150]) 
    upper_range = np.array([35,255,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    letterImage = cv2.bitwise_and(croppedLetter, croppedLetter, mask=mask)

    letterXShape, letterYShape = letterImage.shape[1], letterImage.shape[0]
    splitLetterPieceY = round(letterYShape/6)
    splitLetterPieceX = round(letterXShape/4)

    splitLetterArray = np.zeros([6,4])
    for yIndex in range(0,6):
        for xIndex in range(0,4):
            splitLetter = letterImage[(splitLetterPieceY*yIndex) : (splitLetterPieceY*(yIndex+1)), 
                                  (splitLetterPieceX*xIndex) :  (splitLetterPieceX*(xIndex+1))]

            nonBlackPixels = np.count_nonzero(splitLetter)

            # If the number of non-black is more than 40% of the cropped area, then mark that area as filled
            if (nonBlackPixels/splitLetter.size > 0.40):
                    splitLetterArray[yIndex, xIndex] = 1

            if DEBUG["TSPIN_DETECT"]:
                cv2.line(letterImage, (splitLetterPieceX * xIndex, 0), (splitLetterPieceX * xIndex, letterYShape), (0, 255, 0), thickness=1)
                cv2.line(letterImage, (0,splitLetterPieceY * yIndex), (letterXShape, splitLetterPieceY * yIndex), (0, 255, 0), thickness=1)
    
    if DEBUG["TSPIN_DETECT"]:
        cv2.imshow("Detect TSpin", letterImage)
        cv2.waitKey(0)
        print(splitLetterArray)
    
    for index, detectLetter in enumerate([TSS, TSD, TST]):
        if np.array_equal(splitLetterArray, detectLetter):
            return TSPIN_NAMES[index]
    return None

def detect_mini(miniIndicatorLocationInfo, frame):
    miniIndicatorX, miniIndicatorY, miniIndicatorWidth, miniIndicatorHeight = miniIndicatorLocationInfo

    # Same concept as identify_tspin_type
    croppedLetter = frame[miniIndicatorY:miniIndicatorY+miniIndicatorHeight, miniIndicatorX:miniIndicatorX+miniIndicatorWidth]  

    hsv_image = cv2.cvtColor(croppedLetter, cv2.COLOR_BGR2HSV)
    lower_range = np.array([25,150,150]) 
    upper_range = np.array([35,255,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    letterImage = cv2.bitwise_and(croppedLetter, croppedLetter, mask=mask)

    letterXShape, letterYShape = letterImage.shape[1], letterImage.shape[0]
    splitLetterPieceY = round(letterYShape/7)
    splitLetterPieceX = round(letterXShape/5)

    splitLetterArray = np.zeros([7,5])
    for yIndex in range(0,7):
        for xIndex in range(0,5):
            splitLetter = letterImage[(splitLetterPieceY*yIndex) : (splitLetterPieceY*(yIndex+1)), 
                                  (splitLetterPieceX*xIndex) :  (splitLetterPieceX*(xIndex+1))]

            nonBlackPixels = np.count_nonzero(splitLetter)

            # If the number of non-black is more than 40% of the cropped area, then mark that area as filled
            if (nonBlackPixels/splitLetter.size > 0.40):
                    splitLetterArray[yIndex, xIndex] = 1

            if DEBUG["MINI_DETECT"]:
                cv2.line(letterImage, (splitLetterPieceX * xIndex, 0), (splitLetterPieceX * xIndex, letterYShape), (0, 255, 0), thickness=1)
                cv2.line(letterImage, (0,splitLetterPieceY * yIndex), (letterXShape, splitLetterPieceY * yIndex), (0, 255, 0), thickness=1)
    
    if DEBUG["MINI_DETECT"]:
        cv2.imshow("Detect Mini", letterImage)
        # cv2.waitKey(0)
        # print(splitLetterArray)
    
    return np.array_equal(splitLetterArray, MINI)

def detect_zone(zoneLocationInfo, frame):
    zoneX, zoneY, zoneWidth, zoneHeight = zoneLocationInfo

    # Same concept as identify_tspin_type
    croppedZone = frame[zoneY:zoneY+zoneHeight, zoneX:zoneX+zoneWidth]  

    hsv_image = cv2.cvtColor(croppedZone, cv2.COLOR_BGR2HSV)
    lower_range = np.array([0,0,210]) 
    upper_range = np.array([179,25,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    zoneImage = cv2.bitwise_and(croppedZone, croppedZone, mask=mask)

    if DEBUG["ZONE"]:
        cv2.imshow("Zone", zoneImage)

    # If the number of non-black is more than 30% of the cropped area, then zone should be on
    nonBlackPixels = np.count_nonzero(zoneImage)
    return (nonBlackPixels/zoneImage.size > 0.3)

def identify_atk_digit(zoneAttackLocationInfo, frame):
    zoneAttackX, zoneAttackY, zoneAttackWidth, zoneAttackHeight = zoneAttackLocationInfo

    # Same concept as identify_tspin_type
    croppedAtk = frame[zoneAttackY:zoneAttackY+zoneAttackHeight, zoneAttackX:zoneAttackX+zoneAttackWidth]  

    hsv_image = cv2.cvtColor(croppedAtk, cv2.COLOR_BGR2HSV)
    lower_range = np.array([10,55,100]) 
    upper_range = np.array([28,150,255])
    mask = cv2.inRange(hsv_image, lower_range, upper_range)
    atkImage = cv2.bitwise_and(croppedAtk, croppedAtk, mask=mask)

    # # Median Blur to Sharpen Edges
    # blurred = cv2.medianBlur(atkImage, 5)

    # Sharpen image
    # sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    # atkImage = cv2.filter2D(atkImage, -1, sharpen_kernel)

    numberXShape, numberYShape = atkImage.shape[1], atkImage.shape[0]
    splitNumberPieceY = round(numberYShape/12)
    splitNumberPieceX = round(numberXShape/9)

    splitNumberArray = np.zeros([12,9])

    for yIndex in range(0,12):
        for xIndex in range(0,9):
            splitNumber = atkImage[(splitNumberPieceY*yIndex) : (splitNumberPieceY*(yIndex+1)), 
                                  (splitNumberPieceX*xIndex) :  (splitNumberPieceX*(xIndex+1))]

            nonBlackPixels = np.count_nonzero(splitNumber)

            # If the number of non-black is more than 30% of the cropped area, then mark that area as filled
            if (nonBlackPixels/splitNumber.size > 0.30):
                    splitNumberArray[yIndex, xIndex] = 1

            if DEBUG["ZONE"]:
                cv2.line(atkImage, (splitNumberPieceX * xIndex, 0), (splitNumberPieceX * xIndex, numberYShape), (0, 255, 0), thickness=1)
                cv2.line(atkImage, (0,splitNumberPieceY * yIndex), (numberXShape, splitNumberPieceY * yIndex), (0, 255, 0), thickness=1)

    
    confidencePerNumber = np.zeros(10, np.float64)
    
    for index, numberArray in enumerate([ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]):
        matchingOnes = np.sum((numberArray == 1) & (splitNumberArray == 1))
        confidencePerNumber[index] += (matchingOnes/(np.count_nonzero(numberArray == 1))) * 0.75

        matchingZeros = np.sum((numberArray == 0) & (splitNumberArray == 0))
        confidencePerNumber[index] += (matchingZeros/(np.count_nonzero(numberArray == 0))) * 0.25

    if DEBUG["ZONE_ATTACK"]:
        print(splitNumberArray)
        print(confidencePerNumber)
        cv2.imshow("Zone Attack", atkImage)
        cv2.waitKey(0)

    indexMax = np.argmax(confidencePerNumber)
    if (confidencePerNumber[indexMax] < 0.65):
        return -1
    
    return indexMax
