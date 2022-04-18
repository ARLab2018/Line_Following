#!/usr/bin/env python

import rospy
import cv2
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import sys

bridge = CvBridge()

hsvVals = [0, 0, 117, 179, 22, 219] #HSV Color Space
sensors = 5  #Number of senors(Hypothetical)
threshold = 0.1 #Sensitivity of Color detection
Kernel_size=15


  #from now on, you can work exactly like with opencv
  #(rows,cols,channels) = cv_image.shape
 # if cols > 200 and rows > 200 :
 #     cv2.circle(cv_image, (100,100),90, 255)
 # font = cv2.FONT_HERSHEY_SIMPLEX
 # cv2.putText(cv_image,'Webcam Activated with ROS & OpenCV!',(10,350), font, 1,(255,255,255),2,cv2.LINE_AA)
 # cv2.imshow("Image window", cv_image)
 # cv2.waitKey(3)


def image_callback(ros_image):
  #print ('got an image')
  global bridge
  #convert ros_image into an opencv-compatible image
  try:
    img = bridge.imgmsg_to_cv2(ros_image, "bgr8")
  except CvBridgeError as e:
      print(e)
  #while True:
      #_, img = cap.read()



  def thresholding( img ):                                       #Creates an HSV mask over the live feed
	  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	  blurred = cv2.GaussianBlur(img, (Kernel_size, Kernel_size), 0)
	  hsv = cv2.cvtColor( blurred, cv2.COLOR_BGR2HSV )
      #hsv = cv2.cvtColor( img, cv2.COLOR_BGR2HSV )
	  lower = np.array( [hsvVals[0], hsvVals[1], hsvVals[2]] )
	  upper = np.array( [hsvVals[3], hsvVals[4], hsvVals[5]] )
	  mask = cv2.inRange( hsv, lower, upper )
	  return mask

  def getContours( imgThres, img ):                             #Forms a contour around the largest visible(White) patch
	  contours, heirarchy = cv2.findContours( imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE )
	  biggest = max( contours, key=cv2.contourArea )
	  x, y, w, h = cv2.boundingRect( biggest )
	  cx = x + w // 2
	  cy = y + h // 2
	  cv2.drawContours( img, biggest, -1, (255, 255, 0), 5 )
	  cv2.circle( img, (cx, cy), 5, (0, 128, 255), cv2.FILLED )

  
  def droneOutput(senOut):                                      #Gives Commands to drone
	  if senOut==[0,1,1,1,0] :
		  return 'Move Forward'
	  if senOut==[0,1,1,1,1] :
	  	  return  'Move Slight Right'
	  if senOut==[1,1,1,1,0] :
		  return  'Move Sligth Left'
	  if senOut==[1,1,1,0,0] or senOut==[0,1,1,0,0] :
		  return  'Move Left'
	  if senOut==[0,0,1,1,1] or senOut==[0,0,1,1,0] :
		  return  'Move Right'
	  if senOut==[0,0,0,1,1] :
		  return  'Rotate Right'
	  if senOut==[1,1,0,0,0] :
		  return  'Rotate Left'
	  else :
		  return 'Stop'

  def getSensorOutput( imgThres, sensor ):                      #Senses the position of the drone along the path
	  imgs = np.hsplit( imgThres, sensor )
	  totalPixels = (img.shape[1] // sensor) * img.shape[0]
	  senOut = []
	  for x, im in enumerate( imgs ):
		  pixelCount = cv2.countNonZero( im )
		  if pixelCount > threshold * totalPixels:
			  senOut.append( 1 )
		  else:
			  senOut.append( 0 )
		  cv2.imshow( str( x ), im )
	  print( senOut )
	  return senOut

  img = cv2.resize( img, (480, 360) )
  #img = cv2.flip( img, 1 )
  imgThres = thresholding( img )
  cx = getContours( imgThres, img )  # Translation
  senOut = getSensorOutput( imgThres, sensors )
  cv2.imshow( "Output", img )
  cv2.imshow( "Path", imgThres )
  print(droneOutput(senOut))
  cv2.waitKey( 10 )


def main(args):
  rospy.init_node('image_converter', anonymous=True)
  #for turtlebot3 waffle
  #image_topic="/camera/rgb/image_raw/compressed"
  #for usb cam
  #image_topic="/usb_cam/image_raw"

  #image_sub = rospy.Subscriber("/usb_cam/image_raw",Image, image_callback)
  image_sub = rospy.Subscriber("/plutocamera/image_raw",Image, image_callback)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)