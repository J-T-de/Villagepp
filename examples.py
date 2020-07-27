from aiv import aiv
import numpy as np
import matplotlib.pyplot as plt
import os

# your directory
directory = "D:/Games/Steam/steamapps/common/Stronghold Crusader Extreme/aiv_bu"

aivs = {}

aivs["pig8"] = aiv.parse_file(os.path.join(directory, "pig8.aiv"))

pig8_bmap_size = np.frombuffer(aivs["pig8"].bmap_size.data, dtype=np.int8).reshape((100,100))


plt.matshow(pig8_bmap_size, cmap = "rainbow")
plt.colorbar()
plt.show()
