# Zone Battle Real-Time APM

Python application that uses image processing techniques to calculate the APM (attack per minute) in a recorded or real-time match of Zone Battle in Tetris® Effect: Connected. 

<img width="171" alt="figure3" src="https://github.com/user-attachments/assets/bd8c451e-d40a-450a-b744-400c212b0c8d">

## Demonstration
<video src="https://github.com/user-attachments/assets/b08b3a65-1753-4c24-9639-9019e0c2cc71"></video>
![figure1](https://github.com/user-attachments/assets/d7f09caf-b6cb-4759-b69c-ace1f40fdaf1)
![figure2](https://github.com/user-attachments/assets/3505fd8d-7ea2-43da-9666-01857763e29a)

## REQUISITES
For best results, the game needs to meet the following conditions:
1. Tetrimino colors: Traditional
2. Next Queue: at least 2, supports up to 4
3. Camera zoom must remain the same for the entire duration of the match.

## Directory Structure

### main.py
Run this file to start the program. Contains code to change the capture mode to either image, frame from video, video, or screen.

### locationInfo.py
Pre-calculate the locations that need to be analyzed. 

### lineClears.py
Determines what type of line clear was performed. 

### boardReader.py
Analyzes frame-by-frame for the following infomation:  
* Board Location
* Board State (Determining which parts of the board are filled or not)
* Piece Recognition (Used for the next/hold queue)
* TSpin Type (Determines what type of T-Spin was cleared) 
* TSpin-Mini Detection (Determines if the T-Spin was mini or not)
* Zone Detection (Determines if the player is in zone or not)
* Zone Attack Detection (Reads *number* ATTACK after zone ends)

### attackData.py
Calculates amount of attack sent based on the line type, combo, and back-to-back bonus.

### pieceInformation.py
Contains numpy array variables that visually correspond to certain game elements.

### mode/capture_image.py
Code used when the capture mode is set to image or frame from video.

### mode/capture_screen.py (UNFINISHED)
Code used when the capture mode is set to screen capture. 

### mode/capture_video.py
Code used when the capture mode is set to video. 

## Future Plans
* APM Calculation for both players
* AI Implementation for more reliability 
* Rewrite the program in C to increase performance 