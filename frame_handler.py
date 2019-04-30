import time
import cv2
import numpy as np
from PIL import Image, ImageTk

hQ = (640, 480)
mQ = (320, 240)
lQ = (160, 120)
class FrameHandler:
    def __init__(self):
        self.fps = 30
        self.res = "HIGH"
        self.ratio = 50
        self.order = 0

    def prepareFrame(self, frame):
        message = str(self.order)+'#'+str(time.time())+'#'+self.res+'#'+str(self.fps)+'#'
        message = message.encode('ascii')
        frame = self.resizeFrame(frame)
        guiFrame = self.frameFormat(frame)
        inetFrame = self.compress(frame)
        if inetFrame is None:
            return None
        self.order += 1
        return message+inetFrame, guiFrame

    def resizeFrame(self, frame):
        if self.res == "HIGH":
            return cv2.resize(frame, hQ)
        if self.res == "MEDIUM":
            return cv2.resize(frame, mQ)
        if self.res == "LOW":
            return cv2.resize(frame, lQ)
        return None

    def frameFormat(self, frame):
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(Image.fromarray(cv2_im))

    def inet2GUI(self, inetFrame):
        frame = self.decompress(inetFrame)
        return self.frameFormat(frame)

    def compress(self, frame):
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.ratio]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)
        if result == False:
            return None
        return encimg.tobytes()

    def decompress(self, frame):
        return cv2.imdecode(np.frombuffer(frame,np.uint8),1)

    def updateFps(self, fps):
        self.fps = fps

    def updateRatio(self, ratio):
        self.ratio = ratio

    def resetCount(self):
        self.order = 0
