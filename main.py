import discord
from discord.ext import commands
from discord.utils import get

import json
import random
import asyncio


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('with magical ball'))
    print('Has been logged in as {0.user}'.format(client))

# CONFIG VARIABLES CHANGE ONLY THOSE ONES
client = commands.Bot(command_prefix="!")
win_id_role = 1
message_id_to_follow = 1
emotes = ['✅']
next_game_delay = 60
channel_delete_delay = 5
game_create_delay = 5
# CONFIG VARIABLES CHANGE ONLY THOSE ONES


_cd = commands.CooldownMapping.from_cooldown(1, next_game_delay, commands.BucketType.member)

def get_ratelimit(message):
    bucket = _cd.get_bucket(message)
    return bucket.update_rate_limit()

def questionData():
    with open('questions.json') as question:
        questions = json.load(question)
    return questions


@client.event
@commands.cooldown(1, next_game_delay, commands.BucketType.member)
async def on_raw_reaction_add(payload):
    async def game(payload):
        reactionAnswers = {"🇦": "A", "🇧": "B", "🇨": "C", "🇩": "D"}
        reactionAnswersReversed = {"A": "🇦", "B": "🇧", "C": "🇨", "D": "🇩"}
        questionNumbers = []
        correctAnswers = []
        corAnswers = []
        data = questionData()
        data_copy = dict(data)
        if len(data) < 6:
            return
        for _ in range(1, 6):
            randomNumber = random.choice(list(data_copy.keys()))
            questionNumbers.append(randomNumber)
            del data_copy[str(randomNumber)]
        print(questionNumbers)
        for x in questionNumbers:
            corAnswers.append(data[x]["correctAnswer"])
        for item in corAnswers:
            correctAnswers.append(reactionAnswersReversed[item])
        print(correctAnswers)
        for _ in questionNumbers:
            quest = discord.Embed(title=data[str(_)]["question"], description="", color=0xFFA500)
            quest.add_field(name="A:", value=data[str(_)]["answerA"], inline=True)
            quest.add_field(name="B:", value=data[str(_)]["answerB"], inline=True)
            quest.add_field(name="C:", value=data[str(_)]["answerC"], inline=True)
            quest.add_field(name="D:", value=data[str(_)]["answerD"], inline=True)
            question = await channel.send(embed=quest)
            for answer in reactionAnswers:
                await question.add_reaction(answer)
            try:
                answer = await client.wait_for('reaction_add', timeout=15.0, check=
                                               lambda reaction, user: reaction.emoji in reactionAnswers and user != client.user)
                if str(answer[0]) == correctAnswers[0]:
                    correctAnswers.pop(0)
                else:
                    e = discord.Embed(title="Incorrect answer! Try again later!", description="", color=0xFF0000)
                    await channel.send(embed=e)
                    await asyncio.sleep(5)
                    await channel.delete(reason="Incorrect answer")
                    return
            except asyncio.TimeoutError:
                await channel.send("You didn\'t answer in time")
                await asyncio.sleep(channel_delete_delay)
                await channel.delete()
                return

        e = discord.Embed(title="Congratulations! You answered correctly 5 times! You just won a special rank!", description="Channel will be deleted soon.", color=0x224433)
        e.set_footer(text="Made by: Kitty <3#9446")
        await channel.send(embed=e)

        var = get(guild.roles, id=win_id_role)
        member = await guild.query_members(user_ids=[user.id])
        await member[0].add_roles(var)
        await asyncio.sleep(channel_delete_delay)
        await channel.delete()
        return


    if payload.message_id == message_id_to_follow:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await client.fetch_user(payload.user_id)
        guild = message.guild
        member = await guild.query_members(user_ids=[user.id])
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member[0]: discord.PermissionOverwrite(view_channel=True)
        }
        if payload.emoji.name == emotes[0]:
            retry_after = get_ratelimit(message)
            if retry_after is None:
                channel = await guild.create_text_channel(f'Reacted with {emotes[0]}', overwrites=overwrites)
                e = discord.Embed(title="Welcome to the Quiz Game!",
                                  description="You have 15s to answer each of 5 questions!", color=0x6a0dad)
                e.set_footer(text="Made by: Kitty <3#9446")
                await channel.send(embed=e)
                await message.remove_reaction(emotes[0], user)
                await asyncio.sleep(game_create_delay)
                await game(payload)
            else:
                await message.remove_reaction(emotes[0], user)
                await member[0].send(f"You need to wait {int(retry_after)} seconds to start again")


