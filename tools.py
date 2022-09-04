from data import *
import png
import random as r
import heapq


def map_to_png(map, *, file_name, filter):
    pnglist = []
    for y, row in enumerate(map):
        pngrow = []
        for x, value in enumerate(row):
            colour = filter(value, x=x, y=y)
            pngrow += colour
        pnglist.append(pngrow)
    image = png.from_array(pnglist, "RGB")
    image.save(f"{file_name}.png")


def bmap_to_png(world):
    map = world._biome_map
    def filter(biome, **_): return BIOME_COLOURS[biome]
    map_to_png(map, file_name=f"{world.name}_bmap", filter=filter)


def hmap_to_png(world):
    map = world.get_height_map()
    def filter(height, **_): return [int(255 * (1 - height)) for _ in range(3)]
    map_to_png(map, file_name=f"{world.name}_hmap", filter=filter)


def tmap_to_png(world, path):
    map = world.get_terrain_map()
    def filter(terrain, x, y, **_): return [255, 0, 0] if (
        x, y) in path else TERRAIN_COLOURS.get(terrain)
    map_to_png(map, file_name=f"{world.name}_tmap", filter=filter)


def world_stats(world):
    print("World Analysis:")
    hmap = world.get_height_map()
    lowest = 1
    highest = 0
    for row in hmap:
        if min(row) < lowest:
            lowest = min(row)
        if max(row) > highest:
            highest = max(row)
    print("  Lowest Point:", lowest)
    print("  Highest Point:", highest)
    biome_tallies = {"Deep Ocean": 0,
                     "Medium Ocean": 0,
                     "Shallow Ocean": 0,
                     "Beach": 0,
                     "Flatlands": 0,
                     "Hills": 0,
                     "Mountains": 0,
                     "River": 0}
    tmap = world.get_tmap()
    for row in tmap:
        for tval in row:
            biome_tallies[tval] += 1
    print("  Biome Tile Counts:")
    for name in biome_tallies.keys():
        print("   ", name + ":", biome_tallies.get(name))


# PATHFINDING
class Priority_Queue:
    def __init__(self):
        self.elements = []  # List of tuples of form [priority element]

    def is_empty(self):
        return not self.elements

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def a_star_pathfinding(world, start, end):
    frontier = Priority_Queue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.is_empty():
        current = frontier.get()

        if current == end:
            break

        for next in world.get_adjacents(current):
            new_cost = cost_so_far[current] + world.get_cost(current, next)
            # if space not already in path or if a better path into space found
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + world.distance(next, end)
                frontier.put(next, priority)
                came_from[next] = current

    # Rebuild path :)
    current = end
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    return path


# OTHER TOOLS
def generate_name(sound_length):
    vowel_sounds = ["a", "e", "i", "o", "ai", "ee", "oa", "oi", "ow", "ar",
                    "ay", "ou", "ea", "aw", "ir", "ier", "oo", "or", "ur", "er",
                    "'"]

    consonant_sounds = ["b", "br", "c", "ck", "cr", "d", "dr", "f", "fr", "g",
                        "gr", "gn", "h", "j", "k", "l", "m", "n", "p", "pr", "q",
                        "qu", "s", "st", "sh", "t", "th", "tr", "v", "x", "z"]
    last = "v"
    name = ""
    for i in range(sound_length):
        if last == "v":
            name += r.choice(consonant_sounds)
            last = "c"
        else:
            name += r.choice(vowel_sounds)
            last = "v"
    return name.capitalize()
