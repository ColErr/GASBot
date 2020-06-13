from urllib.request import urlopen
import math
import hashlib
import pickle
from os import path, getenv

class Deck:

    def importDeck(number):
        #Grab the Deck list Webpage
        link = "https://aetherhub.com/Deck/Public/"+number
        page = urlopen(link).read().decode("utf-8")
        decklists = page.find("store.tcgplayer.com/massentry") + 127
        deckliste = page.find("\"", decklists)

        decklist = []
        nonsingleton = getenv("NON_SINGLE").split("|")
        banned = getenv("BANNED").split("|")
        
        #Split the list into an array
        for i in page[decklists:deckliste].split("||"):
            # Checks for singleton, ignores cards that allow multiples
            if i[:1] != '1' and (i[2:] not in nonsingleton):
                return "Deck isn't singleton"
            # Checks for banned cards
            elif (i[2:] in banned):
                return "Deck contains banned cards"
            else:
                decklist.append([ int(i[:1]), i[2:].replace("&#x27;", "'") ])
        
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
        