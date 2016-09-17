#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tkinter import *
import threading
import time
import queue
import socket
import select
import pickle




outputQueue = queue.Queue()
inputQueue = queue.Queue()

#outputQueue.put_nowait({'nombreMessages':1, 'nombreConnectes':0, 'etat':'off', 'log':''})
#inputQueue.put_nowait({'port':0, 'nom':'', 'bouton':0})

downQueue = queue.Queue()
upQueue = queue.Queue()



class Interface(Frame):

    def __init__(self, fenetre, **kwargs):

        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)

        self.nombreMessages = 0
        self.nombreConnectes = 0
        self.log = ''

        self.construire()
        self.getAndShowOutput()

        self.dicoTmpGetOuput = {}


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

        self.boxRun = Button(self.frameOption, text="Lancer", command=self.refreshInput)
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


    def refreshInput(self):

        inputQueue.put_nowait({'nom': self.boxName.get(), 'port': int(self.boxPort.get())})
        

    def getAndShowOutput(self):
        
        self.fenetre.after(100, self.getAndShowOutput)


        try:
            outputDico = outputQueue.get_nowait()
            for cle, valeur in outputDico.items():
                if(cle == 'nombreMessages'):
                    self.boxNbreMessages.config(text=valeur)
                    self.boxNbreMessages.grid()
                elif(cle == 'nombreConnectes'):
                    self.boxCompteur.config(text=valeur)
                    self.boxCompteur.grid()
                elif(cle == 'log'):
                    self.boxLog.config(state="normal")
                    self.boxLog.insert(END, '\n'+time.strftime("%H:%M:%S -> ")+valeur)
                    self.boxLog.config(state="disable")
                    self.boxLog.pack()
                elif(cle == 'etat'):
                    self.boxEtat.config(text=valeur)
                    self.boxEtat.grid()
                

        except:
            pass



class Modele(threading.Thread):


    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        
        self.nom = ''
        self.port = 0


    def run(self):
        i = 0
        while self.running:
            #tant qu'on a pas appuié sur stop
            if self.getInput():
                #si on a lancé
                while self.getInput() == False and self.running:
                    #tant que l'on a pas lancé une autre fois

                    requeteClient = self.getQueue()

                    if requeteClient != False:

                        if requeteClient['type'] == 'msg':
                            self.downQueue('send@all', requeteClient['msg'])
                        else:
                            self.addOutput({'log':'Commande serveur: ' + requeteClient['type'] + ' pas encore implémentée.'})




    #Communication avec thread d'affichage (interface)
    def addOutput(self, dicoNomValeur):

        outputQueue.put_nowait(dicoNomValeur)

    def getInput(self):

        inputDico = {}
        try:
            inputDico = inputQueue.get_nowait()

            for cle, valeur in inputDico.items():

                if cle == 'port':
                    self.port = valeur

                elif cle == 'nom':
                    self.nom = valeur

            return True
            
            
        except:
            return False
            


    #communication avec thread de connexion reseau (comm avec clients)
    def downQueue(self, type, var):

        try:
            downQueue.put_nowait({'type':type, 'var':var})
        except:
            self.addOutput({'log':"Erreur: downQueue in Modele"})

    def getQueue(self):

        try:
            tmp = upQueue.get_nowait()
            tmp2 = tmp['type']

            return tmp

        except:
            return False

    def stop(self):
        self.running = False


class Reseau(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

        self.port = 4545
        self.hote = ''

        self.listeClients = []

        #on lance une connexion

        self.connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_principale.bind((self.hote, self.port))
        self.connexion_principale.listen(5)
        self.addOutput({'log': "Le serveur est sur le port {}".format(self.port)})


    def run(self):

        while self.running :

            queue = self.from_downQueue()
            if queue != False:

                if queue['type'] == 'port':
                    self.port = queue['port']

                    #on actualise la connexion au port demandé
                    self.connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connexion_principale.bind((self.hote, self.port))
                    self.connexion_principale.listen(5)
                    self.addOutput({'log':"Le serveur est sur le port {}".format(self.port)})


            # ecoute pour des demandes de connexion
            self.checkDemandes()

            #ecoute les requetes des clients
            clients_a_lire = self.checkClients_a_lire()

            #envoie info dans la Queue
            try:
                for client in clients_a_lire:
                    msg_brut = client.recv(1024)
                    msg_brut = msg_brut.loads()

                    if isinstance(msg_brut, type([])):
                        self.to_upQueue('recv', msg_brut)
            except:
                pass

            #lit Queue modèle
            msg_modele = self.from_downQueue()
            try:
                if msg_modele['type'] == 'send@all':
                    self.send_at_all(msg_modele['var'])

            except:
                self.addOutput({'log': "Erreur lecture queue modèle in Reseau"})



    def send_at_all(self, var):
        try:
            var = var.dumps()
            for client in self.listeClients:
                client.send(var)
        except:
            self.addOutput({'log': "Erreur in send@all in Reseau"})


    def checkDemandes(self):

        connexions_demandees, wlist, xlist = select.select([self.connexion_principale], [], [], 0.05)

        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            self.listeClients.append(connexion_avec_client)

    def checkClients_a_lire(self):
        client_a_lire = []
        try:
            client_a_lire, wlist, xlist = select.select(self.listeClients, [], [], 0.05)
            return client_a_lire
        except select.error:
            return []


    # communication avec thread de modèle (comm avec clients)
    def to_upQueue(self, type, var):

        try:
            upQueue.put_nowait({'type': type, 'var': var})
        except:
            self.addOutput({'log': "Erreur downQueue in Reseau"})

    def from_downQueue(self):

        try:
            tmp = upQueue.get_nowait()
            tmp2 = tmp['type']

            return tmp

        except:
            return False

    # Communication avec thread d'affichage (interface)
    def addOutput(self, dicoNomValeur):

        outputQueue.put_nowait(dicoNomValeur)

    def getInput(self):

        inputDico = {}
        try:
            inputDico = inputQueue.get_nowait()

            for cle, valeur in inputDico.items():

                if cle == 'port':
                    self.port = valeur

                elif cle == 'nom':
                    self.nom = valeur

            return True

        except:
            return False


    def stop(self):
        self.running = False



#definition fenetre

fenetre = Tk()
fenetre.title("Flying Fish")
fenetre.resizable(0,0)
interface = Interface(fenetre)


#definition modele

modele = Modele()
reseau = Reseau()


#lancement des threads
modele.start()
reseau.start()

fenetre.mainloop()




modele.stop()
reseau.stop()
reseau.join()
modele.join()