from locationInfo import *
from boardReader import *
from lineClears import *

DEBUG = {
    "BOARD_STATE": False, # Prints out the board state
    "NEXT_PIECE": False, # Prints out the next pieces 
    "PIECE_HELD": False, # Prints out if a piece has been held
    "ZONE_DIGIT_OCCURANCE": False, # Prints out zone attack
    "SAVE_VIDEO": False # Saves video with APM
}

def video_mode(src, isDisplay):
    video = cv2.VideoCapture(src)
    fps = video.get(cv2.CAP_PROP_FPS)

    if DEBUG["SAVE_VIDEO"]:
        cap = cv2.VideoCapture(0)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('outputNoAudio.mp4', fourcc, fps, (width, height))

    # NOTE: KNOWING THE BOARD LOCATION BEFOREHAND SIGNFICIANTLY INCREASES SPEED OF THE PROGRAM
    # Board Location
    boardLocation = None
    # For APM
    gameInProgress = False
    gameFinished = False
    inGameFrameCount = 0
    attackPerMinute = 0
    # Current Piece
    prevPiece, currentPiece = 'X', 'X'
    # Next Queue (T Piece Storage)
    nextQueue = ['X', 'X', 'X', 'X']
    prevTLocations, tLocations = [], []
    # Hold Piece
    holdPiece = 'X'
    # Board State
    prevBoardState, boardState = None, None
    # Combo
    combo = 0
    # TSpin Detection 
    tSpinType = None
    tSpinLastFrame = 0
    # Mini Detection 
    miniDetected = False
    miniLastFrame = 0
    # Zone Variables
    zoneActive = False
    zoneActiveFrames = 0
    framesSinceZoneEnded = 0
    # Zone Attack Variables
    doubleLeftDigitOccurance = np.zeros(10, int)
    doubleRightDigitOccurance = np.zeros(10, int)
    singleDigitOccurance = np.zeros(10, int)
    # MISC
    frameCount = 0

    if (video.isOpened()== False): 
        print("Error opening video file") 

    while (video.isOpened()): 
        ret, frame = video.read() 
        if ret == True: 

            #If board location is not found,  locate the board
            if (boardLocation is None):
                newBoardLocation = np.array([614,291,390,780])
                # newBoardLocation = locate_board(frame)

                # If the function successfully finds the board, pre-calculate location of all features
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

            #If board location is found
            else:
                # Store previous board state in temporary variables
                prevQueue = nextQueue.copy()
                prevHold = holdPiece
                prevBoardState = boardState
                prevPiece = currentPiece
                lineType = None

                # Get the next 4 pieces
                nextQueue[0] = get_next_piece(next1Location, frame)
                nextQueue[1] = get_next_piece(next2Location, frame)
                nextQueue[2] = get_next_piece(next3Location, frame)
                nextQueue[3] = get_next_piece(next4Location, frame)

                # Get the hold piece
                holdPiece = get_hold_piece(holdLocation, frame)
                if (prevHold != holdPiece):
                    currentPiece = prevHold
                    if DEBUG["PIECE_HELD"]:
                        print("Frame " + str(frameCount))
                        print("Piece held!")
                        print("Current: " + currentPiece)
                        print()

                # Check if zone is active or not
                zoneDetection = detect_zone(zoneLocation, frame)
                if (zoneDetection == True):
                    if (zoneActiveFrames < fps):
                        zoneActiveFrames += 1
                        if (zoneActive == False and zoneActiveFrames >= (fps/2)):
                            print("Frame " + str(frameCount) + ": ZONE ACTIVE")
                else:
                    if (zoneActiveFrames > 0):
                        zoneActiveFrames -= 1
                        if (zoneActive == True and zoneActiveFrames < (fps/2)):
                            print("Frame " + str(frameCount) + ": ZONE INACTIVE")
                            framesSinceZoneEnded = fps*1 # 0.5 Seconds

                    
                if (zoneActiveFrames >= (fps/2)):
                    zoneActive = True
                else:
                    zoneActive = False

                if (framesSinceZoneEnded > 0):
                    doubleLeftDigit = identify_atk_digit(atkDblLeftLocation, frame)
                    if (doubleLeftDigit != -1):
                        doubleLeftDigitOccurance[doubleLeftDigit] += 1
                    doubleRightDigit = identify_atk_digit(atkDblRightLocation, frame)
                    if (doubleRightDigit != -1):
                        doubleRightDigitOccurance[doubleRightDigit] += 1
                    singleDigit = identify_atk_digit(atkSingleLocation, frame)
                    if (singleDigit != -1):
                        singleDigitOccurance[doubleLeftDigit] += 1

                    framesSinceZoneEnded -= 1
                    if (framesSinceZoneEnded == 0):
                        zoneAttack = 0

                        singleDigitIndexMax = np.argmax(singleDigitOccurance)
                        doubleLeftDigitIndexMax = np.argmax(doubleLeftDigitOccurance)
                        doubleRightDigitIndexMax = np.argmax(doubleRightDigitOccurance)
                        # Check if it was a single digit 
                        if (singleDigitOccurance[singleDigitIndexMax] > round(fps/6)) and singleDigitIndexMax > doubleLeftDigitIndexMax and singleDigitIndexMax > doubleRightDigitIndexMax:
                            zoneAttack = np.argmax(singleDigitOccurance)

                        # Else assume it was two digits
                        else:

                            # If the tens digit is not confident, don't bother adding attack
                            if (doubleLeftDigitOccurance[doubleLeftDigitIndexMax] < round(fps/12)):
                                zoneAttack = -1
                            else:
                                zoneAttack += doubleLeftDigitIndexMax * 10
                                if (doubleRightDigitOccurance[doubleRightDigitIndexMax] > round(fps/12)):
                                    zoneAttack += doubleRightDigitIndexMax

                        if DEBUG["ZONE_DIGIT_OCCURANCE"]:
                            print(doubleLeftDigitOccurance)
                            print(doubleRightDigitOccurance)
                            print(singleDigitOccurance)

                        doubleLeftDigitOccurance = np.zeros(10, int)
                        doubleRightDigitOccurance = np.zeros(10, int)
                        singleDigitOccurance = np.zeros(10, int)

                        if (zoneAttack != -1):
                            print("Frame " + str(frameCount) + " ZONE ATTACK: " + str(zoneAttack))
                            add_Attack_Total(zoneAttack)

                # Check for Mini
                # 1.5 Seconds of Cooldown
                if (zoneActive == False and (miniLastFrame == 0 or frameCount - miniLastFrame > (fps*1.5))):
                    miniDetected = detect_mini(miniIndicatorLocation, frame)
                    if miniDetected is True:
                        miniLastFrame = frameCount
                        storeMini(miniLastFrame)   
                
                # Check for TSpin Type by checking SI[N]GLE, DO[U]BLE, T[RI]PLE
                # 1.5 Seconds of Cooldown
                if (zoneActive == False and (tSpinLastFrame == 0 or frameCount - tSpinLastFrame > (fps*1.5))) :
                    tSpinType = identify_tspin_type(tSpinIndicatorLocation, frame)
                    if tSpinType is not None:
                        tSpinLastFrame = frameCount
                        storeTSpinAttack(tSpinLastFrame, tSpinType)  

                # If the previous two pieces are both different from the next two pieces, this means a piece was placed, therefore updating the board state
                if (zoneActive == False and (prevQueue[0] != nextQueue[0] or prevQueue[1] != nextQueue[1] or prevQueue[2] != nextQueue[2])):

                    if (('X' not in nextQueue) and ('?' not in nextQueue)):
                        gameInProgress = True
                    if (nextQueue == ['?', '?', '?', '?'] and holdPiece == '?'):
                        gameInProgress = False

                    boardState = scan_board(boardLocation,frame)

                    # Compare previous locations of T piece, Used to check if the current piece is a T piece
                    prevTLocations = tLocations
                    tLocations = [index for index, type in enumerate(nextQueue) if type =='T']

                    if (0 in prevTLocations):
                        currentPiece = 'T'
                    else:
                        currentPiece = "Not T"
                    
                    if (prevBoardState is not None):
                        lineType = calculateLineType(prevBoardState, boardState)

                        if (lineType is not None):
                            addLineType(frameCount, lineType, prevPiece, combo)
                            combo += 1
                        else:
                            combo = 0

                    # Information about current frame
                    # print("Frame " + str(frameCount))
                    # print("Current: " + currentPiece)
                    
                    if DEBUG["NEXT_PIECE"]:   
                        print("Next: " + nextQueue[0] + " " + nextQueue[1] + " " + nextQueue[2] + " " + nextQueue[3])

                    if DEBUG["BOARD_STATE"]:        
                        print(boardState)

                if (gameInProgress == True):
                    inGameFrameCount += 1

                if (inGameFrameCount != 0):
                    attackPerMinute = str(round((get_Attack_Total()/(inGameFrameCount/fps)) * 60,2))
                    cv2.putText(frame, text="APM", org=textAPMDisplayLocation, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.95, color=(255,255,255), thickness=2, lineType=cv2.LINE_AA)
                    cv2.putText(frame, text=attackPerMinute, org=actualAPMDisplayLocation, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1.45, color=(255,255,255), thickness=2, lineType=cv2.LINE_AA)

                if isDisplay:
                    cv2.imshow('Frame', frame) 

                if DEBUG["SAVE_VIDEO"]:
                    out.write(frame)

            # Press Q on keyboard to exit 
            if cv2.waitKey(25) & 0xFF == ord('q'): 
                break
        else: 
            break
        frameCount += 1

    video.release() 
    if DEBUG["SAVE_VIDEO"]:
        cap.release()
        out.release()
    cv2.destroyAllWindows() 