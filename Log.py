import sys
import os

class Log:
    dirname = "logs"
    
    def __init__(self, filename):
        if not os.path.exists(Log.dirname):
            os.makedirs(Log.dirname)
        fullFilename = os.path.join(Log.dirname, filename)
        if os.path.exists(fullFilename):
            os.remove(fullFilename)
        self.f = open(fullFilename, 'a')
        
    def log(self, text):
        self.f.write(text + "\n")
    
    def close(self):
        self.f.close()
        
