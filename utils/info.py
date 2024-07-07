import discord

Forum_channel_ID = ...  # Forum Channel ID

# Role IDs
Physics = ...
Chemistry = ...
Maths = ...
Biology = ...

# IDs
OWNER_IDS = []
ERROR_LOG_CHANNEL_ID = ...
restricted = []

# Random greet on error handling
greet= ["Hey there!",
        "Peak-a-boo!",
        "Howdy!",
        "Hiya!",
        "Greetings!",
        "Yo!",
        "Hi, friend!",
        "Aloha!",
        "Hi, there!",
        "Hola amigo!"]

colors = [
    0xFFA07A,  # Light Salmon
    0xFFD700,  # Gold
    0xFFFF00,  # Yellow
    0x32CD32,  # Lime Green
    0x00FF7F,  # Spring Green
    0x00CED1,  # Dark Turquoise
    0x00FFFF,  # Cyan
    0x40E0D0,  # Turquoise
    0x48D1CC,  # Medium Turquoise
    0x87CEEB,  # Sky Blue
    0x87CEFA,  # Light Sky Blue
    0x4682B4,  # Steel Blue
    0x4169E1,  # Royal Blue
    0x6495ED,  # Cornflower Blue
    0x1E90FF,  # Dodger Blue
    0x00BFFF,  # Deep Sky Blue
    0x87CEEB,  # Sky Blue
    0x7B68EE,  # Medium Slate Blue
    0x6A5ACD,  # Slate Blue
    0x483D8B,  # Dark Slate Blue
    0xFF69B4,  # Hot Pink
    0xFFB6C1,  # Light Pink
    0xFFC0CB,  # Pink
    0xFF1493,  # Deep Pink
    0xFF00FF   # Magenta
]

Tick = ("<:Tick:1228250999966404618>")
list = ("<:list:1231898439068155965>")
keypad = ("<:keypad:1231900545707671562>")
loading = ("<a:loading:1232002621208789018>")

instructions = discord.Embed(
    title="INSTRUCTIONS",
    description="""1. Questions will be either option-based or numeric type.
2. For option-based questions, submit the option alphabet (e.g., 'A'). For questions with multiple correct options, submit all correct options (e.g., 'ABC').
3. For numeric type questions, submit the value of your answer rounded off to two decimal places.
4. Please ensure fairness by using only one account to attempt questions.
5. If you encounter technical issues during the quiz, ping any online moderator for assistance.
    """)

instructions.add_field(
    name="MARKING SCHEME",
    value="""**For every Correct answer:-**

            \u2022 Solved in less than 2 minutes - `20` Points            
            \u2022 Solved in between 2 to 5 minutes - `15` Points          
            \u2022 Solved in between 5 to 10 minutes - `10` Points
            \u2022 Solved in more than 10 minutes - `5` Points
            
            **Incorrect Answer** - `0` Points
            **Skipped** - `0` Points"""
)


Help_embed = discord.Embed(title="Commands",
                           
                        description="""`+help`- Shows this embed.
                        `+solved @user1, @user2...`- Marks the post as solved and archives it. Only the OP of that post can use this command. Mention the users to give them the credit of solving your doubt. 
                        `+stats`- View your doubt and quiz stats. Mention the user with the command to view their stats.
                        `+lb doubts`- Leaderboard to keep track of the top doubt solvers.
                        `+lb quiz`- Leaderboard to keep track of the top users in quiz.
                        `+check`- Returns all active doubt posts in the last 24 hrs.
                        `+unsolved`- Retruns all active doubt posts (7 days).
                        `+threads`- Get info about your doubt posts. Mention the user with the command to view their posts.
                        `+link`- Link to the Google sheets.
                        `+ping`- Pong!
                        """,

                        color=0x00ff00)

Admin_help_embed = discord.Embed(title="Admin Help",
                                 
                        description=f"""`+help admin`- Shows this embed.
                        `+status <type> <status message>`- Change the bot status to anything you want. `<type>` accepts p, l, w, c.
                        `+fsolved @user1, @user2...`- Marks the post as solved and archives it. Accepts no user mentions too.
                        `+reopen`- Opens a closed doubt post (Manage Threads).
                        `+set <type> <user> <number>`- Set the stats of a user. <type> accepts doubts, solved, attempted, points, skipped.
                        `+info`- Returns info about the doubt channel stats.
                        `+q`- Command to make changes in questions. Accepts add, get, remove and export.
                        `+qs`- Command used to start a quiz. Accepts start and stop.
                        """,
                        color=0x00ff00)

Leaderboard_link = "https://docs.google.com/spreadsheets/"