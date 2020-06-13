from urllib.request import urlopen
import math
import hashlib
import pickle
from os import path

class Deck:

    def importDeck(number):
        #Grab the Deck list Webpage
        link = "https://aetherhub.com/Deck/Public/"+number
        page = urlopen(link).read().decode("utf-8")
        decklists = page.find("store.tcgplayer.com/massentry") + 127
        deckliste = page.find("\"", decklists)
        
        #Split the list into an array
        decklist = []
        for i in page[decklists:deckliste].split("||"):
            # REPLACE need a better way to check for multi-legal cards
            if i[:1] != '1' and ((i[2:] != "Seven Dwarves") and (i[2:] != "Rat Colony") and (i[2:] != "Persistent Petitioners")):
                return "Deck isn't singleton"
            else:
                decklist.append([ int(i[:1]), i[2:].replace("&#x27;", "'") ])
        
        # REPLACE with better system that handles multiple cards
        #Check ban list
        if ["1", "Oko, Thief of Crowns"] in decklist:
            return "Deck contains banned cards"
        
        # Get Basic land count, and add to deck list
        basics = []
        basicnames = ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]
        j=0
        for i in basicnames:
            basics.append(math.ceil((page.count(i) - 5) / 10))
            if basics[j] != 0:
                decklist.append([ basics[j], i ])
            j += 1
        
        #Check deck size
        cardcount = 0
        for i in decklist:
            cardcount += i[0]
        if cardcount < 100:
            return "Deck has too few cards"
        
        #Create a hash of the deck to compare to database
        h = hashlib.md5()
        h.update(bytes(str(decklist), "utf-8"))
        deckhash = h.hexdigest()
        
        if not path.exists("decks"):
            os.mkdir("decks")
        
        if not path.exists("decks/" + deckhash):
            with open("decks/"+deckhash, 'wb') as fp:
                pickle.dump(decklist, fp)
        
        return deckhash
        