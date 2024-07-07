import discord
from discord.ext import commands, tasks
from utils import info
from admin import db_handler
from commands import handler
from datetime import datetime
import aiosqlite
import os

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx: commands.Context, activity: str, *, status: str):
        permissions = ctx.channel.permissions_for(ctx.author)
        if ctx.author.id in info.OWNER_IDS or permissions.administrator:
            activity = activity.lower()
            if activity == "playing" or activity == "p":
                await ctx.bot.change_presence(activity=discord.Game(name=status))
            elif activity == "listening" or activity == "l":
                await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
            elif activity == "watching" or activity == "w":
                await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
            elif activity == "custom" or activity == "c":
                custom_activity = discord.CustomActivity(name=status)
                await ctx.bot.change_presence(activity=custom_activity)
            else:
                await ctx.send("Invalid activity type. Please choose one of 'playing', 'listening', 'watching' or 'custom'.")
                return

            await ctx.send(f"Status set to \n**Activity:** {activity} \n**Status:** '{status}'")
        else:
            return

    @commands.command(name="fsolved")
    @commands.has_guild_permissions(manage_threads=True)
    async def fsolve(self, ctx: commands.Context, *members: commands.Greedy[discord.Member]):
        forum_channel_id = info.Forum_channel_ID  
        try:
            assert isinstance(ctx.channel, discord.Thread)
        except AssertionError:
            await ctx.send("This command can only be used in a thread channel.")
            return

        if members:
            for member in members:
                if member.id == ctx.author.id:
                    await ctx.send(":x: You cannot mark yourself as the solver.", delete_after=5)
                    return
                if member.bot:
                    await ctx.send(":x: You cannot mark a bot as the solver.", delete_after=5)
                    return

        if ctx.channel.parent_id == info.Forum_channel_ID:
            channel = ctx.guild.get_channel(forum_channel_id)
            if channel:
                all_tags = channel.available_tags 
                solved_tag = discord.utils.get(all_tags, name="Solved")
                tags = ctx.channel.applied_tags
                if solved_tag:
                    tags_to_add = [solved_tag] + tags
                    thread_id = ctx.channel.id  
                    thread = discord.utils.get(channel.threads, id=thread_id)
                    if thread:
                        current_time = datetime.now()
                        unix_timestamp = int(current_time.timestamp())
                        em = discord.Embed(title="Post locked and archived successfully!", color= 0x575287)
                        em.add_field(name="Archived by", value=f"{ctx.author.mention} ({ctx.author.id})")
                        em.add_field(name="Time", value=f"<t:{unix_timestamp}:R>")
                        if members:
                            solved_by_mentions = ', '.join([f"{member.mention} ({member.id})" for member in members])
                            em.add_field(name="Solved by", value=solved_by_mentions)
                        
                        await ctx.send(embed=em)
                        await thread.edit(locked=True, archived=True, applied_tags=tags_to_add)
                        
                        for member in members:
                            check = await handler.check_user_in_main(member)
                            if check:
                                await db_handler.update_user_data(member, "doubts_solved", 1)
                            else:
                                await handler.add_user_in_main(member)
                                await db_handler.update_user_data(member, "doubts_solved", 1)
                    else:
                        await ctx.send("Thread not found.")
                else:
                    await ctx.send("The 'Solved' tag was not found.")
            else:
                await ctx.send("The forum channel is not found.")
        else:
            await ctx.send("The channel is not within the specified category.")

    @commands.group(name="set", aliases=['s'])
    @commands.has_permissions(administrator=True)
    async def set(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Subcommand not found!', delete_after=5)

    @set.command(name="doubts")
    async def doubt(self, ctx: commands.Context, user: discord.User, number: int):
        check = await handler.check_user_in_main(user)
        if check is True:
            process = await db_handler.update_user_data(user, "doubts_solved", number)
            if process is True:
                await ctx.send(f"Doubts set to `{number}` for {user.name} ({user.id})")
            else:
                await ctx.send(f"An error occurred! \nError code: `D01`")
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in the database.")
        else:
            await ctx.send("Error!")

    @set.command(name="solved")
    async def solved(self, ctx: commands.Context, user: discord.User, number: int):
        check = await handler.check_user_in_main(user)
        if check is True:
            process = await db_handler.update_user_data(user, "questions_solved", number)
            if process is True:
                await ctx.send(f"Questions solved set to `{number}` for {user.name} ({user.id})")
            else:
                await ctx.send(f"An error occurred! \nError code: `D02`")
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in the database.")
        else:
            await ctx.send("Error!")

    @set.command(name="attempted")
    async def attempted(self, ctx: commands.Context, user: discord.User, number: int):
        check = await handler.check_user_in_main(user)
        if check is True:
            process = await db_handler.update_user_data(user, "questions_attempted", number)
            if process is True:
                await ctx.send(f"Questions attempted set to `{number}` for {user.name} ({user.id})")
            else:
                await ctx.send(f"An error occurred! \nError code: `D03`")
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in the database.")
        else:
            await ctx.send("Error!")

    @set.command(name="points")
    async def points(self, ctx: commands.Context, user: discord.User, number: int):
        check = await handler.check_user_in_main(user)
        if check is True:
            process = await db_handler.update_user_data(user, "points", number)
            if process is True:
                await ctx.send(f"Points set to `{number}` for {user.name} ({user.id})")
            else:
                await ctx.send(f"An error occurred! \nError code: `D04`")
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in the database.")
        else:
            await ctx.send("Error!")

    @set.command(name="skipped")
    async def skipped(self, ctx: commands.Context, user: discord.User, number: int):
        check = await handler.check_user_in_main(user)
        if check is True:
            process = await db_handler.update_user_data(user, "questions_skipped", number)
            if process is True:
                await ctx.send(f"Questions skipped set to `{number}` for {user.name} ({user.id})")
            else:
                await ctx.send(f"An error occurred! \nError code: `D05`")
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in the database.")
        else:
            await ctx.send("Error!")
    
    @commands.group(name="user")
    @commands.is_owner()
    async def user_set(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Subcommand not found!', delete_after=5)

    @user_set.command(name="add")
    async def user_add(self, ctx: commands.Context, user: discord.User):
        check = await handler.check_user_in_main(user)
        if check is False:
            result = await handler.add_user_in_main(user)
            if result:
                await ctx.send(f"{user.global_name} ({user.id}) added to main data")
            else:
                await ctx.send("Error!")
        elif check is True:
            await ctx.send(f"User {user.name} ({user.id}) is already in the database.")
        else:
            await ctx.send("Error!")

    @user_set.command(name="remove")
    async def remove(self, ctx: commands.Context, user: discord.User):
        check = await handler.check_user_in_main(user)
        if check is True:
            await db_handler.remove_user_data(ctx, user)
        elif check is False:
            await ctx.send(f"User {user.name} ({user.id}) not found in database.")
        else:
            await ctx.send("Error!")

    @commands.command(name="info")
    @commands.has_permissions(administrator=True)
    async def info(self, ctx: commands.Context):
        forum_channel_id = info.Forum_channel_ID
        forum_channel = ctx.guild.get_channel(forum_channel_id)
        
        if not forum_channel or not isinstance(forum_channel, discord.ForumChannel):
            await ctx.send("The specified channel is not a valid forum channel.")
            return
        
        main_threads = len(forum_channel.threads)
        archived_threads = await self.fetch_archived_threads(forum_channel)
        solved_threads = await self.count_solved_threads(forum_channel)
        total_threads = main_threads + archived_threads

        await ctx.send(f"Total Doubt Posts: {total_threads}\nActive Doubt Posts: {main_threads}\nArchived: {archived_threads}\nSolved Doubts: {solved_threads}")

    async def fetch_archived_threads(self, forum_channel: discord.ForumChannel):
        archived_threads = []
        async for thread in forum_channel.archived_threads(limit=1000):
            archived_threads.append(thread)
        return len(archived_threads)

    async def count_solved_threads(self, forum_channel: discord.ForumChannel):
        solved_threads = 0
        try:
            async for thread in forum_channel.archived_threads(limit=1000):
                all_tags = forum_channel.available_tags
                solved_tag = discord.utils.get(all_tags, name="Solved")
                archive = thread.archived 
                if archive and solved_tag in thread.applied_tags:
                    solved_threads += 1
        except Exception as e:
            print(f"Error counting solved threads: {e}")
        return solved_threads

async def setup(bot):
    await bot.add_cog(Admin(bot))
