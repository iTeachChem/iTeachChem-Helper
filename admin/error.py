import discord
from discord.ext import commands
import random
from utils import info
import aiosqlite

class Error(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.error_channel_id = info.ERROR_LOG_CHANNEL_ID

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found! Use `+help` to view all available commands", delete_after=5)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            # param = error.param.name
            # await ctx.reply(f"Missing required argument \n\n '{param}'.", delete_after=10)
            return

        elif isinstance(error, commands.BadArgument):
            await ctx.reply(":no_entry_sign: | Invalid Arguments", delete_after=10)

        elif isinstance(error, commands.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            await ctx.reply(f"You do not have permission to use this command. \n\nMissing permissions: `{missing_perms}`.", delete_after=10)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f"I do not have the necessary permissions to perform this action. \n\nMissing permissions: `{error.missing_permissions}`", delete_after=10)

        elif isinstance(error, commands.CommandOnCooldown):
            if await cooldown_exempt(ctx):
                await ctx.reinvoke()
            else:
                greet = random.choice(info.greet)
                cooldown_time = await format(error.retry_after)
                await ctx.reply(f"{greet} This command is on cooldown. Try again in {cooldown_time}.", delete_after=10)
        
        elif isinstance(error, aiosqlite.Error):
            await self.log_aiosqlite_error(ctx, error)
        
        else:
            await self.log_command_error(ctx, error)

    async def log_command_error(self, ctx, error):
        error_channel = self.bot.get_channel(self.error_channel_id)
        if error_channel:
            embed = discord.Embed(title="Command Error Occurred", color=discord.Color.red())
            embed.add_field(name="Error Type", value=type(error).__name__, inline=False)
            embed.add_field(name="Error Message", value=str(error), inline=False)
            embed.add_field(name="Context", value=f"User: {ctx.author} (ID: {ctx.author.id})\nChannel: {ctx.channel.name} (ID: {ctx.channel.id})\nServer: {ctx.guild.name} (ID: {ctx.guild.id})\nCommand: {ctx.message.content}", inline=False)
            await error_channel.send(embed=embed)

    async def log_aiosqlite_error(self, ctx, error):
        error_channel = self.bot.get_channel(self.error_channel_id)
        if error_channel:
            embed = discord.Embed(title="Database Error Occurred", color=discord.Color.red())
            embed.add_field(name="Error Type", value=type(error).__name__, inline=False)
            embed.add_field(name="Error Message", value=str(error), inline=False)
            embed.add_field(name="Context", value=f"User: {ctx.author} (ID: {ctx.author.id})\nChannel: {ctx.channel.name} (ID: {ctx.channel.id})\nServer: {ctx.guild.name} (ID: {ctx.guild.id})\nCommand: {ctx.message.content}", inline=False)
            await error_channel.send(embed=embed)
        await ctx.reply("An error occurred while accessing the database. The issue has been logged and will be investigated.", delete_after=10)

    async def log_error(self, error):
        error_channel = self.bot.get_channel(self.error_channel_id)
        if error_channel:
            embed = discord.Embed(title="Unhandled Error Occurred", color=discord.Color.red())
            embed.add_field(name="Error Type", value=type(error).__name__, inline=False)
            embed.add_field(name="Error Message", value=str(error), inline=False)
            await error_channel.send(embed=embed)

async def cooldown_exempt(ctx: commands.Context):
    exempt_users = info.OWNER_IDS  
    return ctx.author.id in exempt_users

async def format(retry_after):
    hours, remainder = divmod(int(retry_after), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}H {minutes}M {seconds}S"

async def setup(bot):
    await bot.add_cog(Error(bot))