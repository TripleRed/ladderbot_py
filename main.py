# GD Demon Ladder Discord bot
# Written by RFMX, (c) 2021-2022

# ver 1.1.5b

"""
This bot is written to make searching for demons easier in server.
This basically means cloning the features found in the website
and do something more or different about it.

Comments refer to the previous line unless for headers marked with *

Current functions:
g!bean: Beans
g!level: Information about a level. Input is the ID.
g!need: Gives 5 random demons of the same tier. Input is the required tier.
g!ping: Pings.
g!help: Shows info about commands.
g!rating: Submits ratings.
g!user: Shows ratings submitted by a user.
"""

# ** Setup **
import logging, discord, asyncio, aiohttp, json, random, os, datetime, pytz, keep_alive, math
from discord.ext import commands, tasks

random.seed(a=os.urandom(32))  # set seed for randomness
logging.basicConfig(level=logging.INFO)  # logging so that I see stuff
token = os.environ.get("TOKEN")  # Discord bot token
apikey = os.environ.get("APIKEY")  # Google sheets API key
sheetid = "1Cq6TcaXZU7w8jVpgy4pYpmI76ALwQqX7Mm8itETz9wU" # sheet in use
# original: 1xaMERl70vzr8q9MqElr4YethnV15EOe8oL1UV9LLljc
# bot: 1Cq6TcaXZU7w8jVpgy4pYpmI76ALwQqX7Mm8itETz9wU

# * Discord bot set-up *
intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = commands.Bot(intents=intents, command_prefix='g!', help_command=None)

# * Color hex for tiers *
tierhex = (0xBBBBBB,
            0xDDDFEE, 0xD5D3E9, 0xD3CBE7, 0xD3C3E4, 0xD4BBE2, 0xD5B0DE, 0xDBA7DC, 0xDB9FD1, 0xD991C1, 0xDA86B0, 0xDB7698, 0xDC6A7D, 0xDD5A5A, 0xDC514C, 0xDA493E, 0xDA4535, 0xD93E26, 0xCD3F23, 0xC03A1B, 0xB23415, 0xA23010, 0x9B2B0C, 0x932B0B, 0x892608, 0x832607, 0x752105, 0x6C1E04, 0x601A02, 0x5A1802, 0x511700)
            
# * Prompts for g!need *
# * Prompts for easier demons (Tiers 1-10)
prompts_e = ("A Tier {0}, you say?", "Grinding demons, eh?",
             "An easier level won't hurt.", "You sure are improving.",
             "Here's your next goal.", "You'll be an expert someday.",
             "99% of the people can beat these. :joy: :ok_hand:",
             "Let me guess, you are beating an Extreme? No? Okay.",
             "Tier {0}? Gotcha.", "even harder than Back on Track tbh",
             "Finally pulling yourself to beat another demon, aren't you?",
             "Certified as Tier {0}, players approved")
# * Prompts for harder demons (Tiers 11-30)
prompts_h = ("A Tier {0}, you say?", "Fancy a challenge, eh?",
             "I guess one of these would be your next hardest.", "Um, go?",
             "Honestly, everyone will be amazed if you beat these.",
             "Are you doing this for a demon roulette?",
             "99% of the people cannot beat these. :joy: :ok_hand:",
             "Yet another Medium Demon? Crap, wrong guess.",
             "On my way to deliver a Tier {0} to you.", "so free tbh",
             "Finally trying to have a new hardest, aren't you?",
             "Certified as Tier {0}, players approved")
# * Prompts for unrated demons
prompts_u = (
    "A Tier... unrated? I guess that's a tier.",
    "I see you're into stuff that is unknown.",
    "Yes. It helps the project grow. Do remember to drop a rating.",
    "Warning: enjoyability not guaranteed.", "I hope you run into Ouroboros.",
    "There's 3/4 of levels bearing a tier and you are picking these.",
    "I can't stop you from being the curious cat.",
    "Curiosity allows people to discover hidden gems.",
    "Maybe you can make a race out of these.",
    "Statistics shows that when there is one more rated level, there is one less unrated level.",
    "I'm guessing you are beating a Harder level. This is the Demon Ladder? Whatever.",
    "99% of the people think ads are boring. :joy: :ok_hand:",
    "Finally getting yourself to... what? Unrated?", "so random",
    "support the GD Demon Ladder thanks",
    "*inserts random quote about being random*")

# ** Commands **


