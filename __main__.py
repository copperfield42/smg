from smg import make_gallery_from_folder
import sys

_,ruta = sys.argv
if ruta == "-h":
    print(">smg path")
elif ruta:
    make_gallery_from_folder(ruta)
else: pass