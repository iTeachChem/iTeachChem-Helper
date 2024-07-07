import discord
from discord.ext import commands
import aiosqlite
import random
from utils import info
import pandas as pd
import os

class first_call(discord.ui.View):
    def __init__(self, bot: commands.Bot, author: discord.User, bot_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author
        self.bot_message = bot_message

    @discord.ui.button(style=discord.ButtonStyle.gray, custom_id="add_button", emoji=info.list)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            modal = QuestionForm(self.bot, self.bot_message, self.author)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(":x: Not allowed", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.red, custom_id="cancel_button", emoji="<:Cancel:1231657756310765629>")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            await self.bot_message.edit(content="Cancelled", embed=None, view=None)
        else:
            await interaction.response.send_message(":x: Not allowed", ephemeral=True)

class Confirm(discord.ui.View):
    def __init__(self, bot: commands.Bot, author: discord.User, bot_message: discord.Message, question: str, answer: str, solution: str, subject: str, topic: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author
        self.bot_message = bot_message
        self.question = question 
        self.answer = answer
        self.solution = solution
        self.subject = subject
        self.topic = topic

    @discord.ui.button(style=discord.ButtonStyle.gray, custom_id="set_button", emoji="☑️")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            async with aiosqlite.connect("questions.db") as db:
                cursor = await db.cursor()

                await cursor.execute('INSERT INTO questions (question_image, answer_text, solution_image, subject, topic) VALUES (?, ?, ?, ?, ?)', (self.question, self.answer, self.solution, self.subject, self.topic,))
                await db.commit()
                question_id = cursor.lastrowid

                await cursor.execute('SELECT set_id FROM questions WHERE question_id = ?', (question_id,))
                result = await cursor.fetchone()
                set_id = result[0] if result else None

                color = random.choice(info.colors)
                em = discord.Embed(title="Question Added", color=color)
                em.add_field(name="Set ID", value=f"{set_id}", inline=False)
                em.add_field(name="Question ID", value=f"{question_id}", inline=False)
                em.add_field(name="Subject", value=self.subject)
                em.add_field(name="Topic", value=self.topic)
                em.set_image(url=self.question)
                em2 = discord.Embed(title="Answer", color=color)
                em2.add_field(name="Answer", value=f"{self.answer}")
                em3 = discord.Embed(title="Solution", color=color)
                em3.set_image(url=self.solution)
                await self.bot_message.edit(content="Question added successfully", view=None, embeds=[em, em2, em3])
        else:
            await interaction.response.send_message(":x: Not allowed", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.red, custom_id="cancel_button", emoji="<:Cancel:1231657756310765629>")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            await self.bot_message.edit(content="Cancelled", view=None, embed=None)
        else:
            await interaction.response.send_message(":x: Not allowed", ephemeral=True)



class QuestionForm(discord.ui.Modal, title="Question adding"):
    def __init__(self, bot: commands.Bot, bot_message: discord.Message, author: discord.User):
        super().__init__()
        self.bot = bot
        self.bot_message = bot_message
        self.author = author

    Question = discord.ui.TextInput(label="Question Image link", style=discord.TextStyle.paragraph, required=True, placeholder="Link of the questions image ")
    Answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.paragraph, required=True, placeholder="Please put exact answer")
    Solution = discord.ui.TextInput(label="Solution Image link", style=discord.TextStyle.paragraph, required=True, placeholder="Link of the solution image")
    Subject = discord.ui.TextInput(label="Subject", style=discord.TextStyle.paragraph, required=True, placeholder="Physics, Chemistry, Maths")
    Topic = discord.ui.TextInput(label="Topic", style=discord.TextStyle.paragraph, required=True, placeholder="Mole concept")

    async def on_submit(self, interaction: discord.Interaction):
        em = discord.Embed(title="Question pending approval")
        em.add_field(name="Subject", value=self.Subject.value)
        em.add_field(name="Topic", value=self.Topic.value)
        em.set_image(url=self.Question.value)
        em2 = discord.Embed()
        em2.add_field(name="Answer", value=f"{self.Answer.value}")
        em3 = discord.Embed(title="Solution")
        em3.set_image(url=self.Solution.value)
        view = Confirm(self.bot, self.author, self.bot_message, self.Question.value, self.Answer.value, self.Solution.value, self.Subject.value, self.Topic.value) 
        await interaction.response.send_message("Response taken", ephemeral=True)
        await self.bot_message.edit(content="Would you like to add this question to the data", embeds=[em,em2,em3], view=view)


class Questions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="question", aliases=['q'])
    @commands.has_permissions(administrator=True)
    async def questions(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Subcommand not found!', delete_after=5)

    @questions.command(name='add')
    async def add(self, ctx: commands.Context):
        color = random.choice(info.colors)
        em = discord.Embed(title="Add your question",
                           color=color)
        view = first_call(self.bot, ctx.author, None)
        bot_message = await ctx.send(embed=em, view=view)
        view.bot_message = bot_message

    @questions.command(name="get")
    async def get_question(self, ctx: commands.Context, question_id: int):
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM questions WHERE question_id = ?', (question_id,))
            question = await cursor.fetchone()

            if question:
                question_id, set_id, question_text, answer, solution, subject, topic = question
                color = random.choice(info.colors)
                embed = discord.Embed(title="Question Details", color=color)
                embed.add_field(name="Set ID", value=set_id)
                embed.add_field(name="Question ID", value=question_id)
                embed.add_field(name="Subject", value=subject)
                embed.add_field(name="Answer", value=answer)
                embed.add_field(name="Topic", value=topic)
                embed.set_image(url=question_text)
                embed1 =  discord.Embed(title="Solution")
                embed1.set_image(url=solution)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Question not found with that ID.")

    @questions.command(name="remove")
    async def remove_question(self, ctx: commands.Context, id: int):
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.cursor()
            await cursor.execute('DELETE FROM questions WHERE question_id = ?', (id,))
            await db.commit()
            if cursor.rowcount > 0:
                await ctx.send(f"Question with ID {id} removed successfully.")
            else:
                await ctx.send("Question not found with that ID.")

    @questions.command(name="export")
    async def export(self, ctx: commands.Context):
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.execute('SELECT * FROM questions')
            data = await cursor.fetchall()

            if data:
                excel_file = "questions.xlsx"
                df = pd.DataFrame(data, columns=["question_id", "set_id", "question_image", "answer_text", "solution_image", "subject", "topic"])
                df.to_excel(excel_file, index=False)

                try:
                    with open(excel_file, "rb") as file:
                        await ctx.send(file=discord.File(file, filename=excel_file))
                finally:
                    os.remove(excel_file)
            else:
                await ctx.send("No questions found in the database.")

async def setup(bot):
    await bot.add_cog(Questions(bot))