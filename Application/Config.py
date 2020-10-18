
class Config:
    c = {
        "min_area" : 500,
        "max_area" : 40000,
        "threashold" : 10,
        "resizeWidth" : 512,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 900, 
        "minLayerLength": 20,    
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 1000,
        "noiseThreashold": 0.2,
        "noiseSensitivity": 3/4
        }

    def __init__(self):
        print("Current Config:", self.c)
    
    def __getitem__(self, key):
        if key not in self.c:
            return None
        return  self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