# * G!LEVEL: this receives a level ID then spits data about it *
@client.command()
async def level(ctx, id_search):
    print('ladder> Executing command __level__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))  # prompt in console

    # * HTTP requests
    global apikey
    url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!E:E?key=" + apikey # URL construction
    print('ladder> Requesting to Google sheets for data at Column E.')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("ladder> Status:", response.status)
            r_json = await response.text() # parse response
            r_json = json.loads(r_json)
            r_json = r_json['values']
            id_array = []
            id_array.append(id_search)
            try:
                demon_no = r_json.index(id_array)
            except:
                demon_no = -1 # null response
    if demon_no != -1:
        row_no = demon_no + 1 # off by one :3
        row_select = "'The List'!" + str(row_no) + ":" + str(row_no) # construct area in A1 notation
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/" + row_select + "?key=" + apikey # URL cnstruction again
        print('ladder> Requesting to Google sheets for data at row {0}'.format(
            row_no))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
                r_json = r_json[0]

                # Now r_json is the row of the demon required, but in list form
                # The order of the data in the list follows the order of the columns in the spreadsheet
                # So r_json[0] means entry in Column A, selected row
                
                name = r_json[0]
                gdbrowser_url = 'https://gdbrowser.com/' + r_json[4]
                creator = r_json[1]
                song = r_json[2]
                officialdiff = r_json[3]
                if r_json[5] != "unrated":
                    tier = r_json[5]
                    tier2dp = r_json[6]
                    ratings = ''
                    i = 7
                    try:
                        while r_json[i] != '':
                            ratings = ''.join([ratings, '- Tier ', r_json[i]])
                            i = i + 1
                            ratings = ''.join([ratings, ' by ', r_json[i]])
                            i = i + 1
                            ratings = ''.join([ratings, '\n'])
                    except:
                        pass
                else:
                    tier = 'Unrated'
                    ratings = None

    # * Constructing embed
    if demon_no != -1:
        if tier != 'Unrated':            
            embed = discord.Embed(title="Level information of {0} ({1})".format(name, id_search), url=gdbrowser_url, color=tierhex[int(tier)])
        else:            
            embed = discord.Embed(title="Level information of {0} ({1})".format(name, id_search), url=gdbrowser_url, color=tierhex[0])
        embed.add_field(name="Creator", value=creator, inline=True)
        embed.add_field(name="Song", value=song, inline=True)
        embed.add_field(name="Official Difficulty",
                        value=officialdiff,
                        inline=True)
        if tier != 'Unrated':
            embed.add_field(name="Tier",
                            value="Tier {0} ({1})".format(tier, tier2dp),
                            inline=False)
        else:
            embed.add_field(name="Tier", value="Unrated", inline=False)
        if ratings != None:
            embed.add_field(name="Submitted ratings",
                            value=ratings,
                            inline=True)
    else:
        embed = discord.Embed(title="There is no demon with the ID {0}!".format(id_search), \
        color=0xED4337)
    # Fun section, TODO rewrite this section so that this obtains info from an external file
    if id_search == "60660086":
        embed.set_footer(text="- Tier what the fuck do you mean multition 6")
    elif id_search == "76074130":
        embed.set_footer(text="i too love consuming vast amounts of chlorine!")
    await ctx.channel.send(embed=embed)
    print('ladder> Command execution complete.')


# * G!STATUS: Administrator only, change the status of the bot *
# this is just for legacy purposes, now the bot does it automatically
@client.command()
@commands.has_permissions(administrator=True)
async def status(ctx, playing):
    print('ladder> Executing command __status__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    await client.change_presence(activity=discord.Game(playing))


# * G!NEED: Generates random demons for a specified tier, or unrated demons
@client.command()
async def need(ctx, needtier):
    global apikey
    print('ladder> Executing command __need__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    try:
        # * Setup
        needtier = int(needtier)
        if needtier <= 0 or needtier >= 31:
            raise Exception("Tier out of range")

        if needtier <= 10: etitle = prompts_e[random.randrange(len(prompts_e))]
        else: etitle = prompts_h[random.randrange(len(prompts_h))]

        embed = discord.Embed(title=etitle.format(needtier), \
        description="*If you wish to generate a new set of demons, react with :repeat:.*", \
        color=tierhex[needtier])

        # * HTTP request
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!A:F?majorDimension=COLUMNS&key=" + apikey
        print(
            'ladder> Requesting to Google sheets for data at Columns A to F.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
                result = []
                i = 1
                while i < len(r_json[4]):
                    result.append(i)
                    i += 1

                list = []
                try:
                    while True:
                        check_list = result.pop(0)
                        try:
                            check_try = int(r_json[5][check_list])
                        except:
                            check_try = 0
                        if needtier == check_try:
                            list.append(check_list)  # comparison check
                except:
                    pass
                try:
                    while True:
                        result.append(list.pop(0))
                except:
                    pass

                # * Embed construction
                responsemsg = await ctx.channel.send(content="Processing...")
                await responsemsg.add_reaction("🔁")

                loop = True
                while loop:  # the loop is for repeated generation of demons
                    embed.clear_fields()
                    if len(result) >= 5:
                        for i in random.sample(result, 5):
                            embed.add_field(name="{0}".format(r_json[0][i]), \
                            value="{0}".format(r_json[4][i]), \
                            inline=True)
                    else:
                        embed.add_field(name="Only {0} demons are found.".format(len(result)), \
                            value="As such, only 1 demon is shown.", \
                            inline=False)
                        for i in random.sample(result, 1):
                            embed.add_field(name="{0}".format(r_json[0][i]), \
                            value="{0}".format(r_json[4][i]), \
                            inline=True)
                    await responsemsg.edit(content="", embed=embed)

                    print(
                        "ladder> Command execution complete with samples generated. Awaiting further response."
                    )

                    # * Wait for reply for 1m
                    def check(reaction, user):
                        return user == ctx.author and str(
                            reaction.emoji) == "🔁"

                    try:
                        await client.wait_for('reaction_add',
                                              timeout=60.0,
                                              check=check)
                    except asyncio.TimeoutError:
                        loop = False
                    await responsemsg.remove_reaction("🔁", ctx.author)
    except:
        try:
            # * Unrated tiers
            if needtier.lower() == "unrated":
                # * Setup
                etitle = prompts_u[random.randrange(len(prompts_u))]

                embed = discord.Embed(title=etitle.format(needtier), \
                description="*If you wish to generate a new set of demons, react with :repeat:.*", \
                color=0xD6D6D6)

                # * HTTP request
                url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!A:F?majorDimension=COLUMNS&key=" + apikey
                print(
                    'ladder> Requesting to Google sheets for data at Columns A to F.'
                )
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        print("ladder> Status:", response.status)
                        r_json = await response.text()
                        r_json = json.loads(r_json)
                        r_json = r_json['values']
                        result = []
                        i = 1
                        while i < len(r_json[4]):
                            result.append(i)
                            i += 1

                        list = []
                        try:
                            while True:
                                check_list = result.pop(0)
                                try:
                                    check_try = str(r_json[5][check_list])
                                except:
                                    check_try = 0
                                if needtier == check_try:
                                    list.append(check_list)  # comparison check
                        except:
                            pass
                        try:
                            while True:
                                result.append(list.pop(0))
                        except:
                            pass

                        # * Embed construction
                        responsemsg = await ctx.channel.send(
                            content="Processing...")
                        await responsemsg.add_reaction("🔁")

                        loop = True
                        while loop:
                            embed.clear_fields()
                            for i in random.sample(result, 5):
                                embed.add_field(name="{0}".format(r_json[0][i]), \
                                value="{0}".format(r_json[4][i]), \
                                inline=True)
                            await responsemsg.edit(content="", embed=embed)

                            print(
                                "ladder> Command execution complete with samples generated. Awaiting further response."
                            )

                            # * Wait for reply for 1m
                            def check(reaction, user):
                                return user == ctx.author and str(
                                    reaction.emoji) == "🔁"

                            try:
                                await client.wait_for('reaction_add',
                                                      timeout=60.0,
                                                      check=check)
                            except asyncio.TimeoutError:
                                loop = False
                            await responsemsg.remove_reaction("🔁", ctx.author)

            else:
                embed = discord.Embed(title="Enter the tier as an integer from 1 to 30!", \
                color=0xED4337)
                await ctx.channel.send(embed=embed)
                print(
                    'ladder> Command execution complete as tier is of incorrect syntax.'
                )
        except:
            embed = discord.Embed(title="Enter the tier as an integer from 1 to 30!", \
            color=0xED4337)
            await ctx.channel.send(embed=embed)
            print(
                'ladder> Command execution complete as tier is of incorrect syntax.'
            )


# * G!USER: Generates submitted ratings for a specified username *
@client.command()
async def user(ctx, username, *args):
    global apikey
    username = str(username)
    print('ladder> Executing command __user__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    args = list(args)
    responsemsg = await ctx.channel.send(
        content="Processing...")

    pagecall = "page" in args
    if pagecall: args.remove("page")
    idcall = "id" in args
    if idcall: args.remove("id")
    tiercall = "tier" in args
    if tiercall: args.remove("tier")
    unratedcall = "unrated" in args
    if unratedcall: args.remove("unrated")

    def bodycheck(usernameB, rowdataB, idcallB, specified_idB, tiercallB, specified_tierB, unratedcallB):
        if rowdataB.index(username) <= 6: return False
        elif not(not (idcallB) or (rowdataB[4] == specified_idB)): return False
        elif not(not (tiercallB) or (rowdataB[rowdataB.index(usernameB) - 1] == specified_tierB)): return False
        elif unratedcallB: return False
        else: return True

    url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'?majorDimension=ROWS&key=" + apikey
    print('ladder> Requesting to Google sheets for data of the whole sheet.')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("ladder> Status:", response.status)
            r_json = await response.text()
            r_json = json.loads(r_json)
            r_json = r_json['values']
            submissions = []
            specified_id = None
            specified_tier = None
            if idcall:
                try:
                    specified_id = args.pop(0)
                except:
                    idcall = False
            if tiercall:
                try:
                    specified_tier = args.pop(0)
                except:
                    tiercall = False
            for rowdata in r_json:
                if username in rowdata:
                    if bodycheck(username, rowdata, idcall, specified_id, tiercall, specified_tier, unratedcall):
                        levelsubmit = [
                            rowdata[0], rowdata[4],
                            rowdata[rowdata.index(username) - 1]
                        ]
                        submissions.append(levelsubmit)
                elif unratedcall:
                    if (not tiercall or rowdata[5] == specified_tier):   
                        levelsubmit = [
                            rowdata[0], rowdata[4]
                        ]
                        submissions.append(levelsubmit)
            if unratedcall and submissions[0][0] == "Name": submissions.pop(0)
            try:
                if len(submissions) > 0:
                    totalpages = int(math.ceil(len(submissions) / 10))
                    if pagecall:
                        try:
                            page = int(args.pop()) - 1
                        except:
                            page = 0
                    else:
                        page = 0
                    await responsemsg.add_reaction("⬅️")
                    await responsemsg.add_reaction("➡️")
                    loop = True
                    while loop:
                        sub_excerpt = ""
                        if len(submissions) < 10 * (page + 1):
                            display_range = range(10 * page, len(submissions))
                        else:
                            display_range = range(10 * page, 10 * (page + 1))
                        for i in display_range:
                            if unratedcall:
                                levelmsg = submissions[i][0] + " (" + submissions[i][1] \
                                + ")" + "\n"
                                sub_excerpt = sub_excerpt + levelmsg
                            else:
                                levelmsg = submissions[i][0] + " (" + submissions[i][1] \
                                + ") as Tier " + submissions[i][2] + "\n"
                                sub_excerpt = sub_excerpt + levelmsg
                        if unratedcall: embed = discord.Embed(title="Levels without submissions for " + username, \
                        description=sub_excerpt, \
                        color=0xD6D6D6)
                        else: embed = discord.Embed(title="Submissions for " + username, \
                        description=sub_excerpt, \
                        color=0xD6D6D6)
                        embed.set_footer(text="Page {0} of {1} out of {2} submissions".format(page + 1, totalpages, len(submissions)),
                        )
                        await responsemsg.edit(content="", embed=embed)
                        print(
                            "ladder> Command execution complete with samples generated. Printed Page {0}. Awaiting further response."
                            .format((page + 1)))

                        def check(reaction, user):
                            return (user == ctx.author and (str(reaction.emoji) == "⬅️" or str(reaction.emoji) == "➡️"))

                        try:
                            reaction, user = await client.wait_for(
                                'reaction_add', timeout=180.0, check=check)
                            print(reaction)
                            if reaction.emoji == "⬅️" and page > 0:
                                page -= 1
                            elif reaction.emoji == "➡️" and page < (
                                    totalpages - 1):
                                page += 1
                        except asyncio.TimeoutError:
                            loop = False
                            print("ladder> Timeout.")
                        try:
                            await responsemsg.remove_reaction("⬅️", ctx.author)
                        except:
                            pass
                        try:
                            await responsemsg.remove_reaction("➡️", ctx.author)
                        except:
                            pass
                else:
                    embed = discord.Embed(title="No submissions found for " +
                                          username + "!",
                                          color=0xED4337)
                    await responsemsg.edit(content="", embed=embed)
                    print(
                        'ladder> Command execution complete as no submissions are found.'
                    )
            except:
                embed = discord.Embed(title="An error occured! The page number could be out of the possible range.", \
                color=0xED4337)
                await ctx.channel.send(embed=embed)
                print(
                    'ladder> Command execution complete as an error occured.')


# * G!RATING: Sends rating towards #rating-response-mod *
@client.command()
async def rating(ctx, playername, refreshrate, levelname, levelid, creator,
                 leveltier, *dropped):
    print('ladder> Executing command __rating__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    dropped = list(dropped)
    try: levelenjoy = dropped.pop(0)
    except: levelenjoy = None
    channel = client.get_channel(744552880991764520)
    await ctx.message.delete()
    await channel.send("""
New response submitted at {0} UTC
This is a NORMAL response.
User: {1}
Refresh rate: {2}
Level Name: {3}
ID: {4}
Creator: {5}
Rated Tier: {6}
Rated Enjoyment: {7}
Dropped string: {8}
    """.format(
        str(datetime.datetime.now(tz=pytz.utc))[0:-13], playername,
        refreshrate, levelname, levelid, creator, leveltier, levelenjoy, dropped))
    print('ladder> Command execution complete.')

# * G!ENJOY: Sends enjoyment rating towards #rating-response-mod *
@client.command()
async def enjoy(ctx, playername, levelname, levelid, creator,
                 levelenjoy, *dropped):
    print('ladder> Executing command __enjoy__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(946831960519610378)
    await ctx.message.delete()
    await channel.send("""
- New response submitted at {0} UTC
**THIS IS AN ENJOYMENT SUBMISSION**
- User: {1}
- Level Name: {2}
- ID: {3}
- Creator: {4}
- Rated Enjoyment: {5}
- Dropped string: {6}
    """.format(
        str(datetime.datetime.now(tz=pytz.utc))[0:-13], playername,
        levelname, levelid, creator, levelenjoy, dropped))
    print('ladder> Command execution complete.')
                     
# * G!BEAN: Beans. *
@client.command()
async def bean(ctx, person, *reason):
    print('ladder> Executing command __bean__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    if "!" in person: personid = person[3:-1]
    else: personid = person[2:-1]
    print(personid)
    try:
        person_user = await client.fetch_user(personid)
    except:
        if "#" in person:
            person_tag = person.split("#", 1)
            person_user = discord.utils.get(client.get_all_members(), name=person_tag[0], discriminator=person_tag[1])
        else:
            person_user = discord.utils.get(client.get_all_members(), name=person)
    if person_user != None:
        if len(reason) == 0: reasontext = "No reason given."
        else: reasontext = ' '.join(reason)
        await ctx.channel.send(
            "<:yes_tick:744780635641610240> {0}#{1} (`{2}`) was beaned. Reason: `{3}`"
            .format(person_user.name, person_user.discriminator,
                    person_user.id, reasontext))
    elif person == "everyone":
        await ctx.channel.send("I too wish to give beans to everyone.")
    else:
        await ctx.channel.send("No user found for `{0}`!".format(person))
    print('ladder> Bean successful. Waiting for person to send message in an hour.')
    
    def check(msg):
        return (msg.author == person_user)

    emoji = discord.utils.get(client.emojis, name='mrbean')
    msg = await client.wait_for('message', timeout=3600.0, check=check)
    await msg.add_reaction(emoji)
        
    print('ladder> Command execution complete.')

# * G!SEND: Administrator only, sends ID to boss *
@client.command()
@commands.has_permissions(administrator=True)
async def send(ctx, idcall):
    print('ladder> Executing command __send__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(933282895576051792)
    embed = discord.Embed(title="Sending to boss...", color=0xED4337)
    stringcall = "Level ID: " + idcall
    embed.set_footer(text=stringcall)
    await channel.send(embed=embed)
    print('ladder> Command execution complete.')

# * G!MESSAGE: Administrator only, make bot talk *
@client.command()
@commands.has_permissions(administrator=True)
async def message(ctx, *, message):
    print('ladder> Executing command __message__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    await ctx.message.delete()
    await ctx.channel.send(message)
    print('ladder> Command execution complete.')

# * G!ANNOUNCE: Administrator only, make bot talk at #announcement*
@client.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message):
    print('ladder> Executing command __announce__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(756512731124727988)
    await channel.send(message)
    print('ladder> Command execution complete.')

# * G!HELP: Information about commands *
@client.command(aliases=['info'])
async def help(ctx, *args):
    print('ladder> Executing command __help__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    args = list(args)
    if len(args) == 0:
        embed = discord.Embed(title="LadderBot help", \
        description="This is a list of commands you can use! Parameters are enclosed in <>s.\nFor more info, join the following server: https://discord.gg/TWhxaeM", \
        color=0xCCFF00)
        embed.add_field(name="-----", \
        value="""
**g!bean:** Bean people.
**g!enjoy:** Submit enjoyment ratings for the list.
**g!help:** Information about the commands.
**g!level:** Information about a level in the list.
**g!need:** Random levels of your desired tier.
**g!ping:** Pings bot.
**g!rating:** Submit difficulty ratings for the list.
**g!user:** Ratings submitted by a user.
        """, \
        inline=False)
        embed.set_footer(text="Use g!help <command> for details about each command!")
        await ctx.channel.send(embed=embed)
    elif len(args) > 1:
        embed = discord.Embed(title="Give only 1 command for the info page!", color=0xED4337)
        await ctx.send(embed=embed)
    elif "bean" in args:
        embed = discord.Embed(title="g!bean <user> <reason>", \
        description="Bean any person you like. You can either give only the name, or name with the discriminator, or tag the person! The reason can also have spaces in between. Everyone can use this command.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "help" in args:
        embed = discord.Embed(title="g!help <command>", \
        description="Shows information about a command. Add the command name to the `command` parameter to learn about the details.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "level" in args:
        embed = discord.Embed(title="g!level <id>", \
        description="Shows information about the level in the list. This includes the current tier and submitted ratings.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "need" in args:
        embed = discord.Embed(title="g!need <tier>", \
        description="Get 5 random levels from your specified tier! There is also an `unrated` tier!", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "ping" in args:
        embed = discord.Embed(title="g!ping", \
        description="Pings the bot. If it does not respond, chances are it is down. Please contact RFMX in our official server if this situation continues.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "rating" in args:
        embed = discord.Embed(title="g!rating <username> <refreshrate> <levelname> <levelid> <creatorname> <difficulty> [enjoyment]", \
        description="The command for submitting ratings! For any parameter, if it includes spaces, wrap the whole input in double quotes. (\"\") For example: \n`g!rating \"Chris Wong\" 60 \"Impact X\" 28461869 NiTro451 1`\nIf you use this command outside of the official server, your response will still be directed to us. The `enjoyment` parameter is optional. If you wish to submit only enjoyment ratings, please use `g!enjoy`.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "user" in args:
        embed = discord.Embed(title="g!user <args>", \
        description="Lists ratings from a user. The username is case-sensitive! You can also specify the page, tier or ID at `args`, such as `tier 1`, `user mds62` or `id 26245696`.\nYou can also add `unrated` in `args` to look for levels that the user does not have submissions in! This can be used along with specifying a tier.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "enjoy" in args:
        embed = discord.Embed(title="g!enjoy <username> <levelname> <levelid> <creatorname> <tier>", \
        description="The command for submitting enjoyment ratings! For any parameter, if it includes spaces, wrap the whole input in double quotes. (\"\") For example: \n`g!enjoy \"Chris Wong\" \"Impact X\" 28461869 NiTro451 5`\n **Remember that 5 is the average rating! If you use this command outside of the official server, your response will still be directed to us.", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    print('ladder> Command execution complete.')


# ** Looping **
@tasks.loop(seconds=360)
async def change_status():
    await client.change_presence(activity=discord.Game("g!help"))


# ** Events **
@client.event
async def on_ready():
    print('ladder> Logged in as {0.user}'.format(client))
    change_status.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('g!ping'):
        print('ladder> Pinged. Responding.')
        await message.channel.send('Pong!')
    else:
        await client.process_commands(message)


keep_alive.keep_alive()  # putting bot to Flask to keep it alive
# see keep_alive.py

client.run(token)
