import random as r
import time as t
import math as m
import opensimplex
from data import *
import holdridge_lifezone_system


class World():
    def __init__(self, name, width=500, height=500) -> None:
        self.name = name
        self._width = width
        self._height = height
        self._height_map = [[0 for i in range(width)] for i in range(height)]
        self._precipitation_map = [
            [0 for i in range(width)] for i in range(height)]
        self._PET_map = [[0 for i in range(width)] for i in range(height)]
        self._biome_map = [["" for i in range(width)] for i in range(height)]
        self._terrain_map = [["" for i in range(width)] for i in range(height)]

    def get_adjacents(self, qpos):
        qx, qy = qpos
        xs = [max(qx - 1, 0), qx, min(qx + 1, self._width - 1)]
        ys = [max(qy - 1, 0), qy, min(qy + 1, self._height - 1)]
        adjacents = [(x, y) for x in xs for y in ys if (x, y) != qpos]
        return adjacents

    def get_height_map(self):
        return self._height_map

    def get_terrain_map(self):
        return self._terrain_map

    def get_cost(self, pos1, pos2):
        """
        Returns 'cost' of moving between the two positions
        Used in path finding.
        """
        terrains = self.get_terrain_vals([pos1, pos2])
        return (PATH_COSTS[terrains[0]] + PATH_COSTS[terrains[1]])/2

    def get_terrain_vals(self, qposs):
        """
        Returns a list of the terrains of each of the positions in qposs
        """
        vals = []
        for qpos in qposs:
            x, y = qpos
            vals.append(self._terrain_map[y][x])
        return vals

    def distance(self, pos1, pos2):
        """
        Calculates the Euclidean distance between two points.
        Used as a close enough heuristic in pathfinding
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return m.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _generate_height_map(self, *, seed=None, verbose=True):
        """
        Generates the world's height map.
        Parameters:
            seed(int | None): The seed for the pseudo-randomness.
                              If none, random.randint(1,1000) is used
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Generating Height Map...")
        if seed is None:
            seed = r.randint(1, 1000)
        tic = t.perf_counter()
        _generate_simplex_map(map=self._height_map, seed=seed)
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc - tic:0.4f} seconds)")

    def _generate_precipitation_map(self, *, seed=None, verbose=True):
        """
        Generates the world's annual precipitation map.
        Parameters:
            seed(int | None): The seed for the pseudo-randomness.
                              If none, random.randint(1,1000) is used
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Generating Precipitation Map...")
        if seed is None:
            seed = r.randint(1, 1000)
        tic = t.perf_counter()
        _generate_simplex_map(map=self._precipitation_map, seed=seed, filter=lambda z : 4500*max(min((z + 1)/2, 1), 0))
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc - tic:0.4f} seconds)")

    def _generate_PET_map(self, *, seed=None, verbose=True):
        """
        Generates the world's annual precipitation map.
        Parameters:
            seed(int | None): The seed for the pseudo-randomness.
                              If none, random.randint(1,1000) is used
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Generating PET Map...")
        if seed is None:
            seed = r.randint(1, 1000)
        tic = t.perf_counter()
        _generate_simplex_map(map=self._PET_map, seed=seed, filter=lambda z : 5*max(min((z + 1)/2, 1), 0))
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc - tic:0.4f} seconds)")

    def _generate_biome_map(self, *, verbose=True):
        """
        Generates the biome map.
        Parameters:
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Creating Biome Map...")
        tic = t.perf_counter()
        for y, row in enumerate(self._height_map):
            for x in range(len(row)):
                precipitation = holdridge_lifezone_system.HoldridgeParameter("Annual Precipitation", self._precipitation_map[y][x])
                PET = holdridge_lifezone_system.HoldridgeParameter("PET", self._PET_map[y][x])
                self._biome_map[y][x] = holdridge_lifezone_system.get_holdridge_biome([precipitation, PET])
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc - tic:0.4f} seconds)")

    def _generate_terrain_map(self, *, verbose=True):
        """
        Generates the terrain map.
        Parameters:
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Creating Terrain Map...")
        tic = t.perf_counter()
        # Classify each tile based on TERRAINBOUNDS
        for y, row in enumerate(self._height_map):
            for x, hval in enumerate(row):
                for bound in TERRAIN_BOUNDS:
                    if bound[0] <= hval < bound[1]:
                        self._terrain_map[y][x] = TERRAIN_BOUNDS.get(bound)
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc - tic:0.4f} seconds)")

    def _generate_rivers(self, rivers, river_distance, *, verbose=True):
        """
        Generates rivers.
        Parameters:
            rivers(int): the number of rivers to try to include
            river_distance(int): the minimum distance between river start points
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Generating Rivers...")
        fails = 0  # Fails are where river does not reach the ocean.
        tic = t.perf_counter()
        mountains = []
        stops = []
        # Find starting (mountains) and stopping points
        for y, row in enumerate(self._terrain_map):
            for x, tval in enumerate(row):
                if tval == "Mountains":
                    mountains.append((x, y))
                if tval == "Shallow Ocean":
                    stops.append((x, y))
                if x == 0 or y == 0 or x == self._width or y == self._height:
                    stops.append((x, y))

        river_starts = []
        for _ in range(rivers):
            # Choose starting point sufficiently far away from other river starts
            distance = -1
            while distance < river_distance:
                pstart = r.choice(mountains)
                distances = []
                for start in river_starts:
                    distances.append(self.distance(pstart, start))
                distance = min(distances, default=river_distance)
            river_starts.append(pstart)

            # Start river algorithm until it hits the shallows (or gets stuck)
            cpos = pstart
            while cpos not in stops:
                cx, cy = cpos
                self._terrain_map[cy][cx] = "River"
                # Find the three lowest adjacent spaces
                cadjacents = self.get_adjacents(cpos)
                lowests = []
                for _ in range(3):
                    lowest = cadjacents[0]
                    for apos in cadjacents:
                        if self._height_map[apos[1]][apos[0]] <= self._height_map[lowest[1]][lowest[0]]:
                            lowest = apos
                    cadjacents.remove(lowest)
                    lowests.append(lowest)

                # Add slight randomness to direction (stops straight line rivers)
                cpos = r.choice(lowests)
                # Check if river is about to loop and avoid it
                while self._terrain_map[cpos[1]][cpos[0]] == "River":
                    if len(lowests) != 0:
                        # Pick another one of the three lowests if possible
                        cpos = r.choice(lowests)
                        lowests.remove(cpos)
                    else:
                        # Pick any random direction not a river and go that way
                        if len(cadjacents) != 0:
                            cpos = r.choice(cadjacents)
                            cadjacents.remove(cpos)
                        else:
                            # if no adjacents are not rivers - stop
                            fails += 1
                            cpos = stops[0]

        toc = t.perf_counter()
        if verbose:
            print(
                f"Done! ({toc - tic:0.4f} seconds and {fails} fails out of {rivers} rivers)")

    def _smooth_rivers(self, smoothness=5, *, verbose=True):
        """
        Smooths out rivers.
        Parameters:
            smoothness(int): if at least this many adjacent tiles are river turn tile to river
            verbose(boolean): whether to print runtime and progress
        """
        if verbose:
            print("Smoothing Rivers...")
        tic = t.perf_counter()
        count = 0
        for y, row in enumerate(self._terrain_map):
            for x, tval in enumerate(row):
                if tval != "River":
                    adjacenttvals = self.get_terrain_vals(
                        self.get_adjacents((x, y)))
                    if adjacenttvals.count("River") >= smoothness:
                        self._terrain_map[y][x] = "River"
                        count += 1
        toc = t.perf_counter()
        if verbose:
            print(f"Done! ({toc -tic:0.4f} seconds and {count} smoothings)")

    def generate_world(self, rivers, river_distance, *, verbose=True):
        """
        Generates the world's terrain.
        Parameters:
            rivers(int): number of rivers to attempt to add
            river_distance(int): minimum distance between river start points
        """
        self._generate_height_map(verbose=verbose)
        self._generate_precipitation_map(verbose=verbose)
        self._generate_PET_map(verbose=verbose)
        self._generate_biome_map(verbose=verbose)
        self._generate_terrain_map(verbose=verbose)
        self._generate_rivers(rivers, river_distance, verbose=verbose)
        self._smooth_rivers(verbose=verbose)

        if verbose:
            print("Terrain Generated!")


def _generate_simplex_map(map, *, seed=None, filter=lambda z : max(min((z + 1)/2, 1), 0)):
    """
    Generates a 0 to 1 simplex noise map.
    Parameters:
        map(list[list]): the map to write over
        seed(int | None): The seed for the pseudo-randomness. If none, random.randint(1,1000) is used
        filter(Callable[[float], Any]): A filter to apply on the output of each cell
    """
    if seed is None:
        seed = r.randint(1, 1000)
    tic = t.perf_counter()
    gen = opensimplex.OpenSimplex(seed=seed)
    # Generate simplex noise over each tile
    for y, row in enumerate(map):
        for x in range(len(row)):
            row[x] = (0.8 * gen.noise2(x/75, y/75) +
                      0.3 * gen.noise2(x/20 + 7, y/20 + 7))

            # Scale and clamp between 0 and 1
            row[x] = filter(row[x])
    return map
