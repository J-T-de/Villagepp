import aiv
from aiv_enums import Troop_Id

aiv = aiv.Aiv()

aiv.troop_place(Troop_Id.MGL, (1,1))
aiv.troop_place(Troop_Id.OIL, (1,1))
aiv.troop_place(Troop_Id.OIL, (1,2))
print(aiv.tmap)

# aiv.troop_remove((1,1))

# print(aiv.tmap)
print(aiv.tarr)
print(aiv.tmap)