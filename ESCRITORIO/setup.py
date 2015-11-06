
from distutils.core import setup
import py2exe

setup(name="Nombre ejecutable",
 version="1.0",
 description="Breve descripcion",
 author="autor",
 author_email="email del autor",
 url="url del proyecto",
 license="tipo de licencia",
 scripts=["gui3.py"],
 console=["gui3.py"],
 options={"py2exe": {"includes" : ["sip", ]}, "dll_excludes": ["libiomp5md.dll"]},
 zipfile=None,
)