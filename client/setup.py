
from cx_Freeze import setup, Executable

setup(
    name='flyingfish - client',
    version='0.1',
    description='A network chat app',
    executables=[Executable('D:/User/Bibliothèque/Documents/Programmes/FlyingFish/serveur/client.py')],
)
