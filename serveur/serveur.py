#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tkinter import *
import threading
import time

verrouInput = threading.RLock()
verrouOuput = threading.RLock()

outputQueue = {'nombresMessages':1, 'nombresConnectes':0, 'etat':'off', 'log':''}
inputQueue = {'port':0, 'nom':'', 'bouton':0}



class Interface(threading.Thread, Frame):

    def __init__(self, fenetre, **kwargs):
        threading.Thread.__init__(self)
        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)

        self.nombreMessages = 0
        self.nombreConnectes = 0
        self.log = ''

        self.construire()
        self.showOuput()


    def construire(self):

        #Frame Option

        self.frameOption = LabelFrame(self.fenetre, text="Options", padx=5, pady=5)
        self.frameOption.grid(row=0, column=0)

        self.textName = Label(self.frameOption, text="Nom: ")
        self.textName.grid(row=0, column=0)
        value = StringVar()
        value.set("Flying Fish")
        self.boxName= Entry(self.frameOption, textvariable=value)
        self.boxName.grid(row=0, column=1)

        self.textPort = Label(self.frameOption, text="Port: ")
        self.textPort.grid(row=1, column=0)
        value = StringVar()
        value.set("5050")
        self.boxPort = Spinbox(self.frameOption, from_=0, to=50000, textvariable=value)
        self.boxPort.grid(row=1, column=1)

        self.boxRun = Button(self.frameOption, text="Lancer", command=self.lancer)
        self.boxRun.grid(row=2, column=0, columnspan=2)

        # Frame INfo

        self.frameInfo = LabelFrame(self.fenetre, text="Info", padx=5, pady=5)
        self.frameInfo.grid(row=0, column=1)

        self.textCompteur = Label(self.frameInfo, text=": personnes connectés ")
        self.textCompteur.grid(row=0, column=1, sticky=W)
        self.boxCompteur = Label(self.frameInfo)
        self.boxCompteur.grid(row=0, column=0)

        self.textNbreMessages = Label(self.frameInfo, text=": messages envoyés ")
        self.textNbreMessages.grid(row=1, column=1, sticky=W)
        self.boxNbreMessages = Label(self.frameInfo, text=self.nombreMessages)
        self.boxNbreMessages.grid(row=1, column=0)

        self.textEtat = Label(self.frameInfo, text=": état du serveur")
        self.textEtat.grid(row=2, column=1, sticky=W)
        self.boxEtat = Label(self.frameInfo, text="Etat")
        self.boxEtat.grid(row=2, column=0)

        # Frame log

        self.frameLog = LabelFrame(self.fenetre, text="Log", padx=5, pady=5)
        self.frameLog.grid(row=1, column=0, rowspan=2, columnspan=2)

        self.boxLog = Text(self.frameLog, width="40", height="15")

        self.scrollbar1 = Scrollbar(self.frameLog)
        self.scrollbar1.config(command=self.boxLog.yview)
        self.boxLog.config(yscrollcommand=self.scrollbar1.set)
        self.scrollbar1.pack(side="right", fill="y")
        self.boxLog.pack(fill="both")
        self.boxLog.config(state="disabled")

    def showOuput(self):
        self.fenetre.after(100, self.showOuput)
        self.getOutput()

        self.boxNbreMessages.config(text=self.nombreMessages)
        self.boxNbreMessages.grid()

        self.boxCompteur.config(text=self.nombreConnectes)
        self.boxCompteur.grid()

        self.boxLog.insert(END, '\n'+time.strftime("%H:%M:%S -> ")+self.log)
        self.boxLog.pack()


    def lancer(self):
        print("Lancement demandé !")

    def addToInput(self, nom, valeur):
        with verrouInput:
            outputQueue[nom] = valeur

    def getOutput(self):
        with verrouOuput:
            self.nombreMessages = outputQueue['nombresMessages']
            self.nombreConnectes = outputQueue['nombresConnectes']
            self.log = outputQueue['log']


class Modele(threading.Thread):


    def __init__(self):
        threading.Thread.__init__(self)

        self.mainloop()

    def mainloop(self):
        i = 0
        while 1:
            i += 1
            self.addOutput('nombreMessages', i)
            time.sleep(1)


    def addOutput(self, nom, valeur):
        with verrouOuput:
            outputQueue[nom] = valeur


    def getInput(self):
        with verrouInput:
            self.nom = inputQueue['nom']
            self.port = inputQueue['port']
            self.bouton = inputQueue['bouton']

            inputQueue['bouton'] = 0









fenetre = Tk()
fenetre.title("Flying Fish")
fenetre.resizable(0,0)
interface = Interface(fenetre)



interface.mainloop()

