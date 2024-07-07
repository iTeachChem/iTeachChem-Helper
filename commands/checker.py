import discord
from discord.ext import commands
from utils import info
from datetime import datetime, timedelta, timezone
import random

TIMEZONE = '+05:30'

class Checker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.forum_channel_id = info.Forum_channel_ID

    
    @commands.command(name='check') 
    async def check_active_threads(self, ctx: commands.Context):

        """Returns all the active threads in the Forum Channel from the last 24 hours."""

        forum_channel = ctx.bot.get_channel(int(info.Forum_channel_ID))
        if forum_channel:
            active_threads = []
            now = datetime.now(timezone.utc) + timedelta(hours=int(TIMEZONE[1:3]), minutes=int(TIMEZONE[4:]))
            for thread in forum_channel.threads:
                if not thread.archived and not thread.locked and (now - thread.created_at.replace(tzinfo=timezone.utc)) < timedelta(days=1):
                    created_time = int(thread.created_at.timestamp())
                    owner_name = thread.owner.name
                    tag_names = [tag.name for tag in thread.applied_tags]
                    active_threads.append(( thread.name, thread.jump_url, tag_names, owner_name, created_time)) 
            if active_threads:
                color = random.choice(info.colors)
                embed = discord.Embed(title=f"Active Threads in {forum_channel.name}", color=color)
                for name, url, tags, owner_name, created_time in active_threads:
                    embed.add_field(name=name, value=f"OP: {owner_name}\nTags: {' '.join(tags)}\nLink: {url}\nCreated: <t:{created_time}:R>", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f'No active threads in #{forum_channel.name} created within the last day.')
        else:
            await ctx.send("Could not find the forum channel.")


    @commands.command(name='unsolved')
    async def check_unsolved_threads(self, ctx: commands.Context):

        """Returns all the active threads in the Forum Channel from the last 7 Days."""

        forum_channel = ctx.bot.get_channel(int(info.Forum_channel_ID))
        if forum_channel:
            unsolved_threads = []
            now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            one_week_ago = now - timedelta(days=7)
            
            for thread in forum_channel.threads:
                if (not thread.archived and not thread.locked and 
                    one_week_ago < thread.created_at.replace(tzinfo=timezone.utc) <= now and
                    not any(tag.name.lower() == "solved" for tag in thread.applied_tags)):
                    created_time = int(thread.created_at.timestamp())
                    owner_name = thread.owner.name if thread.owner else "Unknown"
                    tag_names = [tag.name for tag in thread.applied_tags]
                    unsolved_threads.append((thread.name, thread.jump_url, tag_names, owner_name, created_time))
            
            if unsolved_threads:
                color = random.choice(info.colors)
                embeds = []
                embed = discord.Embed(title=f"Unsolved Threads in {forum_channel.name} (Last Week)", color=color)
                
                for i, (name, url, tags, owner_name, created_time) in enumerate(unsolved_threads):
                    if i > 0 and i % 25 == 0:
                        embeds.append(embed)
                        embed = discord.Embed(title=f"Unsolved Threads in {forum_channel.name} (Last Week) - Continued", color=color)
                    
                    embed.add_field(name=name, value=f"OP: {owner_name}\nTags: {' '.join(tags)}\nLink: {url}\nCreated: <t:{created_time}:R>", inline=False)
                
                embeds.append(embed)
                
                for embed in embeds:
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f'No unsolved threads in #{forum_channel.name} created within the last week.')
        else:
            await ctx.send("Could not find the forum channel.")


    @commands.command(name='threads')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def check_user_threads(self, ctx: commands.Context, member: discord.Member = None):

        """Returns last 15 posts made by the user who used the command."""

        member = member or ctx.author
        forum_channel_id = info.Forum_channel_ID
        forum_channel = ctx.guild.get_channel(forum_channel_id)
        
        if forum_channel:
            active_threads = forum_channel.threads
            archived_threads = forum_channel.archived_threads(limit=1000)
            total_archived_user_threads = []
            async for thread in archived_threads:
                if thread.owner_id == member.id:
                    total_archived_user_threads.append(thread)
            
            total_active_user_threads = [thread for thread in active_threads if thread.owner_id == member.id]
            total_user_threads = total_active_user_threads + total_archived_user_threads
            
            total_threads_count = len(total_user_threads)
            solved_threads_count = sum(1 for thread in total_user_threads if any(tag.name.lower() == "solved" for tag in thread.applied_tags))
            total_user_threads.sort(key=lambda t: t.created_at, reverse=True)
            recent_user_threads = total_user_threads[:15]

            if recent_user_threads:
                color = random.choice(info.colors)
                embed = discord.Embed(title=f"Last 15 Doubt threads made by {member.name}", color=color)
                
                for thread in recent_user_threads:
                    
                    if not any(tag.name.lower() == "solved" for tag in thread.applied_tags):
                        created_time = int(thread.created_at.timestamp())
                        tag_names = [tag.name for tag in thread.applied_tags]
                        embed.add_field(
                            name=thread.name, 
                            value=f"Tags: {', '.join(tag_names)}\nLink: [Jump to thread]({thread.jump_url})\nCreated: <t:{created_time}:R>", 
                            inline=False
                        )

                    if any(tag.name.lower() == "solved" for tag in thread.applied_tags):
                        created_time = int(thread.created_at.timestamp())
                        tag_names = [tag.name for tag in thread.applied_tags]
                        embed.add_field(
                            name=thread.name, 
                            value=f"Tags: {', '.join(tag_names)}\nLink: [Jump to thread]({thread.jump_url})\nCreated: <t:{created_time}:R>", 
                            inline=False
                        )

                embed.set_footer(text=f"Total Doubts made: {total_threads_count} | Total Doubts solved: {solved_threads_count}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No threads found for {member.name} in #{forum_channel.name}.")
        else:
            await ctx.send("Could not find the forum channel.")

async def setup(bot):
    await bot.add_cog(Checker(bot))