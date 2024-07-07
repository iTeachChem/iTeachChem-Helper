import discord
from discord.ext import commands
import aiosqlite
from utils import info
from commands import quiz

async def create_table(message_id: int):
    async with aiosqlite.connect("handler.db") as db:
        await db.execute(f'''
            CREATE TABLE IF NOT EXISTS table_{message_id} (
                user_id INTEGER PRIMARY KEY,
                questions_attempted INTEGER,
                Questions_solved INTEGER,
                Questions_skipped INTEGER,
                points INTEGER,
                time TEXT
            )
        ''')
        await db.commit()
        return True

async def add_user_in_handler(message_id: int, user: discord.User):
    async with aiosqlite.connect("handler.db") as db:
        cursor = await db.cursor()
        
        await cursor.execute(f'''
            INSERT INTO table_{message_id} (user_id, questions_attempted, Questions_solved, Questions_skipped, points, time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user.id, 0, 0, 0, 0, "0"))
        
        await db.commit()
        return True


async def add_user_in_main(user: discord.User):
    async with aiosqlite.connect("questions.db") as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT 1 FROM user_points WHERE user_id = ?', (user.id,))
        result = await cursor.fetchone()

        if result:
            return False

        await cursor.execute('INSERT INTO user_points (username, user_id, doubts_solved, questions_attempted, questions_solved, questions_skipped, points, total_time_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user.name, user.id, 0, 0, 0, 0, 0, 0))
        await db.commit()
        return True

async def check_user_in_main(user: discord.User):
    async with aiosqlite.connect("questions.db") as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM user_points WHERE user_id = ?", (user.id,))
        result = await cursor.fetchone()
        return result is not None

async def get_user_data(user: discord.User):
    async with aiosqlite.connect("questions.db") as db:
        cursor = await db.cursor()
        await cursor.execute("""
            SELECT doubts_solved, questions_attempted, questions_solved, questions_skipped, points, total_time_taken 
            FROM user_points 
            WHERE user_id = ?
        """, (user.id,))
        result = await cursor.fetchone()
        return result


async def count_entries(table_name: int):
    async with aiosqlite.connect("handler.db") as db:
        cursor = await db.cursor()
        
        await cursor.execute(f"SELECT COUNT(*) FROM table_{table_name}")

        count = await cursor.fetchone()

        return count[0]

async def check_user_in_handler(table_name: str, user: discord.User):
    async with aiosqlite.connect("handler.db") as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM table_{table_name} WHERE user_id = ?", (user.id,))
        result = await cursor.fetchone()
        return result is not None

async def points_decide(time: str):
     if time < 120:
          return 20
     elif time > 120 and time < 300:
          return 15
     elif time> 300 and time < 600:
          return 10
     else:
          return 5

async def give_points_in_handler(table_name: str, user: discord.User, questions_attempted: int, questions_solved: int, questions_skipped: int, points: int, time_taken: str):
    async with aiosqlite.connect("handler.db") as db:
        cursor = await db.cursor()

        await cursor.execute(f'''
            UPDATE table_{table_name}
            SET questions_solved = questions_solved + ?, points = points + ?, questions_attempted = questions_attempted + ?, questions_skipped = questions_skipped + ?, time = time + ?
            WHERE user_id = ?
        ''', (questions_solved, points, questions_attempted, questions_skipped, time_taken, user.id))

        await db.commit()

async def give_data_in_main(user: discord.User, doubts_solved: int, questions_attempted: int, questions_solved: int, questions_skipped: int, points: int, time_taken: str):
    async with aiosqlite.connect("questions.db") as db:
        cursor = await db.cursor()

        await cursor.execute(f'''
            UPDATE user_points
            SET doubts_solved = doubts_solved + ?, questions_attempted = questions_attempted + ?, questions_solved = questions_solved + ?, questions_skipped = questions_skipped + ?, points = points + ?, total_time_taken = total_time_taken + ?
            WHERE user_id = ?
        ''', (doubts_solved, questions_attempted, questions_solved, questions_skipped, points, time_taken, user.id))

        await db.commit()

async def return_time(table_name: int, user: discord.User):
    async with aiosqlite.connect("handler.db") as db:
        cursor = await db.cursor()
        
        await cursor.execute(f'SELECT time FROM table_{table_name} WHERE user_id = ?', (user.id,))
        result = await cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

async def get_user_rank_for_doubts(user: discord.User):
    try:
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.execute("SELECT doubts_solved FROM user_points WHERE user_id = ?", (user.id,))
            user_data = await cursor.fetchone()
            
            if not user_data:
                return "N/A" 
            
            user_doubts_solved = user_data[0]

            query = """
                SELECT COUNT(*)
                FROM user_points
                WHERE (doubts_solved > ?)
                   OR (doubts_solved = ? AND user_id < ?)
            """
            cursor = await db.execute(query, (user_doubts_solved, user_doubts_solved, user.id))
            rank = await cursor.fetchone()
            
            return rank[0] + 1
    except Exception as e:
        print(f"An error occurred while fetching user rank: {e}")
        return -1

    
async def get_user_rank_for_quiz(user: discord.User):
    try:
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.execute(
                "SELECT questions_solved, points, total_time_taken, questions_attempted, questions_skipped FROM user_points WHERE user_id = ?", 
                (user.id,)
            )
            user_data = await cursor.fetchone()
            
            if not user_data:
                return "N/A"

            user_questions_solved, user_points, user_total_time_taken, user_questions_attempted, user_questions_skipped = user_data

            query = """
                SELECT COUNT(*)
                FROM user_points
                WHERE (questions_solved > ?)
                   OR (questions_solved = ? AND points > ?)
                   OR (questions_solved = ? AND points = ? AND total_time_taken < ?)
                   OR (questions_solved = ? AND points = ? AND total_time_taken = ? AND questions_attempted < ?)
                   OR (questions_solved = ? AND points = ? AND total_time_taken = ? AND questions_attempted = ? AND questions_skipped < ?)
                   OR (questions_solved = ? AND points = ? AND total_time_taken = ? AND questions_attempted = ? AND questions_skipped = ? AND user_id < ?)
            """
            cursor = await db.execute(query, (
                user_questions_solved,
                user_questions_solved, user_points,
                user_questions_solved, user_points, user_total_time_taken,
                user_questions_solved, user_points, user_total_time_taken, user_questions_attempted,
                user_questions_solved, user_points, user_total_time_taken, user_questions_attempted, user_questions_skipped,
                user_questions_solved, user_points, user_total_time_taken, user_questions_attempted, user_questions_skipped, user.id
            ))
            rank = await cursor.fetchone()
            
            return rank[0] + 1
    except Exception as e:
        print(f"An error occurred while fetching user rank: {e}")
        return -1

async def get_doubts_leaderboard(user: discord.User, ctx: commands.Context) -> discord.Embed:
    try:
        user_rank = await get_user_rank_for_doubts(user)
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.execute("SELECT user_id, username, doubts_solved FROM user_points ORDER BY doubts_solved DESC, user_id ASC LIMIT 10")
            leaderboard = await cursor.fetchall()
            
            embed = discord.Embed(title="Doubts Leaderboard", description=f"[FULL LEADERBOARD]({info.Leaderboard_link})", color=0x00ff00)
            medals = ["🥇", "🥈", "🥉"]
            for i, row in enumerate(leaderboard, start=1):
                user_id, username, doubts_solved = row
                if i <= 3:
                    medal = medals[i - 1]
                    embed.add_field(name=f"{medal} {username} ({user_id})", value=f"Doubts Solved: {doubts_solved}", inline=False)
                else:
                    embed.add_field(name=f"{i}. {username} ({user_id})", value=f"Doubts Solved: {doubts_solved}", inline=False)
                    
            embed.set_footer(text=f"Your Rank: #{user_rank}")
            embed.set_thumbnail(url=ctx.guild.icon.url)
            return embed
    except Exception as e:
        return discord.Embed(title="Error", description=f"An error occurred while fetching the leaderboard\nError: {e}", color=0xff0000)

async def get_questions_leaderboard(user: discord.User, ctx: commands.Context) -> discord.Embed:
    try:
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.execute(
                "SELECT user_id, username, questions_solved, points, total_time_taken, questions_attempted, questions_skipped FROM user_points WHERE questions_attempted > 0"
            )
            users_data = await cursor.fetchall()

            sorted_users = sorted(
                users_data,
                key=lambda x: (
                    -x[2],  # questions_solved (higher is better)
                    -x[3],  # points (higher is better)
                    x[4],   # total_time_taken (lower is better)
                    x[5],   # questions_attempted (lower is better)
                    x[6],   # questions_skipped (lower is better)
                    x[0]    # user_id (lower is better for tiebreaker)
                )
            )

            leaderboard = sorted_users[:10]  
            user_rank = await get_user_rank_for_quiz(user)

            embed = discord.Embed(title="Questions Leaderboard", description=f"[FULL LEADERBOARD]({info.Leaderboard_link})", color=0x00ff00)
            medals = ["🥇", "🥈", "🥉"]
            for i, row in enumerate(leaderboard, start=1):
                medal = medals[i - 1] if i <= 3 else f"{i}."
                time_taken_formatted = quiz.time_calculate_convert(row[4])
                embed.add_field(
                    name=f"{medal} {row[1]} ({row[0]})",
                    value=f"Solved: {row[2]} | Points: {row[3]} | Time: {time_taken_formatted} | Attempts: {row[5]} | Skipped: {row[6]}",
                    inline=False
                )

            embed.set_footer(text=f"Your Rank: #{user_rank}")
            embed.set_thumbnail(url=ctx.guild.icon.url)
            return embed
    except Exception as e:
        return discord.Embed(title="Error", description=f"An error occurred while fetching the leaderboard\nError: {e}", color=0xff0000)