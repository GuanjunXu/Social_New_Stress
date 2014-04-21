#!/usr/bin/python
# coding:utf-8

from devicewrapper.android import device as d
import unittest
import commands
import re
import subprocess
import os
import string
import time
import sys
import util 
import string

AD = util.Adb()
TB = util.TouchButton()
SM = util.SetMode() 

#Written by XuGuanjun

PACKAGE_NAME  = 'com.intel.camera22'
ACTIVITY_NAME = PACKAGE_NAME + '/.Camera'

#All setting info of camera could be cat in the folder
PATH_PREF_XML  = '/data/data/com.intel.camera22/shared_prefs/'

#FDFR / GEO / BACK&FROUNT xml file in com.intelcamera22_preferences_0.xml
PATH_0XML      = PATH_PREF_XML + 'com.intel.camera22_preferences_0.xml'

#PICSIZE / EXPROSURE / TIMER / WHITEBALANCE / ISO / HITS / VIDEOSIZE in com.intel.camera22_preferences_0_0.xml
PATH_0_0XML    = PATH_PREF_XML + 'com.intel.camera22_preferences_0_0.xml'

#####                                    #####
#### Below is the specific settings' info ####
###                                        ###
##                                          ##
#                                            #

#FD/FR states check point
FDFR_STATE      = PATH_0XML   + ' | grep pref_fdfr_key'

#Geo state check point
GEO_STATE       = PATH_0XML   + ' | grep pref_camera_geo_location_key'

#Pic size state check point
PICSIZE_STATE   = PATH_0_0XML + ' | grep pref_camera_picture_size_key'

#Exposure state check point 
EXPOSURE_STATE  = PATH_0_0XML + ' | grep pref_camera_exposure_key'

#Timer state check point
TIMER_STATE     = PATH_0_0XML + ' | grep pref_camera_delay_shooting_key'

#Video Size state check point
VIDEOSIZE_STATE = PATH_0_0XML + ' | grep pref_video_quality_key'

#White balance state check point
WBALANCE_STATE  = PATH_0_0XML + ' | grep pref_camera_whitebalance_key'

#Flash state check point
FLASH_STATE     = PATH_0_0XML + ' | grep pref_camera_video_flashmode_key'

#SCENE state check point
SCENE_STATE     = PATH_0_0XML + ' | grep pref_camera_scenemode_key'

class CameraTest(unittest.TestCase):
    def setUp(self):
        super(CameraTest,self).setUp()
        #Delete all image/video files captured before
        AD.cmd('rm','/sdcard/DCIM/*')
        #Refresh media after delete files
        AD.cmd('refresh','/sdcard/DCIM/*')
        #Launch social camera
        self._launchCamera()

    def tearDown(self):
        AD.cmd('pm','com.intel.camera22') #Force reset the camera settings to default
        super(CameraTest,self).tearDown()
        self._pressBack(4)

    #case 9
    def testEnterGalleryFromGalleryPreviewThumbnail100times(self):
        '''
        Summary: enter gallery from gallery preview thumbnail 100times
        Steps  : 1.Launch single capture activity
                 2.enter gallery from gallery preview thumbnail 100times
                 3.Exit  activity
        '''
        for i in range(100):
            try:
                #If there is thumbnail on the camera preview, it is no need to take new image
                assert d(resourceId = 'com.intel.camera22:id/thumbnail').wait.exists(timeout = 5000)
            except:
                TB.takePicture('single')
                time.sleep(5) #Wait a few seconds that thumbnail could display on the preview
            finally:
                #Click on the thumbnail
                d.click(resourceId = 'com.intel.camera22:id/thumbnail').click.wait()
                #Check if gallery launch suc
                assert d(resourceId = 'com.intel.android.gallery3d:id/cardpop').wait.exists(timeout = 3000)

    #case 10
    def testCaptureSingleImage500timesBackCamera(self):
        '''
        Summary: Capture single image 500 times
        Steps  : 1.Launch single capture activity
                 2.Capture single image 500 times
                 3.Exit  activity
        '''
        for i in range(500):
            self._captureAndCheckPicCount('single',2)

    #case 11
    def testCaptureSingleImage500timesFrontCamera(self):
        '''
        Summary: Capture single image 500 times
        Steps  : 1.Launch single capture activity
                 2.Capture single image 500 times
                 3.Exit  activity
        '''
        TB.switchBackOrFrontCamera('front') #Force set camera to front
        for i in range(500):
            self._captureAndCheckPicCount('single',2)

    #case 12
    def testCaptureHdrImage500timesBackCamera(self):
        '''
        Summary: Capture hdr image 500 times
        Steps  : 1.Launch hdr capture activity
                 2.Capture hdr image 500 times
                 3.Exit  activity
        '''
        SM.switchcamera('hdr')
        for i in range(500):
            self._captureAndCheckPicCount('single',2)

    #case 13
    def testCaptureSmileImage500timesBackCamera(self):
        '''
        Summary: Capture smile image 500 times
        Steps  : 1.Launch smile capture activity
                 2.Capture smile image 500 times
                 3.Exit  activity
        '''
        SM.switchcamera('smile')
        for i in range(500):
            self._captureAndCheckPicCount('smile',2)

    #case 14
    def testRecord1080PVideo500times(self):
        '''
        Summary: test Record 1080P video 500 times
        Steps  : 1.Launch video capture activity
                 2.Record 1080P video 500 times
                 3.Exit  activity
        '''
        SM.switchcamera('video')
        for i in range(500):
            self._takeVideoAndCheckCount(30,2)

    #case 15
    def testRecordVideo500timesFrontCamera(self):
        '''
        Summary: test Record video 500 times
        Steps  : 1.Launch video capture activity
                 2.Change to front camera
                 3.Record video 500 times
                 4.Exit  activity
        '''
        SM.switchcamera('video')
        TB.switchBackOrFrontCamera('front')
        for i in range(500):
            self._takeVideoAndCheckCount(30,2)

    def _captureAndCheckPicCount(self,capturemode,delaytime):
        beforeNo = AD.cmd('ls','/sdcard/DCIM/100ANDRO') #Get count before capturing
        TB.takePicture(capturemode)
        time.sleep(delaytime) #Sleep a few seconds for file saving
        afterNo = AD.cmd('ls','/sdcard/DCIM/100ANDRO') #Get count after taking picture
        if beforeNo != afterNo - 10: #If the count does not raise up after capturing, case failed
            self.fail('Taking picture failed!')

    def _launchCamera(self):
        d.start_activity(component = ACTIVITY_NAME)
        #When it is the first time to launch camera there will be a dialog to ask user 'remember location', so need to check
        try:
            assert d(text = 'OK').wait.exists(timeout = 2000)
            d(text = 'OK').click.wait()
        except:
            pass
        assert d(resourceId = 'com.intel.camera22:id/mode_button').wait.exists(timeout = 3000), 'Launch camera failed in 3s'

    def _pressBack(self,touchtimes):
        for i in range(0,touchtimes):
            d.press('back')

    def _takeVideoAndCheckCount(self,recordtime,delaytime,capturetimes=0):
        beforeNo = AD.cmd('ls','/sdcard/DCIM/100ANDRO') #Get count before capturing
        TB.takeVideo(recordtime,capturetimes)
        time.sleep(delaytime) #Sleep a few seconds for file saving
        afterNo = AD.cmd('ls','/sdcard/DCIM/100ANDRO') #Get count after taking picture
        if beforeNo != afterNo - capturetimes - 1: #If the count does not raise up after capturing, case failed
            self.fail('Taking picture failed!')