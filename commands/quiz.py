import discord
from discord.ext import commands
from utils import info
from commands import handler
import time, asyncio, datetime, random, aiosqlite
import os 
import pandas as pd

class Buttons(discord.ui.View):
    def __init__(self, bot: commands.Bot, author: discord.User, bot_message: discord.Message, set_id: int, embed: discord.Embed):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author
        self.bot_message = bot_message
        self.set_id = set_id
        self.embed = embed
        self.start_time = None
        
    @discord.ui.button(style=discord.ButtonStyle.gray, custom_id="question_button", emoji="📝")
    async def view_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        check = await handler.check_user_in_handler(self.bot_message.id, interaction.user)
        if check is False:
            try:
                em = info.instructions
                await interaction.response.send_message("Check your DMs", ephemeral=True)
                
                self.start_time = time.time()
                view = Start_Buttons(self.bot, None, self.set_id, 0, self.start_time, self.bot_message)
                dm_message = await interaction.user.send(embed=em, view=view)
                view.dm_message = dm_message 
                add_user = await handler.add_user_in_handler(self.bot_message.id, interaction.user)
                add_in_main = await handler.add_user_in_main(interaction.user)
                if add_user is True:
                    counts = await handler.count_entries(self.bot_message.id)
                    embed = self.embed
                    embed.set_footer(text=f"Number of users attempted: {counts}")
                    try:
                        await self.bot_message.edit(embed=embed)
                    except discord.NotFound:
                        print("Bot message not found. It might have been deleted.")

            except discord.Forbidden:
                await interaction.response.send_message("I couldn't send you a message. Check your privacy settings.")
        elif check is True:
            await interaction.response.send_message("You have already attempted this quiz!", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred! Contact Admin", ephemeral=True)


    @discord.ui.button(style=discord.ButtonStyle.gray, custom_id="instruction", emoji="📃")
    async def instructions(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = info.instructions
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Start_Buttons(discord.ui.View):
    active_views2 = []
    def __init__(self, bot: commands.Bot, dm_message: discord.Message, set_id: int, question_index: int, start_time: float, main_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.dm_message = dm_message
        self.set_id = set_id
        self.question_index = question_index
        self.start_time = start_time
        self.main_message = main_message
        Start_Buttons.active_views2.append(self)

    @discord.ui.button(label="Start quiz", style=discord.ButtonStyle.gray, custom_id="start_quiz_button")
    async def start_quiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await DM_Buttons.send_question(self, interaction, button, self.question_index, self.set_id)
        button.disabled = True
        button.label = "Started"

class DM_Buttons(discord.ui.View):
    active_views = []  

    def __init__(self, bot: commands.Bot, next_message: discord.Message, set_id: int, question_index: int, start_time: float, main_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.next_message = next_message
        self.set_id = set_id
        self.question_index = question_index
        self.start_time = start_time 
        self.main_message = main_message 
        DM_Buttons.active_views.append(self)
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray, custom_id="attempt_button")
    async def Attempt(self, interaction: discord.Interaction, button: discord.ui.Button):
        await DM_Buttons.send_question(self, interaction, button, self.question_index, self.set_id)

    async def send_question(self, interaction: discord.Interaction, button: discord.ui.Button, question_index, set_id):
        self.start_time = time.time()
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM questions WHERE set_id = ?', (self.set_id,))
            questions = await cursor.fetchall()

            if questions and question_index < len(questions):
                question = questions[self.question_index]
                question_id, set_id, question_image, answer_text, solution_image, subject, topic = question
                
                em = discord.Embed(title=f"Question {self.question_index + 1}", color=discord.Color.blue())
                em.set_image(url=question_image)
                view = DM_Submit_Buttons(self.bot, None, answer_text, question_image, question_id, set_id, self.question_index, self.start_time, self.start_time, solution_image, self.main_message)  
                message = await interaction.user.send(embed=em, view=view)
                view.message = message
                button.disabled = True
                button.label = "Success!"
                try:
                    await interaction.response.edit_message(view=self, delete_after=5)
                except discord.NotFound:
                    print("Interaction message not found. It might have been deleted.")
                
                self.question_index += 1

                if self.question_index < len(questions) + 1:
                    self.stop()
                else:
                    total_time = time.time() - self.start_time
                    total_time_formatted = time_calculate_convert(total_time)
                    await interaction.followup.send(f"All questions attempted! You took **{total_time_formatted}.**", ephemeral=True)
                    self.stop()
            else:
                await interaction.response.send_message("No more questions or invalid Set ID!", ephemeral=True)

    async def send_next_question(self, interaction: discord.Interaction):
        async with aiosqlite.connect("questions.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM questions WHERE set_id = ?', (self.set_id,))
            questions = await cursor.fetchall()

        if self.question_index < len(questions)-1:
            view = DM_Buttons(self.bot, None, self.set_id, self.question_index + 1, self.start_time, self.main_message)  
            end_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
            unix_timestamp = int(end_time.timestamp())
            next_message = await interaction.response.send_message(f"Click to attempt Next question. (Message will time out <t:{unix_timestamp}:R>)", view=view)
            view.next_message = next_message
        else:
            get_time = await handler.return_time(self.main_message.id, interaction.user)
            get_time_converted = time_calculate_convert(get_time)
            await interaction.response.send_message(f"All questions attempted!\nTime given on questions: **{get_time_converted}**")       

class DM_Submit_Buttons(discord.ui.View):
    active_views1 = []
    def __init__(self, bot: commands.Bot, message: discord.Message, answer_text, question_image, question_id, set_id, question_index, start_time, set_start_time, solution_image, main_message: discord.Message):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.answer_text = answer_text
        self.question_image = question_image
        self.question_id = question_id
        self.set_id = set_id
        self.question_index = question_index
        self.start_time = start_time
        self.set_start_time = set_start_time  
        self.solution_image = solution_image
        self.main_message = main_message
        DM_Submit_Buttons.active_views1.append(self)

    @discord.ui.button(label="Click to Answer", style=discord.ButtonStyle.gray, custom_id="submit_button")
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Submit_Form(self.bot, self.message, self.answer_text, self.question_image, self.question_id, self.set_id, self.question_index, self.start_time, self.set_start_time, self.solution_image, self.main_message)
        await interaction.response.send_modal(modal)

class Submit_Form(discord.ui.Modal, title="Submit your answer"):
    def __init__(self, bot: commands.Bot, bot_message: discord.Message, answer_text, question_image, question_id, set_id, question_index, start_time, set_start_time, solution_image, main_message: discord.Message):
        super().__init__()
        self.bot = bot
        self.bot_message = bot_message
        self.answer_text = answer_text
        self.question_image = question_image
        self.question_id = question_id
        self.set_id = set_id
        self.question_index = question_index
        self.start_time = start_time
        self.set_start_time = set_start_time 
        self.solution_image = solution_image
        self.main_message = main_message

    Answer = discord.ui.TextInput(label="Answer", style=discord.TextStyle.short, required=True, placeholder="Your answer here.")

    async def on_submit(self, interaction: discord.Interaction):
        end_time = time.time()
        time_taken = round(end_time - self.start_time, 2)
        rounded = round(time_taken, 2)
        conversion = time_calculate_convert(time_taken)


        if self.Answer.value.lower() == "skip":
            em = discord.Embed(title="You skipped this question", color=discord.Color.purple())
            em.set_image(url=self.question_image)
            em.set_footer(text=f"You took {conversion}.")
            try:
                await self.bot_message.edit(embed=em, view=None)
                await handler.give_points_in_handler(self.main_message.id, interaction.user, 1, 0, 1, 0, rounded)
                await handler.give_data_in_main(interaction.user, 0, 1, 0, 1, 0, rounded)
            except discord.NotFound:
                print("Bot message not found. It might have been deleted.")

        elif self.Answer.value.lower() == self.answer_text.lower():
            points_decide =  await handler.points_decide(time_taken)
            em = discord.Embed(title="You're correct!", color=discord.Color.green())
            em.add_field(name="Correct Answer", value=self.answer_text)
            em.add_field(name="Your answer", value=self.Answer.value)
            em.set_image(url=self.question_image)
            em.set_footer(text=f"You took {conversion}. | You got {points_decide} points.")
            try:
                await self.bot_message.edit(embed=em, view=None)
                await handler.give_points_in_handler(self.main_message.id, interaction.user, 1, 1, 0, points_decide, rounded)
                await handler.give_data_in_main(interaction.user, 0, 1, 1, 0, points_decide, rounded)
            except discord.NotFound:
                print("Bot message not found. It might have been deleted.")
        else:
            em = discord.Embed(title="Incorrect!", color=discord.Color.red())
            em.add_field(name="Correct Answer", value=self.answer_text)
            em.add_field(name="Your answer", value=self.Answer.value)
            em.set_image(url=self.question_image)
            em.set_footer(text=f"You took {conversion}.")
            try:
                await self.bot_message.edit(embed=em, view=None)
                await handler.give_points_in_handler(self.main_message.id, interaction.user, 1, 0, 0, 0, rounded)
                await handler.give_data_in_main(interaction.user, 0, 1, 0, 0, 0, rounded)
            except discord.NotFound:
                print("Bot message not found. It might have been deleted.")
        await DM_Buttons.send_next_question(self, interaction)

class Ques(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="ques", aliases=['qs'])
    @commands.has_permissions(administrator=True)
    async def ques(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Subcommand not found!', delete_after=5)

    @ques.command(name="start")
    async def send(self, ctx: commands.Context, set_id: int, duration: str):
        parsed_duration = parse_duration(duration)
        if parsed_duration:
            current_time = datetime.datetime.now()
            end_time = current_time + parsed_duration
            unix_timestamp = int(end_time.timestamp())
            async with aiosqlite.connect("questions.db") as db:
                cursor = await db.cursor()
                await cursor.execute('SELECT * FROM questions WHERE set_id = ?',(set_id,))
                set = await cursor.fetchall()

                if set:
                    count = len(set)
                    color = random.choice(info.colors)
                    embed = discord.Embed(title="Quiz",
                                            description=f"{ctx.author.mention} started a quiz.\n\n📝 - Click to attempt the quiz.\n📃 - Click to view instructions.",
                                            color=color)
                    embed.add_field(name="Set ID", value=set_id)
                    embed.add_field(name="Number of questions", value=count)
                    embed.add_field(name="Time", value=f"<t:{unix_timestamp}:f> (<t:{unix_timestamp}:R>)", inline=False)
                    embed.set_thumbnail(url="https://imgur.com/41BTX11.png")
                    view = Buttons(self.bot, ctx.author, None, set_id, embed)
                    message = await ctx.send(embed=embed, view=view)
                    view.bot_message = message
                    await handler.create_table(message.id)
                    
                    duration_seconds = int(parsed_duration.total_seconds())
                    self.bot.loop.create_task(self.disable_buttons_after_delay(message, duration_seconds, embed, set_id))
                else:
                    await ctx.send(f"Questions not found with Set ID: {set_id}")
        else:
            await ctx.send("Error! Code: `01`")

    async def disable_buttons_after_delay(self, message: discord.Message, duration: int, embed: discord.Embed, set_id):
        await asyncio.sleep(duration)  
        await Ques.send_leaderboard(self, message, embed, set_id)

    async def send_leaderboard(self, message: discord.Message, embed: discord.Embed, set_id):
        async with aiosqlite.connect("handler.db") as db:
            cursor = await db.cursor()
            await cursor.execute(f'SELECT user_id, questions_solved, points, time FROM table_{message.id}')
            rows = await cursor.fetchall()

        if rows:
            sorted_rows = sorted(rows, key=lambda x: (-x[1], -x[2], x[3], x[0]))
            top_10 = sorted_rows[:10]
            medals = ["🥇", "🥈", "🥉"]

            embed = discord.Embed(title=f"Top 10 Users | Set ID- {set_id}", color=discord.Color.gold())
            embed.set_thumbnail(url="https://imgur.com/e6wbPao.png")
            
            for idx, (user_id, questions_solved, points, time_taken) in enumerate(top_10, 1):
                user = await self.bot.fetch_user(user_id)
                if idx <= 3:
                    medal = medals[idx - 1]
                    time_formatted = time_calculate_convert(time_taken)
                    embed.add_field(name=f"{medal} {user.name}", 
                                    value=f"Questions Solved: {questions_solved} | Points: {points} | Time Taken: {time_formatted}",
                                    inline=False)
                else:
                    time_formatted = time_calculate_convert(time_taken)
                    embed.add_field(name=f"{idx}. {user.name}", 
                                    value=f"Questions Solved: {questions_solved} | Points: {points} | Time Taken: {time_formatted}",
                                    inline=False)

            await message.edit(embed=embed, view=None)
            thread = await message.create_thread(name="Solution and discussion")
            excel_file = await self.export_table(message.id)
            if excel_file:
                with open(excel_file, "rb") as file:
                    await thread.send(file=discord.File(file, filename=excel_file))
                os.remove(excel_file)
            else:
                await thread.send("No data found in the database.")
        else:
            await message.edit(content="No entries found in the leaderboard.", embed=embed, view=None)

    async def export_table(self, message_id: int):
        table_name = f"table_{message_id}"
        async with aiosqlite.connect("handler.db") as db:
            cursor = await db.execute(f'SELECT * FROM {table_name}')
            data = await cursor.fetchall()

            if data:
                columns = ["user_id", "questions_attempted", "questions_solved", "questions_skipped", "points", "time"]
                df = pd.DataFrame(data, columns=columns)

                excel_file = f"{table_name}.xlsx"
                df.to_excel(excel_file, index=False)

                return excel_file
            else:
                return None
       
def time_calculate_convert(time_taken: float) -> str:
    try:
        time_taken = float(time_taken)
    except ValueError:
        raise ValueError("time_taken must be a float or a string that can be converted to a float")

    if time_taken >= 3600:
        hours, remainder = divmod(time_taken, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)} hour(s) {int(minutes)} minute(s) {seconds:.2f} second(s)"
    elif time_taken >= 60:
        minutes, seconds = divmod(time_taken, 60)
        return f"{int(minutes)} minute(s) {seconds:.2f} second(s)"
    else:
        return f"{time_taken:.2f} second(s)"

def parse_duration(time_str):
    try:
        num = float(time_str[:-1])
        unit = time_str[-1].lower()
        if unit == 'h':
            return datetime.timedelta(hours=num)
        elif unit == 'm':
            return datetime.timedelta(minutes=num)
        elif unit == 'd':
            return datetime.timedelta(days=num)
        else:
            return None
    except ValueError as e:
        print(f"Error parsing duration: {e}")
        return None

async def setup(bot):
    await bot.add_cog(Ques(bot))