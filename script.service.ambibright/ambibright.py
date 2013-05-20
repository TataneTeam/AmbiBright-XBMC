import os
import time
import sys
import xbmc
import xbmcaddon
import xbmcgui


__addon__ = xbmcaddon.Addon()
__cwd__ = __addon__.getAddonInfo('path')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')

__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))

sys.path.append(__resource__)

import serial


def debug(msg):
    xbmc.log("### [%s] - %s" % (__scriptname__, msg,), level=xbmc.LOGDEBUG)


def info(msg):
    xbmc.log("### [%s] - %s" % (__scriptname__, msg,), level=xbmc.LOGNOTICE)


def displayNotification(msg):
    xbmc.executebuiltin('Notification("' + __scriptname__ + '","' + str(msg) + '")')


class CapturePlayer(xbmc.Player):
    def __init__(self):
        self.window = xbmcgui.Window()
        self.arduino = serial.Serial('COM3', 115200)
        self.nbLedTop = 24
        self.nbLedSide = 14
        self.nbLedTotal = 24 + 14 * 2 - 2
        self.data = bytearray(6 + self.nbLedTotal * 3)
        self.data[0] = 'A'
        self.data[1] = 'd'
        self.data[2] = 'a'
        self.data[3] = (self.nbLedTotal - 1) >> 8
        self.data[4] = (self.nbLedTotal - 1) & 0xff
        self.data[5] = (self.data[3] ^ self.data[4] ^ 0x55)

    def onPlayBackStarted(self):
        if self.isPlayingVideo():
        #            fullWidth = self.window.getWidth()
        #            fullHeight = self.window.getHeight()

            capture = xbmc.RenderCapture()
            #            capture.capture(256, 256, xbmc.CAPTURE_FLAG_IMMEDIATELY)
            #            capture.waitForCaptureStateChangeEvent(100)
            #
            #            fmt = capture.getImageFormat()
            #            aspectRatio = capture.getAspectRatio()
            #
            #            width = fullWidth / aspectRatio
            #            height = fullHeight
            #
            #            if width < height:
            #                height = width
            #                width = fullWidth
            #
            #            displayNotification("%s => %dx%d" % (aspectRatio, width, height))

            capture.capture(self.nbLedTop, self.nbLedSide, xbmc.CAPTURE_FLAG_CONTINUOUS)
            fmt = capture.getImageFormat()
            #            start = int(round(time.time() * 1000))
            #            count = 0
            while self.isPlayingVideo():
                capture.waitForCaptureStateChangeEvent(100)
                if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
                    # count += 1
                    img = capture.getImage()

                    i = 6

                    # left side
                    x = 0
                    y = self.nbLedSide - 1
                    while y >= 0:
                        pos = y * self.nbLedTop * 4 + x * 4
                        if fmt == 'RGBA':
                            self.data[i] = img[pos]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos + 2]
                        else:
                            self.data[i] = img[pos + 2]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos]
                        i += 3
                        y -= 1

                    # top
                    x = 1
                    y = 0
                    while x < (self.nbLedTop - 1):
                        pos = y * self.nbLedTop * 4 + x * 4
                        if fmt == 'RGBA':
                            self.data[i] = img[pos]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos + 2]
                        else:
                            self.data[i] = img[pos + 2]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos]
                        i += 3
                        x += 1

                    # right side
                    x = self.nbLedTop - 1
                    y = 0
                    while y < self.nbLedSide:
                        pos = y * self.nbLedTop * 4 + x * 4
                        if fmt == 'RGBA':
                            self.data[i] = img[pos]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos + 2]
                        else:
                            self.data[i] = img[pos + 2]
                            self.data[i + 1] = img[pos + 1]
                            self.data[i + 2] = img[pos]
                        i += 3
                        y += 1

                    self.arduino.write(self.data)

            #            end = int(round(time.time() * 1000))
            #            displayNotification("Video captured : %d ms average time li" % ((end - start) / count))

    def close(self):
        self.arduino.close()

player = CapturePlayer()
while not xbmc.abortRequested:
    xbmc.sleep(1000)
player.close()
player = None
