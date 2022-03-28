from statistics import linear_regression
import numpy as np
from PIL import Image
import sys
from pathlib import Path
import os
import math

PATH = Path(sys.argv[1])
tileSize = int(sys.argv[2])

designDBUs = {
	"8t1" : ((0, 390800), (0, 383040)),
	"8t2" : ((0, 1301600), (0, 1148360)),
	"8t3" : ((0, 1977170), (0, 1410020)),
	"8t4" : ((0, 1777200), (0, 1210000)),
	"8t5" : ((0, 1857000), (0, 1840000)),
	"8t6" : ((0, 1715200), (0, 1062400)),
	"8t7" : ((0, 2716400), (0, 2650880)),
	"8t8" : ((0, 2716400), (0, 2650880)),
	"8t9" : ((0, 1820000), (0, 1568800)),
	"8t10" : ((0, 1820000), (0, 1568800)),
	"9t1" : ((0, 296800), (0, 292000)),
	"9t2" : ((0, 1745600), (0, 1178400)),
	"9t3" : ((0, 390600), (0, 390000)),
	"9t4" : ((-2000, 1602000), (-2000, 1552000)),
	"9t5" : ((0, 906000), (0, 906000)),
	"9t6" : ((0, 2716400), (0, 2650880)),
	"9t7" : ((0, 3161400), (0, 3033600)),
	"9t8" : (),
	"9t9" : (),
	"9t10" : ()
}

grSizes = {
	"8t1" : (80, 80)
}


