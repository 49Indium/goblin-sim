import world as w
from data import *
import tools as tls
import random as r

r.seed("4")
test = w.World("test", 100, 100)
test.generate_world(0, 0)
#path = tls.a_star_pathfinding(test, (135,35), (154, 99))
tls.tmap_to_png(test, [])
tls.bmap_to_png(test)