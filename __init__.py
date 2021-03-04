"""Simple creador de manga galeries display para imagenes locales"""

import os
from urllib.parse import quote
from mimetypes import guess_type
import dominate
from dominate.tags import a, p, h3, img, meta, style, div
from collections.abc import Iterable
import itertools_recipes
from valid_filenames import valid_file_name
import contextlib_recipes
#from dominate import tags


__all__=['make_gallery','make_gallery_from_folder','get_img_list_from',"extrac_menu","sort_key_num","make_gallery_from_folder_with_subfolders","DEFAULT_MENU","es_img"]

DEFAULT_MENU = 20

#
def make_gallery(nombre_html:str,
                 imagenes:[str],
                 path:str="",
                 menu:[('img_number:int','name:str')]=DEFAULT_MENU,
                 title:str=None,
                 individual_ch:bool=False,
                 _of=-1,_total=0,
                 remove_old_html=False):
    """Crea un simple archivo html para mostrar todas las imagenes sumistradas.

       nombre_html: nombre del archivo a crear
       imagenes: lista de los path de las imagenes deseadas
       path: lugar donde guardara el resultado
       title: titulo que tendra el archivo html creado, por defecto es el mismo
              del nombre del archivo
       menu: lista de tuplas para la creacion de un simple menu, consistentes del index
             de una imagen (en 1-index format) en la lista de imagenes y un string
             representativo para saltar a ese punto en la galeria creada.
             Tambien puede ser un número k, en cuyo caso se creara un menu automatico
             que apunte a una imagen a intevalos k siempre que haya más de k imagenes
       individual_ch: si es True, y el menu no es un numero, entonces se crearan galleries
                      adicionales para cada capitulo en el menu
       """
    if remove_old_html:
        with contextlib_recipes.redirect_folder(path):
            for html in [x for x in os.listdir() if os.path.isfile(x) and x.endswith(".html")]:
                os.remove(html)
    if not title:
        title = nombre_html
    try:
        total = len(imagenes)
    except TypeError:
        imagenes = tuple(imagenes)
        total = len(imagenes)
    if not imagenes:
        return
    if isinstance(menu,int) and total > 50:
        menu = [ ( i, 'paginas {}-{}'.format(i,min(i+menu-1,total)) ) for i in range(1,total+1,menu) ]
    if individual_ch and isinstance(menu,Iterable):
        if isinstance(menu,str):
            menu = menu_from_txt(os.path.join(path,menu))
        menu = list(menu) # just in case a generator is given
        for i,((start,name),(end,_)) in enumerate(itertools_recipes.pairwise(itertools_recipes.chain(( (int(x)-1,y) for x,y in menu),[(None,None)])),1):
            make_gallery(nombre_html+" ch{:02d} - ".format(i)+name, imagenes[start:end], path, menu=None, title=name, individual_ch=False, _of=start, _total=total)        
    with dominate.document(title=title) as doc:
        with doc.head:
            meta(charset="UTF-8")
            style('img {max-width:100%;}' )
        if isinstance(menu,int):
            #auto menu
            step = menu
            if total > step:
                with div(id='menu'):
                    h3('Paginas')
                    for i in range(1,total+1,step):
                        p(a('paginas {}-{}'.format(i,min(i+step-1,total)),href='#{}'.format(i)),__pretty=False)
        elif menu:
            with div(id="menu"):
                h3("Menu")
                for num, name in menu:
                    p(a(name,href='#{}'.format(num)),__pretty=False)
        with div(align='center', id='imagenes'):
            for i,image in enumerate(imagenes,1):
                src = quote(image, safe=r'\/')
                p([a(os.path.basename(image),href=src,target='_blank')," ({i}/{total}) ({ii} of {ttotal})".format(i=i,total=total, ii=i+_of,ttotal=_total) if _total and _of>=0 else " ({i}/{total})".format(i=i,total=total)],id=i,__pretty=False)
                img(src=src)
    with open(os.path.join(path,valid_file_name(nombre_html)+".html"), "w", encoding="utf8") as html:
        html.write(doc.render())

    #return doc

def es_img(name):
    tipo,_ = guess_type(name)
    if tipo:
        return tipo.startswith("image")
    return name.endswith(".webp")

def get_img_list_from(path, sort_key=str.lower):
    """Regresa una lista con las imagenes contenidas en path"""
    return sorted(filter(es_img,os.listdir(path)),key=sort_key)

def sort_key_num(name_file:str) -> int:
    """si el nombre del archivo dado empiesa por un numero, 
       regresa el valor numerico del mismo, sino regresa el
       valor suministrado"""
    num = ''.join(itertools_recipes.takewhile(str.isnumeric, name_file))
    if num:
        return int(num)
    else:
        return name_file

def menu_from_txt(file_name:str,*,encoding="utf8") -> [(int,str)]:
    """Lee el menu del archivo de texto dado"""
    try:
        with open(file_name,encoding=encoding) as file:
            for line in map(str.strip, file):
                if line:
                    try:
                        pag,ch = line.split(maxsplit=1)
                        yield int(pag),ch
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass

def make_gallery_from_folder(path:str=".",nombre_html:str=None,menu:[('img_number','name')]=DEFAULT_MENU,sort_key=str.lower,**mg):
    """Crea un simple archivo html para mostrar todas las imagenes de la carpeta sumistrada

       nombre_html: nombre del archivo a crear
       path: lugar donde estan las imagenes y se guardara el resultado"""
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise ValueError("No es una carpeta")
    if not nombre_html:
        nombre_html = os.path.basename(path)
    make_gallery(nombre_html,get_img_list_from(path,sort_key),path,menu=menu,**mg)

def make_gallery_from_folder_with_subfolders(path:str=".",nombre_html:str=None,sort_key=str.lower,fsort_key=str.lower,**mg):
    """Crea un simple archivo html para mostrar todas las imagenes de las subcarpeta de la carpeta sumistrada
       

       nombre_html: nombre del archivo a crear
       path: lugar donde estan las carpetas de imagenes y se guardara el resultado"""
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise ValueError("No es una carpeta")
    if not nombre_html:
        nombre_html = os.path.basename(path)
    with contextlib_recipes.redirect_folder(path):
        img = [ os.path.join(c,n) for c in sorted(os.listdir(path),key=fsort_key) if os.path.isdir(c) for n in get_img_list_from(c,sort_key)]
        menu=[]
        i=1
        for k,v in itertools_recipes.groupby(img,os.path.dirname):
            menu.append( (i,k) )
            i += itertools_recipes.ilen(v)
        make_gallery(nombre_html,img,menu=menu,**mg)

def remove_non_img(path):
    """Remueve todos los archivos que no sean imagenes de la carpeta dada"""
    with contextlib_recipes.redirect_folder(path):
        for f in filter(os.path.isfile,os.listdir()):
            if not es_img(f):
                os.remove(f)

def _extrac_menu(text):
    """extrae un menu de un extracto html hecho por este modulo"""
    return [ x.strip().replace('<p><a href="#',"").replace("</a></p>","").split('">')
             for x in text.splitlines()]


