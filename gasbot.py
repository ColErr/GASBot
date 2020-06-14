import discord
from datetime import datetime, timedelta
from discord.ext import commands
import sqlite3

from deck import Deck

class GASBot:
    
    def __init__(self, bot_token, databasename):
        self.token = bot_token
        self.lastResetTime = datetime.now()
        self.setup_db(databasename)
        
        self.lfgqueue = []
        
        self.bot = commands.Bot(command_prefix="!", case_insensitive=True)
        
    def run(self):
        self.setup_commands()
        self.setup_cogs()
        self.setup_listeners()
        
        self.bot.run(self.token)
        
        self.database.close()
        
    def setup_listeners(self):
        @self.bot.event
        async def on_ready():
            print(f"{self.bot.user.name} has connected")
            for guild in self.bot.guilds:
                print(f"Joined {guild.name}")
        
    
    def setup_commands(self):
        def check_only_me():
            def predicate(ctx):
                return ctx.message.author.id == 92305780048420864
            return commands.check(predicate)
        
        @self.bot.command(name="shutdown")
        @check_only_me()
        async def shutdown(ctx):
            print("I was asked to shutdown")
            await self.bot.close()
            
        @self.bot.command(name="lfg")
        async def lfg(ctx, decknum):
            async with ctx.channel.typing():
                deckID = Deck.importDeck(decknum)
            
            if len(self.lfgqueue) == 0:
                self.lfgqueue.append([ctx.author.id, deckID])
                await ctx.send("You have joined the queue")
            else:
                match = self.lfgqueue.pop(0)
                opp = await self.bot.fetch_user(match[0])
                self.database.execute('''
                    INSERT INTO matches(player1, p1deck, p1wins, p1confirm, player2, p2deck, p2wins, p2confirm)
                    VALUES(?, ?, 0, 0, ?, ?, 0, 0);
                    ''', (match[0], match[1], ctx.author.id, deckID))
                self.database.commit()
                message = ctx.author.mention + ", you are playing " + opp.mention
                await ctx.send(message)
            return
            
        @self.bot.command(name="leavequeue")
        async def leavequeue(ctx):
            i=0
            for x in self.lfgqueue:
                if ctx.author.id == x[0]:
                    self.lfgqueue.pop(i)
                    await ctx.send(ctx.author.mention + ", you have been dropped from the queue")
                    return
                else:
                    i += 1
            await ctx.send(ctx.author.mention + ", you are not in the queue")
            
    def setup_db(self, name):
        self.database = None
        # Establish DB connection
        try:
            self.database = sqlite3.connect(name)
        except Error as e:
            print(e)
            quit()
        
        # Check to see if tables are set up
        c = self.database.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='matches' ")
        if c.fetchone()[0] != 1:
            self.database.execute('''
                CREATE TABLE matches(
                id INTEGER PRIMARY KEY,
                player1 INT NOT NULL,
                p1deck TEXT NOT NULL,
                p1wins INT NOT NULL,
                p1confirm NUMERIC,
                player2 INT NOT NULL,
                p2deck TEXT NOT NULL,
                p2wins INT NOT NULL,
                p2confirm NUMERIC);
            ''')
            print("Created matches table")
        else:
            c.execute
        
        return
    
    def setup_cogs(self):
        return
        
    