import discord
import os
import traceback
from os.path import isfile
from datetime import datetime, timedelta
from discord.ext import commands
import sqlite3

from deck import Deck

class GASBot:
    
    def __init__(self, bot_token, databasename):
        self.token = bot_token
        self.lastResetTime = datetime.now()
        self.setup_db(databasename)
        
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
        
        @self.bot.event
        async def on_command_error(ctx, error):
            print(f"Handling error {error}")
            if isinstance(error, commands.CommandNotFound):
                print(f"Command {ctx.command.name} not found")
                return
            elif isinstance(error, commands.MissingRequiredArgument):
                print("Command missing arguments")
                await ctx.send(ctx.command.help)
            else:
                print(traceback.format_exc())
        
    
    def setup_commands(self):
        def check_only_me():
            def predicate(ctx):
                return ctx.message.author.id == 92305780048420864
            return commands.check(predicate)
        
        @self.bot.command(name="register")
        async def register(ctx, arenaname):
            c = self.database.cursor()
            c.execute("SELECT count(id) FROM players WHERE id = ?", (ctx.author.id, ))
            if c.fetchone()[0] != 1:
                self.database.execute('''
                INSERT INTO players(id, arenaname, matchwins, matchlosses) 
                VALUES(?, ?, 0, 0);
                ''', (ctx.author.id, arenaname))
                self.database.commit()
                await ctx.send(f"{ctx.author.mention}, you have successfully registered")
            else:
                await ctx.send(f"{ctx.author.mention}, you have already registered")
            return
        
        @self.bot.command(name="shutdown")
        @check_only_me()
        async def shutdown(ctx):
            print("I was asked to shutdown")
            await self.bot.close()
            
        @self.bot.command(name="reloadcog")
        @check_only_me()
        async def reloadext(ctx, cog):
            self.bot.reload_extension("cogs." + cog)
            await ctx.send(f"Cog {cog} has been reloaded")
            return
            
        @self.bot.command(name="loadcog")
        @check_only_me()
        async def loadext(ctx, cog):
            self.bot.load_extension("cogs." + cog)
            await ctx.send(f"Cog {cog} has been loaded")
            return
            
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
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = []
        for table in c:
            tables.append(table[0])
        
        print(tables)
        
        if "matches" not in tables:
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
        if "players" not in tables:
            self.database.execute('''
                CREATE TABLE players(
                id INT PRIMARY KEY,
                arenaname TEXT NOT NULL,
                matchwins INT NOT NULL,
                matchlosses INT NOT NULL);
            ''')
            print("Created matches table")
        
        return
    
    def setup_cogs(self):
        for cog in os.listdir("cogs"):
            if isfile("cogs/" + cog):
                self.bot.load_extension("cogs." + cog[:-3])
        return
        
    