def getCongMapChannel(dir, rule, gridSize, value):
	print(rule)
	vios = []
	designName = str(dir).split("/")[-1]
	# print("Get " + rule + " of: " + str(dir))
	longName = "ispd1" + designName.split('t')[0] + "_test" + designName.split("t")[1] + ".solution.def"
	fileName = longName + "." + rule
	file = open(os.path.join(dir, fileName))
	logName = "ispd1" + designName.split('t')[0] + "_test" + designName.split("t")[1] + ".log"
	logFile = open(os.path.join(dir, logName))
	logLines = logFile.readlines()
	logLineStart = 0
	while logLines[logLineStart][11:16] != "METAL":
		logLineStart += 1
	logLineStart += 1
	layer = 0
	# trackStart = 0
	# trackPitch = 0
	# cpStart = 0
	# cpPitch = 0
	direction = 'X'
	channel = np.zeros(gridSize)
	while True:
		line = file.readline()
		if not line:
			break
		if (line[0:5] == "Layer"):
			layer = int(line[6])
			trackNum = int(logLines[logLineStart+layer].split('), crossPts=(locs=')[0].split(',#=')[1])
			# trackStart = int(logLines[logLineStart+layer].split('-')[0].split('=')[-1])
			# trackPitch = int(logLines[logLineStart+layer].split('pitch=')[1].split(',')[0])
			# cpStart = int(logLines[logLineStart+layer].split('crossPts=(locs=')[1].split('-')[0])
			# cpEnd = int(logLines[logLineStart+layer].split('crossPts=(locs=')[1].split('-')[1].split(',#=')[0])
			cpNum = int(logLines[logLineStart+layer].split(',#=')[-1].split('), #grids=')[0])
			# cpPitch = (cpEnd - cpStart) / (cpNum - 1)
			direction = logLines[logLineStart+layer][23]
			continue
		# trackDBU = int(line.split(" ")[0]) * trackPitch + trackStart
		# cpDBU = int(line.split(" ")[1]) * cpPitch + cpStart
		# if (direction == 'X'):
		# 	vios.append([layer, trackDBU, cpDBU])
		# else:
		# 	vios.append([layer, cpDBU, trackDBU])
		trackId = int(line.split(" ")[0])
		cpId = int(line.split(" ")[1])
		if (direction == 'X'):
			channel[int(trackId//math.ceil(trackNum/gridSize[0]))][int(cpId//math.ceil(cpNum/gridSize[1]))] = value
		else:
			channel[int(cpId//math.ceil(cpNum/gridSize[0]))][int(trackId//math.ceil(trackNum/gridSize[1]))] = value
	file.close()
	logFile.close()
	return channel
		
def getFeatsInDBU(dir, feature):
	designName = str(dir).split("/")[-1]
	# print("Get " + feature + " of: " + str(dir))
	longName = "ispd1" + designName.split('t')[0] + "_test" + designName.split("t")[1] + ".solution.def"
	fileName = longName + "." + feature
	file = open(os.path.join(dir, fileName))
	res = []
	lineList = file.read().splitlines()
	for line in lineList:
		lineSplit = line.split(" ")
		layer = int(lineSplit[0])
		lx = int(lineSplit[1])
		hx = int(lineSplit[2])
		ly = int(lineSplit[3])
		hy = int(lineSplit[4])
		res.append([layer, lx, hx, ly, hy])
	file.close()
	return res


def generateHyperImg(dir, netPins, obs, unUsedPins):
	# TODO: the channel of obs???
	designName = str(dir).split("/")[-1]
	sizeDBU = designDBUs[designName]
	xSizeDBU = sizeDBU[0][1] - sizeDBU[0][0]
	ySizeDBU = sizeDBU[1][1] - sizeDBU[1][0]
	grSize = (math.ceil(xSizeDBU / tileSize), math.ceil(ySizeDBU / tileSize))
	print('Generating hyper image of %s, size: %d x %d' % (designName, grSize[0], grSize[1]))
	image = np.zeros((9, grSize[0], grSize[1]))
	for pinBox in netPins:
		for i in range(pinBox[1] // tileSize, int(pinBox[2] / tileSize) if pinBox[2] % tileSize == 0 else int(pinBox[2] / tileSize) + 1):
			for j in range(pinBox[3] // tileSize, pinBox[4] // tileSize):
				image[pinBox[0]][i][j] = 1
	for pinBox in obs:
		for i in range(pinBox[1] // tileSize, int(pinBox[2] / tileSize) if pinBox[2] % tileSize == 0 else int(pinBox[2] / tileSize) + 1):
			for j in range(pinBox[3] // tileSize, pinBox[4] // tileSize + 1):
				image[pinBox[0]][i][j] = 2
	for pinBox in unUsedPins:
		for i in range(pinBox[1] // tileSize, int(pinBox[2] / tileSize) if pinBox[2] % tileSize == 0 else int(pinBox[2] / tileSize) + 1):
			for j in range(pinBox[3] // tileSize, pinBox[4] // tileSize + 1):
				image[pinBox[0]][i][j] = 3
	return image


def genCongMap(dir):
	designName = str(dir).split("/")[-1]
	sizeDBU = designDBUs[designName]
	xSizeDBU = sizeDBU[0][1] - sizeDBU[0][0]
	ySizeDBU = sizeDBU[1][1] - sizeDBU[1][0]
	mapSize = (math.ceil(xSizeDBU / tileSize), math.ceil(ySizeDBU / tileSize))
	print('Generating congestion map of %s, size: %d x %d' % (designName, mapSize[0], mapSize[1]))
	image = np.zeros((9, mapSize[0], mapSize[1]))
	# for point in poorWireInDBU:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 1
	# for point in wireShortVio:
	# 	if (int(point[1]//tileSize) >= mapSize[0] or int(point[2]//tileSize) >= mapSize[1]):
	# 		print((point))
	# 		continue
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 2
	# for point in wireSpaceVio:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 3
	# for point in poorVia:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 4
	# for point in sameLayerViaVios:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 5
	# for point in viaBotWireVios:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 6
	# for point in viaTopViaVios:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 7
	# for point in viaTopWireVios:
	# 	image[point[0]][int(point[1]//tileSize)][int(point[2]//tileSize)] = 8
	vios = ['poorWire', 'wireShortVio', 'wireSpaceVio', 'poorVia', 'sameLayerViaVios', 'viaBotWireVios', 'viaTopViaVios', 'viaTopWireVios']
	for i in range(len(vios)):
		image[i] = getCongMapChannel(dir, vios[i], mapSize, i+1)
	return image


for dir in PATH.glob("*"):
	designName = str(dir).split("/")[-1]
	# longName = "ispd1" + designName.split('t')[0] + "_test" + designName.split("t")[1] + ".solution.def"
	# poorWireInDBU = getViosInDBU(dir, "poorWire")
	# wireShortVio = getViosInDBU(dir, "wireShortVio")
	# wireSpaceVio = getViosInDBU(dir, "wireSpaceVio")
	# poorVia = getViosInDBU(dir, "poorVia")
	# sameLayerViaVios = getViosInDBU(dir, "sameLayerViaVios")
	# viaBotWireVios = getViosInDBU(dir, "viaBotWireVios")
	# viaTopViaVios = getViosInDBU(dir, "viaTopViaVios")
	# viaTopWireVios = getViosInDBU(dir, "viaTopWireVios")
	# netPins = getFeatsInDBU(dir, "netPins")

	# print(len(netPins))
	obs = getFeatsInDBU(dir, "obs")
	unUsedPins = getFeatsInDBU(dir, "unUsedPins")

	# hyperImage = generateHyperImg(dir, netPins, obs, unUsedPins)
	congMap = genCongMap(dir)
	# np.save("hyperImage_"+designName, hyperImage)
	# np.save("congMap_"+designName, congMap)