#World Generation
TERRAINBOUNDS = {(0, 0.3):"Deep Ocean", 
                 (0.3, 0.45): "Medium Ocean",
                 (0.45, 0.5): "Shallow Ocean",
                 (0.5, 0.525): "Beach",
                 (0.525, 0.75): "Flatlands",
                 (0.75, 0.8): "Hills",
                 (0.8, 1.1): "Mountains"}

TERRAINCOLOURS = {"Deep Ocean": (2, 7, 93),
                  "Medium Ocean": (0, 65, 194),
                  "Shallow Ocean": (173, 216, 230),
                  "Beach": (220, 192, 139),
                  "Flatlands": (126, 200, 80),
                  "Hills": (68, 76, 56),
                  "Mountains": (58, 59, 60),
                  "River": (144, 204, 224)}

RIVER_AMOUNT = 75
RIVER_DISTANCE = 5