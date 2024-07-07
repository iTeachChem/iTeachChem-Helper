import discord
from discord.ext import commands
from utils import info

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="help")
    async def help_(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await help_default(ctx)

    @help_.command(name="admin")
    async def admin_help(self, ctx: commands.Context):
        permissions = ctx.channel.permissions_for(ctx.author)
        if permissions.administrator:
            embed = info.Admin_help_embed
            await ctx.send(embed=embed)
        else:
            return
        
    @help_.error
    async def help_error(self, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, commands.CommandNotFound):
                return
        raise error

async def help_default(ctx: commands.Context):

    em = info.Help_embed
    await ctx.send(embed=em) 

async def setup(bot):
    await bot.add_cog(Help(bot))
