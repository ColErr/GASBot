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
            
        @self.bot.command(name="report")
        async def report(ctx, wins: int, losses: int):
            c = self.database.cursor()
            c.execute('''
                SELECT id, player1, p1confirm, p1wins, player2, p2confirm, p2wins FROM matches
                WHERE player1 = ? OR player2 = ?
                ORDER BY id DESC LIMIT 1;
                ''', (ctx.author.id, ctx.author.id))
            result = c.fetchone()
            
            if result == None:
                await ctx.send("No matches found for " + ctx.author.mention)
                return
            
            if result[1] == ctx.author.id:
                if result[2] == 1:
                    await ctx.send(ctx.author.mention + ", you have already reported your last match")
                    return
                if result[5] == 1:
                    if (result[3] != wins) or (result[6] != losses):
                        await ctx.send(ctx.author.mention + ", there is a mismatch with your last opponent")
                        return
                self.database.execute('''
                    UPDATE matches SET
                    p1confirm = 1, 
                    p1wins = ?, 
                    p2wins = ?
                    WHERE id = ?;
                ''', (wins, losses, result[0]))
            else:
                if result[5] == 1:
                    await ctx.send(ctx.author.mention + ", you have already reported your last match")
                    return
                if result[2] == 1:
                    if (result[6] != wins) or (result[3] != losses):
                        await ctx.send(ctx.author.mention + ", there is a mismatch with your last opponent")
                        return
                self.database.execute('''
                    UPDATE matches SET
                    p2confirm = 1, 
                    p1wins = ?, 
                    p2wins = ?
                    WHERE id = ?;
                ''', (losses, wins, result[0]))
            
            self.database.commit()
            await ctx.send(ctx.author.mention + ", your match result has been recorded")
            return
        
        @self.bot.command(name="leave")
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
        
    