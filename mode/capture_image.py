from locationInfo import *
from boardReader import *
import random

DEBUG = {
    "NEXT_PIECE" : False, # Prints out the next 4 pieces
    "HOLD_PIECE" : False, # Prints out the hold piece
    "TSPIN_TYPE" : False, # Prints out the T-Spin Type (None if not found)
    "DETECT_MINI" : False, # Prints out if T-Spin Mini is detected
    "DETECT_ZONE" : False, # Prints out whether or not the player is in zone
    "DETECT_ZONE_ATTACK": False, # Prints out zone attack if found
    "BOARD_STATE": False,# Prints out the board state
    "PRINT_APM": False, # Prints out random APM at expected location (random for images)
    "SAVE_IMAGE": False # Saves the image
}

def image_mode(src, isDisplay):
    # Differentiate from file path (read from image) and image (read frame from video)
    if (type(src) == str):
        image = cv2.imread(src)
    else:
        image = src

    boardLocation = None
    if (boardLocation is None):
        # newBoardLocation = locate_board(image)
        newBoardLocation = np.array([614,291,390,780])
        
        if (newBoardLocation is not None):
            next1Location = get_next_location(newBoardLocation, 1)
            next2Location = get_next_location(newBoardLocation, 2)
            next3Location = get_next_location(newBoardLocation, 3)
            next4Location = get_next_location(newBoardLocation, 4)
            holdLocation = get_hold_location(newBoardLocation)
            tSpinIndicatorLocation = get_tspin_indicator_location(newBoardLocation)
            miniIndicatorLocation = get_mini_indicator_location(newBoardLocation)
            zoneLocation = get_zone_location(newBoardLocation)
            atkDblLeftLocation = get_attack_location(newBoardLocation, "doubleLeft")
            atkDblRightLocation = get_attack_location(newBoardLocation, "doubleRight")
            atkSingleLocation = get_attack_location(newBoardLocation, "single")
            textAPMDisplayLocation = get_text_apm_location(newBoardLocation)
            actualAPMDisplayLocation = get_actual_apm_location(newBoardLocation)

            boardLocation = newBoardLocation
            #cv2.rectangle(image,(boardLocation[0],boardLocation[1]-119),(boardLocation[0]+boardLocation[2],boardLocation[1]+boardLocation[3]),(0,255,0),2)

    # Get the next four pieces
    if DEBUG["NEXT_PIECE"]:   
        nextPiece = get_next_piece(next1Location, image)
        nextPiece2 = get_next_piece(next2Location, image)
        nextPiece3 = get_next_piece(next3Location, image)
        nextPiece4 = get_next_piece(next4Location, image)
        #cv2.rectangle(image,(next1Location[0],next1Location[1]),(next1Location[0]+next1Location[2],next1Location[1]+next1Location[3]),(0,255,0),2)
        #cv2.rectangle(image,(next2Location[0],next2Location[1]),(next2Location[0]+next2Location[2],next2Location[1]+next2Location[3]),(0,255,0),2)
        #cv2.rectangle(image,(next3Location[0],next3Location[1]),(next3Location[0]+next3Location[2],next3Location[1]+next3Location[3]),(0,255,0),2)
        #cv2.rectangle(image,(next4Location[0],next4Location[1]),(next4Location[0]+next4Location[2],next4Location[1]+next4Location[3]),(0,255,0),2)

        print("Next: " + nextPiece + " " + nextPiece2 + " " + nextPiece3 + " " + nextPiece4)

    if DEBUG["HOLD_PIECE"]:
        holdPiece = get_hold_piece(holdLocation, image)
        #cv2.rectangle(image,(holdLocation[0],holdLocation[1]),(holdLocation[0]+holdLocation[2],holdLocation[1]+holdLocation[3]),(0,255,0),2)
        print("Hold: " + holdPiece)
    
    if DEBUG["TSPIN_TYPE"]:
        tSpinType = identify_tspin_type(tSpinIndicatorLocation, image)
        #cv2.rectangle(image,(tSpinIndicatorLocation[0],tSpinIndicatorLocation[1]),(tSpinIndicatorLocation[0]+tSpinIndicatorLocation[2],tSpinIndicatorLocation[1]+tSpinIndicatorLocation[3]),(0,255,0),2)
        print("TSpin Type: " + str(tSpinType))

    if DEBUG["DETECT_MINI"]:
        miniDetected = detect_mini(miniIndicatorLocation, image)
        #cv2.rectangle(image,(miniIndicatorLocation[0],miniIndicatorLocation[1]),(miniIndicatorLocation[0]+miniIndicatorLocation[2],miniIndicatorLocation[1]+miniIndicatorLocation[3]),(0,255,0),2)
        print("Mini Detected: " + str(miniDetected))

    if DEBUG["DETECT_ZONE"]:
        zoneDetection = detect_zone(zoneLocation, image)
        #cv2.rectangle(image,(zoneLocation[0],zoneLocation[1]),(zoneLocation[0]+zoneLocation[2],zoneLocation[1]+zoneLocation[3]),(0,255,0),2)
        print("Zone Detected: " + str(zoneDetection))
    
    if DEBUG["DETECT_ZONE_ATTACK"]:
        # One Digit Zone Attack
        singleDigit = identify_atk_digit(atkSingleLocation, image)

        # Two Digit Zone Attack
        doubleLeftDigit = identify_atk_digit(atkDblLeftLocation, image)
        doubleRightDigit = identify_atk_digit(atkDblRightLocation, image)

        #cv2.rectangle(image,(atkDblLeftLocation[0],atkDblLeftLocation[1]),(atkDblLeftLocation[0]+atkDblLeftLocation[2],atkDblLeftLocation[1]+atkDblLeftLocation[3]),(0,255,0),2)
        #cv2.rectangle(image,(atkDblRightLocation[0],atkDblRightLocation[1]),(atkDblRightLocation[0]+atkDblRightLocation[2],atkDblRightLocation[1]+atkDblRightLocation[3]),(0,255,0),2)

        if (singleDigit != -1):
            print("Zone Attack: " + str(singleDigit))
        elif (doubleLeftDigit != -1 and doubleRightDigit != -1):
            print("Zone Attack: " + str((doubleLeftDigit * 10) + singleDigit))
        else:
            print("Unable to find zone attack")

    if DEBUG["BOARD_STATE"]:
        print(scan_board(newBoardLocation, image))
    
    if DEBUG["PRINT_APM"]:
        message = "APM"
        location = textAPMDisplayLocation
        font = cv2.FONT_HERSHEY_DUPLEX         
        fontScale = 1
        color = (255, 255, 255)
        thickness = 2
        cv2.putText(image, message, location, font, fontScale, color, thickness, cv2.LINE_AA)
        message = str(round(random.uniform(0, 120),2))
        location = actualAPMDisplayLocation
        font = cv2.FONT_HERSHEY_DUPLEX         
        fontScale = 1.5
        color = (255, 255, 255)
        thickness = 2
        cv2.putText(image, message, location, font, fontScale, color, thickness, cv2.LINE_AA)
    if DEBUG["SAVE_IMAGE"]:
        cv2.imwrite("saved.jpg", image)
    if (isDisplay):
        cv2.imshow("Image", image)
        cv2.waitKey(0)