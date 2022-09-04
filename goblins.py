import world as w
from data import *
import tools as tls
import random as r

r.seed("hyn")
test = w.World("test", width=500, height=500)
test.generate_world(0, 0)
#path = tls.a_star_pathfinding(test, (135,35), (154, 99))
tls.tmap_to_png(test, [])
tls.bmap_to_png(test)
tls.map_to_png(test._temperature_map, file_name="temp", filter = lambda temp, **_ : [int(255 * temp / 40) for _ in range(3)])
tls.map_to_png(test._precipitation_map, file_name="rain", filter = lambda temp, **_ : [int(255 * temp / 10000) for _ in range(3)])