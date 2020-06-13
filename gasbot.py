import discord
from datetime import datetime, timedelta
from discord.ext import commands
import sqlite3

from deck import Deck

class GASBot:
    
    def __init__(self, bot_token, database):
        self.token = bot_token
        self.database = database
        self.lastResetTime = datetime.now()
        
        self.lfgQueue = []
        
        self.bot = commands.Bot(command_prefix="!", case_insensitive=True)
        
    def run(self):
        self.setup_commands()
        self.setup_cogs()
        self.setup_listeners()
        
        self.bot.run(self.token)
        
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
            
            if len(self.lfgQueue) == 0:
                self.lfgQueue.append([ctx.author.id, deckID])
                await ctx.send("You have joined the queue")
            else:
                match = self.lfgQueue.pop(0)
                opp = await self.bot.fetch_user(match[0])
                message = ctx.author.mention + ", you are playing " + opp.mention
                await ctx.send(message)
            
    def setup_cogs(self):
        return
        
    