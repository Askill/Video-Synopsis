
class Config:
    c = {
        "min_area" : 100,
        "max_area" : 900000,
        "threashold" : 7,
        "resizeWidth" : 500,
        "inputPath" : None,
        "outputPath": None,
        "maxLayerLength": 5000, 
        "minLayerLength": 40,    
        "tolerance": 20,
        "maxLength": None,
        "ttolerance": 60,
        "videoBufferLength": 450,
        "LayersPerContour": 220,
        "avgNum":10
        }

    def __init__(self):
        '''This is basically just a wrapper for a json / python dict'''
        print("Current Config:")
        for key, value in self.c.items():
            print(f"{key}:\t\t{value}")
    
    def __getitem__(self, key):
        if key not in self.c:
            return None
        return  self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value
