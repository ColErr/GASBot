import discord
from discord.ext import commands
from discord.utils import get

class ModCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="participate", help="Assigns the Tournament Participant Role")
    async def participate(self, ctx):
        role = get(ctx.guild.roles, name="Tournament Participant")
        
        if role not in ctx.author.roles: #User doesn't have role, add it
            await ctx.author.add_roles(role, reason="Requested by user")
            await ctx.send(f"{ctx.author.mention}, you joined Tournament Participant")
        else: #User does have role, remove it
            await ctx.author.remove_roles(role, reason="Requested by user")
            await ctx.send(f"{ctx.author.mention}, you left Tournament Participant")
        
        return
    
def setup(bot):
    bot.add_cog(ModCog(bot))