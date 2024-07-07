import discord
from discord.ext import commands
from utils import info
from commands import handler
from admin import db_handler
from datetime import datetime, timezone
import random
import asyncio

class Button(discord.ui.View):
    def __init__(self, bot: commands.Bot, thread: discord.Thread, message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot 
        self.thread = thread
        self.message = message  

    @discord.ui.button(label="Physics", style=discord.ButtonStyle.green, custom_id="physics", emoji="⚛️")
    async def role_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == interaction.channel.owner_id:
            await self.thread.send(f"<@&{info.Physics}>")
            await self.message.edit(content=f"Thank you for your response {interaction.user.mention}.", view=None, embed=None, delete_after= 10)
            color = random.choice(info.colors)
            em= discord.Embed(title="Note for OP",
                            description="`+solved @user1 @user2...` to close the thread when your doubt is solved. Mention the users who helped you solve the doubt. This will be added to their stats.",
                            color=color)
            await self.thread.send(embed=em)
        else:
            await interaction.response.send_message(":x: You cannot do that.", ephemeral=True)

    @discord.ui.button(label="Chemistry", style=discord.ButtonStyle.green, custom_id="chemistry", emoji="🧪")
    async def role_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == interaction.channel.owner_id:
            await self.thread.send(f"<@&{info.Chemistry}>")
            await self.message.edit(content=f"Thank you for your response {interaction.user.mention}.", view=None, embed=None, delete_after= 10)
            color = random.choice(info.colors)
            em= discord.Embed(title="Note for OP",
                            description="`+solved @user1 @user2...` to close the thread when your doubt is solved. Mention the users who helped you solve the doubt. This will be added to their stats.",
                            color=color)
            await self.thread.send(embed=em)
        else:
            await interaction.response.send_message(":x: You cannot do that.", ephemeral=True)

    @discord.ui.button(label="Maths", style=discord.ButtonStyle.green, custom_id="maths", emoji="📏")
    async def role_three(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == interaction.channel.owner_id:
            await self.thread.send(f"<@&{info.Maths}>")
            await self.message.edit(content=f"Thank you for your response {interaction.user.mention}.", view=None, embed=None, delete_after= 10)
            color = random.choice(info.colors)
            em= discord.Embed(title="Note for OP",
                            description="`+solved @user1 @user2...` to close the thread when your doubt is solved. Mention the users who helped you solve the doubt. This will be added to their stats.",
                            color=color)
            await self.thread.send(embed=em)
        else:
            await interaction.response.send_message(":x: You cannot do that.", ephemeral=True)

    @discord.ui.button(label="Biology", style=discord.ButtonStyle.green, custom_id="biology", emoji="🦠")
    async def role_four(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == interaction.channel.owner_id:
            await self.thread.send(f"<@&{info.Biology}>")
            await self.message.edit(content=f"Thank you for your response {interaction.user.mention}.", view=None, embed=None, delete_after= 10)
            color = random.choice(info.colors)
            em= discord.Embed(title="Note for OP",
                            description="`+solved @user1 @user2...` to close the thread when your doubt is solved. Mention the users who helped you solve the doubt. This will be added to their stats.",
                            color=color)
            await self.thread.send(embed=em)
        else:
            await interaction.response.send_message(":x: You cannot do that.", ephemeral=True)

class Forum(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.forum_channel_id = info.Forum_channel_ID


    # Event called when a thread is created in the server
    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        await asyncio.sleep(4)
        if thread.parent_id == self.forum_channel_id:
            owner = thread.owner_id
            color = random.choice(info.colors)
            em = discord.Embed(title= "Choose the Study Helper subject ping",
                               description="Choose the subject for the respective doubt :)",
                               color = color)            
            message = await thread.send(f"Hello <@{owner}>!", embed=em)
            button = Button(self.bot, thread, message)
            await message.edit(view=button)
        else:
            return
        
    @commands.command(name="solved")
    async def solve(self, ctx: commands.Context, *members: commands.Greedy[discord.Member]):

        """Command for Thread owner to close the thread. Note: Users with manage threads permission can also use this command."""

        forum_channel_id = info.Forum_channel_ID
        if not members:
            await ctx.send(":x: You must specify at least one member.", delete_after=5)
            return

        seen_members = set()
        for member in members:
            if member.id == ctx.author.id:
                await ctx.send(":x: You cannot mark yourself as the solver.", delete_after=5)
                return
            if member.bot:
                await ctx.send(":x: You cannot mark a bot as the solver.", delete_after=5)
                return
            if member.id in seen_members:
                await ctx.send(f":x: {member.name} is mentioned more than once. Please mention each member only once.", delete_after=5)
                return
            seen_members.add(member.id)

        try:
            assert isinstance(ctx.channel, discord.Thread)
        except AssertionError:
            await ctx.send("This command can only be used in a thread channel.")
            return

        if ctx.channel.parent_id == info.Forum_channel_ID:
            permissions = ctx.channel.permissions_for(ctx.author)
            if ctx.author.id == ctx.channel.owner_id or permissions.manage_threads:
                if ctx.channel.locked:
                    await ctx.send("Channel is already marked 'Solved'.")
                    return

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
                            await ctx.message.add_reaction(info.Tick)
                            current_time = datetime.now(timezone.utc)
                            unix_timestamp = int(current_time.timestamp())
                            em = discord.Embed(title="Post locked and archived successfully!", color=0x575287)
                            em.add_field(name="Archived by", value=f"{ctx.author.mention} ({ctx.author.id})")
                            em.add_field(name="Time", value=f"<t:{unix_timestamp}:R>")
                            
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
                await ctx.send(":x: You cannot do that. Only the OP of the post or a user with manage threads permission can solve the thread.", delete_after=5)
        else:
            await ctx.send(f"The channel is not within the specified <#{info.Forum_channel_ID}> category.")


    @commands.command(name="reopen")
    @commands.has_permissions(manage_threads=True)
    async def reopen(self, ctx: commands.Context):

        """Unlocks a locked post. Mod only command."""

        forum_channel_id = info.Forum_channel_ID  
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send("This command can only be used in a thread channel.")
            return
        
        if ctx.channel.parent_id == forum_channel_id:
            if not ctx.channel.locked:
                await ctx.send("Channel was not locked.")
                return  
            channel = ctx.guild.get_channel(forum_channel_id)
            if channel:
                all_tags = channel.available_tags
                solved_tag = discord.utils.get(all_tags, name="Solved")
                if solved_tag:
                    applied_tags = ctx.channel.applied_tags
                    if solved_tag in applied_tags:
                        applied_tags.remove(solved_tag) # Removed the "Solved" Tag from the post to avoid conflicts when it is closed again.
                    thread_id = ctx.channel.id  
                    thread = discord.utils.get(channel.threads, id=thread_id)
                    if thread:
                        current_time = datetime.now(timezone.utc)
                        unix_timestamp = int(current_time.timestamp())
                        await thread.edit(locked=False, archived=False, applied_tags=applied_tags)
                        em = discord.Embed(title="Post unlocked and unarchived successfully!", color=0x575287)
                        em.add_field(name="Unarchived by", value=f"{ctx.author.mention} ({ctx.author.id})")
                        em.add_field(name="Time", value=f"<t:{unix_timestamp}:R>")
                        await ctx.message.add_reaction(info.Tick)
                        await ctx.send(embed=em)
                    else:
                        await ctx.send("Thread not found.")
                else:
                    await ctx.send("The 'Solved' tag was not found.")
            else:
                await ctx.send("The forum channel is not found.")
        else:
            await ctx.send("The channel is not within the specified category.")


    @solve.error
    async def on_solve_error(self, ctx, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You need to mention a member to mark the thread as solved. \n\n`+solved @user`. This will be added to their stats.") # Different message respone on missing arguments for the solved command.

async def setup(bot):
    await bot.add_cog(Forum(bot))