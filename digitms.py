# digms
import os
import cv2
from pypylon import pylon
import matplotlib.pyplot as plt
import serial
from time import sleep
import numpy as np
def camera_setting(*status):
    # input if open and exposure time (3 argument)
    # if only open don't using exposure time
    # if close == colse
    # Connect to the camera
    camera = status[0]
    if status[1] == "close":
        camera.Close()
        return None
    # Set the exposure time to 500 microseconds
    if status[1] == "open":
        camera.Open()
    else:
        return None
    try:
        camera.ExposureTime.SetValue(status[2]) # Exposure time in microseconds
    except:
        return None


def plotimage(camera):   
    # Grab a single frame
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    image = grab_result.Array

    # Display the image using matplotlib
    plt.imshow(image)
    plt.axis('off')
    plt.show()
    # Save the image
    #pylon.save_image(pylon.ImagePersistenceFormat_Png, "image.png", image)

    # Release resources
    grab_result.Release()

def capture_and_save_image(camera,name):
    # Define the output directory
    # exp is exposure time 
    documents_path = os.path.expanduser("~/Documents")
    output_dir = os.path.join(documents_path, "concept_mecha")

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Start the grabbing process
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # Create an image converter
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    # Grab an image
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grab_result)
        img = image.GetArray()

        # Define the path to save the image
        image_path = os.path.join(output_dir, name +".png")

        # Save the image using OpenCV
        cv2.imwrite(image_path, img)
        print(f"Image saved to {image_path}")
    else:
        print("Error: Image grab failed")

    # Release the grab result
    grab_result.Release()

    # Stop the grabbing process
    camera.StopGrabbing()

def sendmessage(*arg):
    ser = arg[0] # input serial port
    fullmessage = arg[1] # input list of g-code
    try:
        camera = arg [2] # input identify camera
        name = arg[3] # input is numpy of file name
    except: pass
    for k in range (len(fullmessage)):
        sleep(0.2)
        message = fullmessage[k]
        ser.write(message.encode()+b'\r\n')
        sleep(0.1)
        try:
            if name[k] != 'er':
                sleep(1.0)
                capture_and_save_image(camera,name[k])
        except:pass
def live_video(camera):
    # Image format converter to convert to OpenCV format
    camera_setting(camera,"open",150)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    # Start grabbing continuously with the fastest frame rate
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    # Display live video
    while camera.IsGrabbing():
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            # Convert the image to OpenCV format
            image = converter.Convert(grab_result)
            img = image.GetArray()

            # Display the image using OpenCV
            cv2.imshow('Live Video', img)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        grab_result.Release()

    # Release resources
    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()
