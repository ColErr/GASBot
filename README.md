# GASBot

A work in progress Discord bot to allow for matchmaking for the MTG:Arena Gladiator format.

Currently deck-checks and adds to a queue, then will match people as the queue fills. Plans to add tournament/league standings
as well as some statistics on deck/player win percentages.

## Functions
!lfg <aetherhub deck number>:			Performs a deck check, then adds a user to the queue  
!leave:									Leaves the queue  
!report <wins> <losses>: 				Report the results of your last match  
!correction <match #> <wins> <losses>:	Allows a user to change the results of their incorrectly reported matches  
!participate:							Adds a user to the "Tournament Participant" group

## Todo
* Add tournament/league queues
* Allow decks to be imported from more websites
* More robust deck checks to handle cards outside the format, as well as cards like Seven Dwarves
* Possibly add Discord server maintenence
