import numpy as np
from scipy import signal as sg
import cv2
from matplotlib import pyplot as plt

class segmenter():
	"""Segments page as a precursor to OCR process"""

	def __init__(self,image,pim):
		self.__image = image
		self.__width = np.shape(image)[1]
		self.__height = np.shape(image)[0]
		self.__pim = pim
		self.__threshold = 15
		self.__slack = 5
		self.getSegments()

	def displaySegments(self):
		if not hasattr(self, '__segments'):
			self.getSegments()
		for segment in self.__segments:
			top, bottom = segment
			cv2.line(self.__image, (0,top), (self.__width,top), (0,0,255), 1)
			cv2.line(self.__image, (0,bottom), (self.__width,bottom), (0,0,255), 1)
		plt.imshow(self.__image)
		plt.show()

	def getSegments(self):
		if hasattr(self, '__segments'):
			return self.__segments
		hist = np.sum(self.__pim,1)
		smhist = sg.medfilt(hist,21)
		diffhist = np.diff(smhist)
		peaks = self.getPeaks(diffhist)
		peaks = self.mergeNearbyPeaks(peaks)
		self.__segments = [(peaks[i-1],peaks[i]+self.__slack) for i in range(1,len(peaks))]
		self.__segments.insert(0,(0,peaks[0]+self.__slack))
		self.__segments.append((peaks[-1],self.__height))
		return self.__segments

	def getPeaks(self,diffhist):
		peaks = [i for i in range(1,len(diffhist)-2) \
					if diffhist[i-1] < diffhist[i] \
					and diffhist[i+1] < diffhist[i] \
					and diffhist[i] > 255*10]
		mergedPeaks = self.mergeNearbyPeaks(peaks)
		return mergedPeaks

	def mergeNearbyPeaks(self,peaks):
		mergedPeaks = [peaks[i-1] for i in range(1,len(peaks)) \
							if peaks[i]-peaks[i-1] > self.__threshold]
		mergedPeaks.append(peaks[i])
		return mergedPeaks