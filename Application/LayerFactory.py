from Application.Layer import Layer
from Application.Config import Config
from Application.VideoReader import VideoReader
from Application.Exporter import Exporter
from multiprocessing.pool import ThreadPool
import cv2
import numpy as np
import copy

class LayerFactory:
    def __init__(self, config, data=None):
        self.data = {}
        self.layers = []
        self.tolerance = config["tolerance"]
        self.ttolerance = config["ttolerance"]
        self.minLayerLength = config["minLayerLength"]
        self.maxLayerLength = config["maxLayerLength"]
        self.resizeWidth = config["resizeWidth"]
        self.footagePath = config["inputPath"]
        self.config = config
        print("LayerFactory constructed")
        self.data = data
        if data is not None:
            self.extractLayers(data)

    def extractLayers(self, data = None):
        '''Bundle given contours together into Layer Objects'''
        if self.data is None:
            if data is None or len(data) == 0 :
                print("LayerFactory data was none")
                return None
            else:
                self.data = data

        frameNumber = min(data)
        contours = data[frameNumber]
        for contour in contours:
            self.layers.append(Layer(frameNumber, contour, self.config))
  
        self.oldLayerIDs = []
        
        with ThreadPool(16) as pool:
            for frameNumber in sorted(data.keys()):
                contours = data[frameNumber]
                if frameNumber%5000 == 0:
                    print(f"{int(round(frameNumber/max(data.keys()), 2)*100)}% done with Layer extraction")

                tmp = [[frameNumber, contour] for contour in contours]
                #pool.map(self.getLayers, tmp)
                for x in tmp:
                    self.getLayers(x)

        return self.layers

    def getLayers(self, data):
        frameNumber = data[0]
        bounds = data[1]
        (x,y,w,h) = bounds
        tol = self.tolerance
        foundLayer = 0
        #to merge layers
        foundLayerIDs = []

        for i in range(0, len(self.layers)):
            if foundLayer >= self.config["LayersPerContour"]:
                break
            
            if i in self.oldLayerIDs:
                continue
            if frameNumber - self.layers[i].lastFrame > self.ttolerance:
                self.oldLayerIDs.append(i)
                continue
            
            lastXframes = 3
            if len(self.layers[i].bounds) < lastXframes:
                lastXframes = len(self.layers[i].bounds)
            lastBounds = [bound for bounds in self.layers[i].bounds[-lastXframes:] for bound in bounds]

            for bounds in lastBounds:
                if bounds is None:
                    break
                (x2,y2,w2,h2) = bounds
                if self.contoursOverlay((x-tol,y+h+tol), (x+w+tol,y-tol), (x2,y2+h2), (x2+w2,y2)):
                    self.layers[i].add(frameNumber, (x,y,w,h))
                    foundLayer += 1
                    foundLayerIDs.append(i)
                    break

        if foundLayer == 0:
            self.layers.append(Layer(frameNumber, (x,y,w,h), self.config))

        if len(foundLayerIDs) > 1:
            self.mergeLayers(foundLayerIDs)

    def mergeLayers(self, foundLayerIDs):
        
        layers = self.sortLayers(foundLayerIDs)
        layer1 = layers[0]
        for layerID in range(1, len(layers)):
            layer2 = layers[layerID]
            layer1 = self.merge2Layers(layer1, layer2)
        
        self.layers[foundLayerIDs[0]] = layer1

        layers = []
        for i, layer in enumerate(self.layers):
            if i not in foundLayerIDs[1:]:
                layers.append(layer)
        self.layers = layers
        
            
    def merge2Layers(self, layer1, layer2):
        """Merges 2 Layers, Layer1 must start before Layer2"""
        
        dSF = layer2.startFrame - layer1.startFrame
        l1bounds = copy.deepcopy(layer1.bounds)

        for i in range(len(layer2.bounds)):
            bounds = layer2.bounds[i]
            while dSF + i >= len(l1bounds):
                l1bounds.append([])
            for bound in bounds:
                if bound not in l1bounds[dSF + i]: 
                    l1bounds[dSF + i].append(bound)

        layer1.bounds = l1bounds
        return layer1


    def contoursOverlay(self, l1, r1, l2, r2): 
        # If one rectangle is on left side of other 
        if(l1[0] >= r2[0] or l2[0] >= r1[0]): 
            return False
        # If one rectangle is above other 
        if(l1[1] <= r2[1] or l2[1] <= r1[1]): 
            return False
        return True

    def sortLayers(self, foundLayerIDs):
        layers = []
        for layerID in foundLayerIDs:
            layers.append(self.layers[layerID])
        
        layers.sort(key = lambda c:c.startFrame)
        return layers