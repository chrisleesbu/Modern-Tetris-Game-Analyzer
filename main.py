from mss.windows import MSS as mss
import cv2
from mode.capture_image import image_mode
from mode.capture_video import video_mode

MODE = {
    # Image
    "IMAGE": False, # Uses an image as the source
    "IMAGE_SRC": "test/tsd.png", # Source of image
    "DISPLAY_IMAGE" : True, # Displays the image

    # Video
    "VIDEO": True, # Uses a video as the source
    "VIDEO_SRC" : "test/tspin.mp4", # Source of video
    "DISPLAY_VIDEO" : True, # Displays the video

    # Frame from Video
    "FRAME_FROM_VIDEO": False, # Grabs a specific frame from a video
    "FRAME_SRC" : "test/tspin.mp4", # Source of video
    "FRAME_NUMBER" : 200, # Frame number
    "DISPLAY_FRAME": True, # Displays the frame

    # Screen Capture
    "SCREEN_CAPTURE": False, # Uses your screen as the source
}

sumModes = int(MODE["IMAGE"]) + int(MODE["VIDEO"]) + int(MODE["FRAME_FROM_VIDEO"]) + int(MODE["SCREEN_CAPTURE"])
if (sumModes == 0):
    print("Select one input mode")
    quit()
if (sumModes != 1):
    print("Only one input mode can be active at a time")
    quit()

if MODE["IMAGE"]:
    image_mode(MODE["IMAGE_SRC"], MODE["DISPLAY_IMAGE"])
elif MODE["VIDEO"]:
    video_mode(MODE["VIDEO_SRC"], MODE["DISPLAY_VIDEO"])
elif MODE["FRAME_FROM_VIDEO"]:
    vCapture = cv2.VideoCapture(MODE["FRAME_SRC"])
    vCapture.set(cv2.CAP_PROP_POS_FRAMES, MODE["FRAME_NUMBER"])
    res, image = vCapture.read()
    if (res == False):
        print("Unable to get frame from video (Make sure frame number is valid)")
        quit()
    image_mode(image, MODE["DISPLAY_FRAME"])

"""
ASSUMPTIONS
1. TRADITIONAL COLOR MUST BE ON
2. AT LEAST 2 PIECES IN THE NEXT QUEUE
"""
