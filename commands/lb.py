import discord
from discord.ext import commands
from commands import quiz, handler
from utils import info

class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="leaderboard", aliases=['lb'])
    async def lbd(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Subcommand not found! Use `+lb doubts` or `+lb quiz`', delete_after=5)

    @lbd.command(name="doubts")
    async def doubts_lb(self, ctx: commands.Context):
        embed = await handler.get_doubts_leaderboard(ctx.author, ctx)
        await ctx.send(embed=embed)

    @lbd.command(name="quiz")
    async def quiz_lb(self, ctx: commands.Context):
        embed = await handler.get_questions_leaderboard(ctx.author, ctx)
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.channel.id in info.restricted:
            return
        if member is None:
            member = ctx.author
        try:
            check_user = await handler.check_user_in_main(member)
            if check_user:
                get_data = await handler.get_user_data(member)
                if get_data:
                    doubts_solved, questions_attempted, questions_solved, questions_skipped, points = map(int, get_data[:-1])
                    total_time_taken = float(get_data[-1])
                    quiz_rank = await handler.get_user_rank_for_quiz(member)
                    doubts_rank = await handler.get_user_rank_for_doubts(member)
                    correct_percent = percentage(questions_solved, questions_attempted)
                    skip_percent = percentage(questions_skipped, questions_attempted)
                    av_score = average(points, questions_solved)
                    av_time = average(total_time_taken, questions_attempted)
                    av_time_formatted = quiz.time_calculate_convert(av_time)
                    time_formatted = quiz.time_calculate_convert(total_time_taken)
                    em = discord.Embed(title=f"{member.name}'s stats", color=0xeea990)
                    em.set_thumbnail(url=member.display_avatar.url)
                    em.add_field(name="Doubts solved", value=f"{doubts_solved}")
                    em.add_field(name="Questions attempted", value=f"{questions_attempted}")
                    em.add_field(name="Questions solved", value=f"{questions_solved}")
                    em.add_field(name="Questions skipped", value=f"{questions_skipped}")
                    em.add_field(name="Points", value=f"{points}")
                    em.add_field(name="Total time taken", value=f"{time_formatted}\n\n")
                    em.add_field(name=f"You have correctly solved {correct_percent:.2f}% of all questions attempted ({skip_percent:.2f}% skipped).\nAverage points scored: {av_score:.2f}\nAverage time spent on all questions: {av_time_formatted}", inline=False, value="")
                    em.set_footer(text=f"Rank: #{quiz_rank} in Quizzes | #{doubts_rank} in doubts")
                    em.timestamp = discord.utils.utcnow()
                    await ctx.send(embed=em)
                else:
                    await ctx.send(f"No data found for {member.name}.")
            else:
                await ctx.send(f"There are no stats found for {member.name} ({member.id}).")
        except commands.BadArgument:
            await ctx.send("Invalid user provided.")
        except ValueError:
            await ctx.send("Data conversion error")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def percentage(num: int, deno: int) -> float:
    if deno == 0:
        return 0.0
    return (num / deno) * 100

def average(points: float, total_number: int) -> float:
    if total_number == 0:
        return 0.0
    return points / total_number

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))