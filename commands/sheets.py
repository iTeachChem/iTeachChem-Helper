import os
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
import aiosqlite
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils import info

load_dotenv()

sheets_data = os.getenv('CREDENTIALS')

if sheets_data is None:
    raise ValueError("Sheets data environment variable not found.")

sheets_data_dict = json.loads(sheets_data)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

class DataToSheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gc = None
        self.send_sheets_task.start()

    async def connect_to_google_sheets(self):
        creds = ServiceAccountCredentials.from_json_keyfile_dict(sheets_data_dict, scope)
        self.gc = gspread.authorize(creds)

    async def send_doubts_leaderboard(self):
        try:
            async with aiosqlite.connect("questions.db") as db:
                cursor = await db.execute('SELECT user_id, username, doubts_solved FROM user_points WHERE doubts_solved > 0 ORDER BY doubts_solved DESC LIMIT 100')
                rows = await cursor.fetchall()

                leaderboard_data = []
                for row in rows:
                    user_id, username, doubts_solved = row
                    leaderboard_data.append([
                        user_id,
                        username,
                        doubts_solved
                    ])

                await self.connect_to_google_sheets()
                sheet = self.gc.open("Leaderboard").sheet1 # Name of your File should be "Leaderboard". You can change it as per your need from here.

                start_cell = 'B2'
                sheet.update(start_cell, leaderboard_data)

        except Exception as e:
            print(f"Error sending doubts leaderboard to Google Sheets: {e}")

    async def send_questions_leaderboard(self):
        try:
            async with aiosqlite.connect("questions.db") as db:
                cursor = await db.execute('SELECT user_id, username, questions_attempted, questions_solved, questions_skipped, points, total_time_taken FROM user_points WHERE questions_attempted > 0')
                rows = await cursor.fetchall()

                sorted_rows = sorted(
                    rows,
                    key=lambda x: (
                        -x[3],  # Questions Solved (Higher is better)
                        -x[5],  # Points (Higher is better)
                        x[6],   # Total Time Taken (Lower is better)
                        x[2],   # Questions Attempted (Lower is better)
                        x[4],   # Questions Skipped (Lower is better)
                        x[0]    # User ID (Lower is better for tiebreaker)
                    )
                )

                leaderboard_data = []
                for row in sorted_rows[:100]:
                    user_id, username, questions_attempted, questions_solved, questions_skipped, points, total_time_taken = row
                    leaderboard_data.append([
                        user_id,
                        username,
                        questions_attempted,
                        questions_solved,
                        questions_skipped,
                        points,
                        total_time_taken
                    ])

                await self.connect_to_google_sheets()
                sheet = self.gc.open("Leaderboard").get_worksheet(1)

                start_cell = 'B2'
                sheet.update(start_cell, leaderboard_data)

        except Exception as e:
            print(f"Error sending questions leaderboard to Google Sheets: {e}")

    @commands.command(name='send')
    @commands.is_owner()
    async def sheets_send(self, ctx: commands.Context):
        """Updates the Sheet data manually"""
        await self.send_to_sheets(ctx)

    async def send_to_sheets(self, ctx: commands.Context):
        message = await ctx.send(f"Sending data from database to Google Sheets... {info.loading}")
        try:
            await self.send_doubts_leaderboard()
            await self.send_questions_leaderboard()
            await message.edit(content="Data sent successfully!")
        except Exception as e:
            await message.edit(content=f"An error occurred: {str(e)}")

    async def send_sheets_loop(self):
        try:
            await self.send_doubts_leaderboard()
            await self.send_questions_leaderboard()
        except Exception as e:
            print(f"Error! Sheets {e}")

    @tasks.loop(hours=3) # Update the Google Sheet every 3 hours
    async def send_sheets_task(self):
        await self.send_sheets_loop()

    @send_sheets_task.before_loop
    async def before_send_sheets_task(self):
        await self.bot.wait_until_ready()

    @commands.command(name="link")
    async def sheet_link(self, ctx: commands.Context):
        """Link to the Leaderboard"""
        await ctx.send(f"[Link to Leaderboard](<{info.Leaderboard_link}>)")

async def setup(bot):
    await bot.add_cog(DataToSheets(bot))