# World Generation
TERRAIN_BOUNDS = {(0, 0.3): "Deep Ocean",
                  (0.3, 0.45): "Medium Ocean",
                  (0.45, 0.5): "Shallow Ocean",
                  (0.5, 0.525): "Beach",
                  (0.525, 0.75): "Flatlands",
                  (0.75, 0.8): "Hills",
                  (0.8, 1.1): "Mountains"}

TERRAIN_COLOURS = {"Deep Ocean": (2, 7, 93),
                   "Medium Ocean": (0, 65, 194),
                   "Shallow Ocean": (173, 216, 230),
                   "Beach": (220, 192, 139),
                   "Flatlands": (126, 200, 80),
                   "Hills": (68, 76, 56),
                   "Mountains": (58, 59, 60),
                   "River": (144, 204, 224)}

BIOME_COLOURS = {"Dry Tundra": (255, 241, 182),
                 "Desert": (255, 255, 0),
                 "Moist Tundra": (202, 163, 232),
                 "Dry Bush": (249, 183, 117),
                 "Desert Bush": (199, 141, 70),
                 "Wet Tundra": (154, 114, 172),
                 "Moist Forrest": (92, 208, 179),
                 "Steppe": (201, 226, 174),
                 "Thorn Steppe": (131, 193, 103),
                 "Thorn Woodland": (105, 156, 82),
                 "Rain Tundra": (100, 65, 114),
                 "Wet Forrest": (88, 196, 221),
                 "Dry Forrest": (247, 161, 163),
                 "Very Dry Forrest": (252, 98, 85),
                 "Rain Forrest": (35, 107, 142)}

# Path-finding
# Represents the relative costs of moving through a terrain type (higher => less likely to pathfind through)
PATH_COSTS = {"Deep Ocean": 10,
              "Medium Ocean": 6,
              "Shallow Ocean": 5,
              "Beach": 3,
              "Flatlands": 1,
              "Hills": 2,
              "Mountains": 3,
              "River": 3}
