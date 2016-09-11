#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tkinter import *
import threading




class Interface(threading.Thread, Frame):

    def __init__(self, fenetre, **kwargs):
        threading.Thread.__init__(self)
        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)
        self.construire()



    def construire(self):
        ##########################################
        ######### cadre de communication #########
        ##########################################


        self.cadreCommunication = Frame(self.fenetre)
        self.cadreCommunication.pack(side='right', fill="both", padx=5, pady=5)

        # cadre console avec scroll bar :
        self.cadreConsole = Frame(self.cadreCommunication)
        self.cadreConsole.pack(fill="both", padx=5, pady=5)

        self.console = Text(self.cadreConsole)

        self.scrollbar1 = Scrollbar(self.cadreConsole)
        self.scrollbar1.config(command=self.console.yview)
        self.console.config(yscrollcommand=self.scrollbar1.set)

        self.scrollbar1.pack(side="right", fill="y")
        self.console.pack(fill="both")
        # fin cadre console

        self.champ_commande = Entry(self.cadreCommunication)
        self.champ_commande.bind("<Return>")
        self.champ_commande.pack(padx=5, fill='x')

        ##########################################
        #########   Tableaud de bord     #########
        ##########################################


        # frame principale
        self.tbBord = LabelFrame(self.fenetre, text="Liste des serveurs", padx=15, pady=10)
        self.tbBord.pack(side="left", fill="y", padx=5, pady=5)

        # liste utilisateurm on lance un thread pour afficher la liste des users
        self.listeAndScroll = Frame(self.tbBord)
        self.listeAndScroll.pack(pady=10, fill='both', side='left')

        self.select_serveur = Listbox(self.listeAndScroll)

        self.scrollbarListe = Scrollbar(self.listeAndScroll)
        self.scrollbarListe.config()
        self.select_serveur.config(yscrollcommand=self.scrollbarListe.set)

        self.scrollbarListe.pack(side='right', fill='y')
        self.select_serveur.pack(fill='both', side='left')

    def lancer(self):
        print("Lancement demandé !")







fenetre = Tk()
fenetre.title("Flying Fish")
fenetre.resizable(0,0)
interface = Interface(fenetre)

interface.mainloop()
interface.destroy()