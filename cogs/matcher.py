import sqlite3
import discord
import os
from discord.ext import commands

from deck import Deck

class MatcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lfgqueue = []
        self.connectdb()
        
    def connectdb(self):
        self.database = None
        name = os.getenv("DB_NAME")
        # Establish DB connection
        try:
            self.database = sqlite3.connect(name)
        except Error as e:
            print(e)
            quit()
    
    @commands.command(name="lfg", help="Join the LFG queue with !lfg <aetherhub deck number>")
    async def lfg(self, ctx, decknum: int):
        for x in self.lfgqueue:
            if ctx.author.id == x[0]:
                await ctx.send(f"{ctx.author.mention}, you are already in the queue")
                return
        
        c = self.database.cursor()
        
        c.execute('''
            SELECT arenaname FROM players
            WHERE id = ?;
        ''', (ctx.author.id, ))
        
        result = c.fetchone()
        if result == None:
            await ctx.send(f"{ctx.author.mention}, please register with !register <arena name> before joining")
            return
        arenaname = result[0]
        
        c.execute('''
            SELECT player1, p1confirm, player2, p2confirm FROM matches
            WHERE player1 = ? OR player2 = ?
            ORDER BY id DESC LIMIT 1;
            ''', (ctx.author.id, ctx.author.id))
        result = c.fetchone()
        
        if result != None:
            if ((result[0] == ctx.author.id) and (result[1] == 0)) or ((result[2] == ctx.author.id) and (result[3] == 0)):
                await ctx.send(f"{ctx.author.mention}, please report your last match with !report <wins> <losses>")
                return
        
        async with ctx.channel.typing():
            deckcheck = Deck.importDeck(str(decknum))
        
        if deckcheck[0] > 0:
            await ctx.send(f"{ctx.author.mention}, deck check failed: {deckcheck[1]}")
            return
        
        if len(self.lfgqueue) == 0:
            self.lfgqueue.append([ctx.author.id, deckcheck[1], arenaname])
            await ctx.send(f"{ctx.author.mention}, you have joined the queue")
        else:
            match = self.lfgqueue.pop(0)
            opp = await self.bot.fetch_user(match[0])
            self.database.execute('''
                INSERT INTO matches(player1, p1deck, p1wins, p1confirm, player2, p2deck, p2wins, p2confirm)
                VALUES(?, ?, 0, 0, ?, ?, 0, 0);
                ''', (match[0], match[1], ctx.author.id, deckcheck[1]))
            self.database.commit()
            await ctx.send(f"{ctx.author.mention} ({arenaname}), you are playing {opp.mention} ({match[2]})")
        return
        
    @commands.command(name="report", help="Report your match result with !report <wins> <losses>")
    async def report(self, ctx, wins: int, losses: int):
        c = self.database.cursor()
        c.execute('''
            SELECT id, player1, p1confirm, p1wins, player2, p2confirm, p2wins FROM matches
            WHERE player1 = ? OR player2 = ?
            ORDER BY id DESC LIMIT 1;
            ''', (ctx.author.id, ctx.author.id))
        result = c.fetchone()
        
        if result == None:
            await ctx.send(f"No matches found for {ctx.author.mention}")
            return
        
        if result[1] == ctx.author.id:
            if result[2] == 1:
                await ctx.send(f"{ctx.author.mention}, you have already reported your last match")
                return
            if result[5] == 1:
                if (result[3] != wins) or (result[6] != losses):
                    await ctx.send(f"{ctx.author.mention}, there is a mismatch with your last opponent. They reported {result[3]}-{result[6]} for match #{result[0]}")
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
                await ctx.send(f"{ctx.author.mention}, you have already reported your last match")
                return
            if result[2] == 1:
                if (result[6] != wins) or (result[3] != losses):
                    await ctx.send(f"{ctx.author.mention}, there is a mismatch with your last opponent. They reported {result[6]}-{result[3]} for match #{result[0]}")
                    return
            self.database.execute('''
                UPDATE matches SET
                p2confirm = 1, 
                p1wins = ?, 
                p2wins = ?
                WHERE id = ?;
            ''', (losses, wins, result[0]))
        
        self.database.commit()
        await ctx.send(f"{ctx.author.mention}, your match result has been recorded")
        return
    
    @commands.command(name="correction", help="Correct the record on a previous match with !correction <match #> <wins> <losses>")
    async def correctmatch(self, ctx, matchnum: int, wins: int, losses: int):
        c = self.database.cursor()
        c.execute('''
            SELECT player1, p1confirm, player2, p2confirm FROM matches
            WHERE id = ?;
            ''', (matchnum,))
        result = c.fetchone()
        
        if ctx.author.id != result[0] and ctx.author.id != result[2]:
            await ctx.send(f"{ctx.author.mention}, that was not your match")
            return
        
        if ctx.author.id == result[0]:
            if result[1] == 0:
                await ctx.send(f"{ctx.author.mention}, you haven't reported that match")
            if result[3] == 1:
                await ctx.send(f"{ctx.author.mention}, your opponent already confirmed that match")
                return
            self.database.execute('''
                UPDATE matches SET
                p1wins = ?,
                p2wins = ?
                WHERE id = ?;
            ''', (wins, losses, matchnum))
        else:
            if result[3] == 0:
                await ctx.send(f"{ctx.author.mention}, you haven't reported that match")
            if result[1] == 1:
                await ctx.send(f"{ctx.author.mention}, your opponent already confirmed that match")
                return
            self.database.execute('''
                UPDATE matches SET
                p1wins = ?,
                p2wins = ?
                WHERE id = ?;
            ''', (losses, wins, matchnum))
        self.database.commit()
        await ctx.send(f"{ctx.author.mention}, the match has been updated")
    
    @commands.command(name="leave", help="Leave the current queue")
    async def leavequeue(self, ctx):
        i=0
        for x in self.lfgqueue:
            if ctx.author.id == x[0]:
                self.lfgqueue.pop(i)
                await ctx.send(f"{ctx.author.mention}, you have been dropped from the queue")
                return
            else:
                i += 1
        await ctx.send(f"{ctx.author.mention}, you are not in the queue")

def setup(bot):
    bot.add_cog(MatcherCog(bot))