@client.command()
async def pyr(ctx):
    data = questionData()
    print(list(data)[-1])

@client.command()
@commands.has_permissions(administrator=True)
async def addquestion(ctx):
    guild = ctx.guild
    setupQuestions = [
        "What\'s the question?",
        "Please insert answer A",
        "Please insert answer B",
        "Please insert answer C",
        "Please insert answer D",
        "Please insert correct answer."
    ]
    setupAnswers = []
    for question in setupQuestions:
        await ctx.send(question)

        try:
            answer = await client.wait_for('message', timeout=15.0,
                                                check=lambda
                                                    message: message.author == ctx.author and message.channel == ctx.channel)
        except asyncio.TimeoutError:
            await ctx.send("You didn\'t answer in time")
            return
        else:
            setupAnswers.append(answer.content)


    with open('questions.json', 'r+') as jsonFile:
        try:
            data = json.load(jsonFile)
            data[str(int(list(data)[-1]) + 1)] = {
                "question": f"{str(setupAnswers[0])}",
                "answerA": f"{str(setupAnswers[1])}",
                "answerB": f"{str(setupAnswers[2])}",
                "answerC": f"{str(setupAnswers[3])}",
                "answerD": f"{str(setupAnswers[4])}",
                "correctAnswer": f"{str(setupAnswers[5])}",
            }
            jsonDataIndent = json.dumps(data, indent=4)
            jsonFile.seek(0)
            jsonFile.write(jsonDataIndent)
            jsonFile.truncate()
        except json.JSONDecodeError:
            data = {}
            data["1"] = {
                "question": f"{str(setupAnswers[0])}",
                "answerA": f"{str(setupAnswers[1])}",
                "answerB": f"{str(setupAnswers[2])}",
                "answerC": f"{str(setupAnswers[3])}",
                "answerD": f"{str(setupAnswers[4])}",
                "correctAnswer": f"{str(setupAnswers[5])}",
            }
            jsonDataIndent = json.dumps(data, indent=4)
            jsonFile.seek(0)
            jsonFile.write(jsonDataIndent)
            jsonFile.truncate()


@client.command()
@commands.has_permissions(administrator=True)
async def delquestion(ctx):
    deletequestion = ["Which question you want to delete?"]
    data = questionData()
    for question in deletequestion:
        await ctx.send(question)

        try:
            answer = await client.wait_for('message', timeout=15.0,
                                                check=lambda
                                                    message: message.author == ctx.author and message.channel == ctx.channel)
        except asyncio.TimeoutError:
            await ctx.send("You didn\'t answer in time")
            return
    del data[str(answer.content)]
    with open('questions.json', 'r+') as jsonFile:
        jsonDataIndent = json.dumps(data, indent=4)
        jsonFile.seek(0)
        jsonFile.write(jsonDataIndent)
        jsonFile.truncate()
    await ctx.channel.send("Question removed correctly.")



@client.command()
@commands.has_permissions(administrator=True)
async def questions(ctx):
    data = questionData()
    e = discord.Embed(title="Question stats:", description=f"You have this many questions: {len(data)}", color=0xFFC0CB)
    e.set_footer(text="Made by: Kitty <3#9446")
    await ctx.channel.send(embed=e)
    e = discord.Embed(title="Questions:", description="", color=0xFFC0CB)
    e.set_footer(text="Made by: Kitty <3#9446")
    _ = 0
    for item in data:
        _ += 1
        if _ > 10:
            _ = 0
            await ctx.channel.send(embed=e)
            e = discord.Embed(title="", description="", color=0xFFC0CB)
        e.add_field(name=f"Question nb. {item}.", value=f"{data[str(item)]['question']}", inline=False)
    e.set_footer(text="Made by: Kitty <3#9446")
    await ctx.channel.send(embed=e)


client.run('YOUR_TOKEN')
