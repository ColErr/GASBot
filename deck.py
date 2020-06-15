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
            card = i.split(" ", 1)
            card[0] = int(card[0])
            card[1] = card[1].replace("&#x27;", "'")
            # Checks for singleton, ignores cards that allow multiples
            if (card[0] != 1 and (card[1] not in nonsingleton)) or (card in decklist):
                return [1, "Deck isn't singleton"]
            # Checks for banned cards
            elif (card[1] in banned):
                return [1, "Deck contains banned cards"]
            else:
                decklist.append(card)
        
        decklist = sorted(decklist, key=lambda x: x[1])
        
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
            return [1, "Deck has too few cards"]
        
        #Create a hash of the deck to compare to database
        h = hashlib.md5()
        h.update(bytes(str(decklist), "utf-8"))
        deckhash = h.hexdigest()
        
        if not path.exists("decks"):
            os.mkdir("decks")
        
        if not path.exists("decks/" + deckhash):
            with open("decks/"+deckhash, 'wb') as fp:
                pickle.dump(decklist, fp)
        
        return [0, deckhash]
        