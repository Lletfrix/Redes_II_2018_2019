import time
import cv2

class FrameHandler:
    def __init__(self, quality):
        self.fps = 30
        self.res = "HIGH"
        self.ratio = 50
        self.order = 0

    def prepareFrame(self, frame):
        message = str(self.order)+'#'+str(time.time())+'#'+self.res+'#'+str(self.fps)+'#'
        bytes_frame = self.compress(self, frame)
        if bytes_frame is None:
            return None
        self.order = self.order + 1
        return message+bytes_frame

    def disectFrame(self, frame):
        attr = frame.split('#')
        attr[-1] = self.decompress(self, attr[-1])
        return attr

    def compress(self, frame):
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.ratio]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)
        if encimg == False:
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
