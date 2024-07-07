import discord
from discord.ext import commands
import aiosqlite

async def update_user_data(user: discord.User, type: str, number: int):
    async with aiosqlite.connect("questions.db") as db:
        cursor = await db.cursor()
        
        await cursor.execute(f'''
            UPDATE user_points
            SET {type} = {type} + ?
            WHERE user_id = ?
        ''', (number, user.id))

        await db.commit()
        return True

async def remove_user_data(ctx: commands.Context, user: discord.User):
    try:
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.cursor()

            query = "DELETE FROM user_points WHERE user_id = ?"
            await cursor.execute(query, (user.id,))
            await db.commit()

            if cursor.rowcount == 0:
                await ctx.send("No user found with that ID.")
            else:
                await ctx.send(f"Data removed successfully for {user.name} ({user.id})")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")