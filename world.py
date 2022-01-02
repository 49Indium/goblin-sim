import random as r
import time as t
import math as m
import opensimplex
from data import *
import png

class World(object):
    def __init__(self, height, width, name) -> None:
        self._width = width
        self._height = height
        self.name = name

        self._hmap = [[0 for i in range(width)] for i in range(height)]
        self._tmap = [["" for i in range(width)] for i in range(height)]

    def get_adjacents(self, qpos):
        qx, qy = qpos
        xs = [max(qx - 1, 0), qx, min(qx + 1, self._width - 1)]
        ys = [max(qy - 1, 0), qy, min(qy + 1, self._height - 1)]
        adjacents = [(x,y) for x in xs for y in ys if (x,y) != qpos]
        return adjacents

    def get_hmap(self):
        return self._hmap
    
    def get_tmap(self):
        return self._tmap

    def get_hvals(self, qposs):
        vals = []
        for qpos in qposs:
            x, y = qpos    
            vals.append(self._hmap[y][x])
        return vals
    
    def get_tvals(self, qposs):
        vals = []
        for qpos in qposs:
            x, y = qpos    
            vals.append(self._tmap[y][x])
        return vals
    
    def distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return m.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def generate_terrain(self):
        #Generate simplex noise over each tile
        print("Generating Height Map...")
        tic = t.perf_counter()
        hmap = self._hmap
        gen = opensimplex.OpenSimplex(seed = r.randint(1,1000))
        for y, row in enumerate(hmap):
            for x in range(len(row)):
                row[x] = (
                0.8 * gen.noise2(x/75, y/75) +
                0.3 * gen.noise2(x/20 + 7, y/20 + 7)
                )
                row[x] = max(min((row[x] + 1)/2, 1), 0) #Scale and clamp between 0 and 1
        self._hmap = hmap
        tmap = self._tmap
        toc = t.perf_counter()
        print(f"Done! ({toc - tic:0.4f} seconds)")
        print("Creating Terrain Map...")
        tic = t.perf_counter()
        for y, row in enumerate(hmap):
            for x, hval in enumerate(row):
                for bound in TERRAINBOUNDS:
                    if bound[0] <= hval < bound[1]:
                        tmap[y][x] = TERRAINBOUNDS.get(bound)
        toc = t.perf_counter()
        print(f"Done! ({toc - tic:0.4f} seconds)")
        print("Generating Rivers...")
        fails = 0
        tic = t.perf_counter()
        ### RIVER TIME ###
        mountains = []
        stops = []
        #Find starting (mountains) and stopping points
        for y, row in enumerate(tmap):
            for x, tval in enumerate(row):
                if tval == "Mountains":
                    mountains.append((x,y))
                if tval == "Shallow Ocean":
                    stops.append((x,y))
                if x == 0 or y == 0 or x == self._width or y == self._height:
                    stops.append((x,y))

        river_starts = []
        for i in range(RIVER_AMOUNT):
            #Choose starting point sufficiently far away from other river starts
            distance = -1
            while distance < RIVER_DISTANCE:
                pstart = r.choice(mountains)
                distances = []
                for start in river_starts:
                    distances.append(self.distance(pstart, start))
                distance = min(distances, default = 999)
            river_starts.append(pstart)
            #Start river algorithm until it hits the shallows (or gets stuck)
            cpos = pstart
            length = 0
            while cpos not in stops:
                cx, cy = cpos
                tmap[cy][cx] = "River"
                length += 1
                #Find the three lowest adjacent spaces
                cadjacents = self.get_adjacents(cpos)
                lowests = []

                for j in range(3):
                    lowest = cadjacents[0]
                    for apos in cadjacents:
                        if hmap[apos[1]][apos[0]] <= hmap[lowest[1]][lowest[0]]:
                            lowest = apos
                    cadjacents.remove(lowest)
                    lowests.append(lowest)
                
                #Add slight randomness to direction (stops straight line rivers)
                cpos = r.choice(lowests)
                #Check river is not looping if so stop it
                while tmap[cpos[1]][cpos[0]] == "River":
                    if len(lowests) == 0:
                        #Pick any random path not a river and go (makes pools)
                        if len(cadjacents) != 0:
                            cpos = r.choice(cadjacents)
                            cadjacents.remove(cpos)
                        else:
                            fails += 1
                            cpos = stops[0]
                    else:
                        cpos = r.choice(lowests)
                        lowests.remove(cpos)

        toc = t.perf_counter()
        print(f"Done! ({toc - tic:0.4f} seconds and {fails} fails out of {RIVER_AMOUNT} rivers)")
        #Smoothing
        print("Smoothing Rivers...")
        tic = t.perf_counter()
        count = 0
        for y, row in enumerate(tmap):
            for x, tval in enumerate(row):
                if tval != "River":
                    adjacenttvals = self.get_tvals(self.get_adjacents((x,y)))
                    if adjacenttvals.count("River") >= 5:
                        tmap[y][x] = "River"
                        count += 1
        toc = t.perf_counter()
        print(f"Done! ({toc -tic:0.4f} seconds and {count} smoothings)")
        print("Terrain Generated!")
        self._tmap = tmap


