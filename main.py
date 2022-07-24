# GD Demon Ladder Discord bot
# Written by RFMX, (c) 2021-2022

# ver 1.2-beta4

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
g!rating: Submits ratings.
g!enjoy: Submits ratings for enjoyment.
g!user: Shows ratings submitted by a user.
g!help: Shows info about commands.
"""

"""
Transferring this beta build towards the host will require multiple steps:
1) Modify prefix currently at line 62 to g!
2) Do the same at b!ping --> g!ping near the end of the script, currently at line 1107.
3) Comment everything regarding keep_alive, currently at lines 43 and 1114.
4) Uncomment everything regarding dot_env, currently at lines 42 and 47. 
"""

"""
TODO:
[DONE] g!level: Change to show the submitted ratings in pages
g!level [v], g!user, g!need [v]: Add enjoyment components.
g!rating, g!enjoy: Change the format to optimise the command
Add g!moreinfo or whatever
[DONE] Find out why it sends too many requests
"""

# ** Setup **
import logging, discord, asyncio, aiohttp, json, random, os, datetime, pytz, math#, dotenv
import keep_alive
from discord.ext import commands, tasks

emerald_sleep = False
#dotenv.load_dotenv()

random.seed(a=os.urandom(32))  # set seed for randomness
logging.basicConfig(level=logging.INFO)  # logging so that I see stuff
token = os.environ.get("TOKEN")  # Discord bot token
apikey = os.environ.get("APIKEY")  # Google sheets API key
sheetid = "1Cq6TcaXZU7w8jVpgy4pYpmI76ALwQqX7Mm8itETz9wU" # sheet in use
original_sheet = "1xaMERl70vzr8q9MqElr4YethnV15EOe8oL1UV9LLljc"
bot_sheet = "1Cq6TcaXZU7w8jVpgy4pYpmI76ALwQqX7Mm8itETz9wU"
gddladmins = {'439091096287707149', '556323843925475328', '374239444057849856', '940054294990827561'}

# * Discord bot set-up *
intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = commands.Bot(intents=intents, command_prefix='b!', help_command=None)

# * Color hex for tiers *
tierhex = (0xBBBBBB,
            0xDDDFEE, 0xD5D3E9, 0xD3CBE7, 0xD3C3E4, 0xD4BBE2, 0xD5B0DE, 0xDBA7DC, 0xDB9FD1, 0xD991C1, 0xDA86B0, 0xDB7698, 0xDC6A7D, 0xDD5A5A, 0xDC514C, 0xDA493E, 0xDA4535, 0xD93E26, 0xCD3F23, 0xC03A1B, 0xB23415, 0xA23010, 0x9B2B0C, 0x932B0B, 0x892608, 0x832607, 0x752105, 0x6C1E04, 0x601A02, 0x5A1802, 0x511700, 0x351100, 0x2C0C00, 0x1F0A00, 0x1A0800, 0x000001)
            
# * Prompts for g!need *
# * Prompts for easier demons (Tiers 1-10)
prompts_e = ("A Tier {0}, you say?", "Grinding demons, eh?",
             "An easier level won't hurt.", "You sure are improving.",
             "Here's your next goal.", "You'll be an expert someday.",
             "99% of the people can beat these. :joy: :ok_hand:",
             "Let me guess, you are beating an Extreme? No? Okay.",
             "Tier {0}? Gotcha.", "even harder than Back on Track tbh",
             "Finally pulling yourself to beat another demon, aren't you?",
             "Certified as Tier {0}, players approved",
            "So you're jumping from Bloodbath?", "so pro", "Your 62739th demon is:")
# * Prompts for harder demons (Tiers 11-35)
prompts_h = ("A Tier {0}, you say?", "Fancy a challenge, eh?",
             "I guess one of these would be your next hardest.", "Um, go?",
             "Honestly, everyone will be amazed if you beat these.",
             "Are you doing this for a demon roulette?",
             "99% of the people cannot beat these. :joy: :ok_hand:",
             "Yet another Medium Demon? Crap, wrong guess.",
             "On my way to deliver a Tier {0} to you.", "so free tbh",
             "Finally trying to have a new hardest, aren't you?",
             "Certified as Tier {0}, players approved", "So you're grinding after beating Deadlocked?", "skill issue", "Your 8.2039e294th demon is:")
# * Prompts for unrated demons
prompts_u = (
    "A Tier... unrated? I guess that's a tier.",
    "I see you're into stuff that is unknown.",
    "Yes. It helps the project grow. Do remember to drop a rating.",
    "Warning: enjoyability not guaranteed.", "I hope you run into Ouroboros.",
    "There's 90% of levels bearing a tier and you are picking these.",
    "I can't stop you from being the curious cat.",
    "Curiosity allows people to discover hidden gems.",
    "Maybe you can make a race out of these.",
    "Statistics shows that when there is one more rated level, there is one less unrated level.",
    "I'm guessing you are beating a Harder level. This is the Demon Ladder? Whatever.",
    "99% of the people think ads are boring. :joy: :ok_hand:",
    "Finally getting yourself to... what? Unrated?", "so random",
    "support the GD Demon Ladder thanks",
    "*inserts random quote about being random*", "So you're beating your first demon?", "random issues", "Your -387th demon is:")

# ** Request function **
async def request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("ladder> Status:", response.status)
            r_json = await response.text()
            r_json = json.loads(r_json)
            r_json = r_json['values']
    return r_json

# ** Commands **

# * G!BEAN: Beans. *
@client.command()
async def bean(ctx, person, *reason):
    print('ladder> Executing command __bean__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))

    # * Processing
    if "!" in person: personid = person[3:-1] # when the tag is in the form of <@!1234567890>
    else: personid = person[2:-1] # when the tag is in the form of <@1234567890>
    # print(person)
    # print(personid)

    # * Get user
    try:
        person_user = await client.fetch_user(personid) # see if personid is a tag
    except:
        if "#" in person:
            person_tag = person.split("#", 1) # cut away the discrim
            person_user = discord.utils.get(client.get_all_members(), name=person_tag[0], discriminator=person_tag[1])
        else:
            person_user = discord.utils.get(client.get_all_members(), name=person)

    # Start beaning
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

    # Await message and react
    def check(msg):
        return (msg.author == person_user)

    emoji = discord.utils.get(client.emojis, name='mrbean')
    msg = await client.wait_for('message', timeout=3600.0, check=check)
    await msg.add_reaction(emoji)
        
    print('ladder> Command execution complete.')

# * G!LEVEL: this receives a level ID then spits data about it *
@client.command(aliases=['map'])
async def level(ctx, id_search, *extra):
    print('ladder> Executing command __level__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))  # prompt in console

    # * Setup
    responsemsg = await ctx.channel.send(content="Processing...")
    global apikey
    demon_no = -1 # null response

    # * HTTP request to check for the row no. of demon
    try:
        int(id_search)
        assert len(extra) == 0
        id_search_type = "int"
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
            pass # demon_no will stay as -1
    except:
        id_search_type = "str"
        extra = list(extra)
        extra.insert(0, id_search)
        id_search = " ".join(extra)
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!A:A?key=" + apikey # URL construction
        print('ladder> Requesting to Google sheets for data at Column A.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
                demon_no_list = []
                demon_name_list = []
                for i in range(len(r_json)) :
                    if id_search.lower() in r_json[i][0].lower():
                        demon_no_list.append(i)
                        demon_name_list.append(r_json[i])
                    else:
                        words_in_level = True
                        for word in extra:
                            if not word.lower() in r_json[i][0].lower():
                                words_in_level = False
                                break
                        if words_in_level:
                            demon_no_list.append(i)
                            demon_name_list.append(r_json[i]) 

    # Determine type of query, and how many results are found

    if id_search_type == "int":
        pass
        
    elif len(demon_no_list) == 0:
        embed = discord.Embed(title="There is no demon with the name {0}!".format(id_search), \
        color=0xED4337)
        await responsemsg.edit(content="",embed=embed)
        print("ladder> Command execution complete.")
        return
        
    elif len(demon_no_list) == 1:
        demon_no = demon_no_list.pop()
        
    else:
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!B:B?key=" + apikey # URL construction
        print('ladder> Requesting to Google sheets for data at Column B.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
        for i in demon_no_list:
            index = demon_no_list.index(i)
            demon_name_list[index].append(r_json[i][0])
            
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!E:E?key=" + apikey # URL construction
        print('ladder> Requesting to Google sheets for data at Column E.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
        for i in demon_no_list:
            index = demon_no_list.index(i)
            demon_name_list[index].append(r_json[i][0])

        embed_list = []
        j = 0
        for i in demon_name_list:
            j += 1
            embed_list.append("{0} by {1} ({2})".format(i[0], i[1], i[2]))
            if j >= 10:
                embed_list.append("...and {0} more.".format(len(demon_name_list)-10))
                break
        embed_text = "\n".join(embed_list)
        
        embed = discord.Embed(title="Your search yields multiple results.", description=embed_text, color=0xED4337)
        embed.set_footer(text="Use g!level with the ID to see the information of the level, or lengthen your search query to reduce the number of results.")
        await responsemsg.edit(content="",embed=embed)
        return
                    
    # * HTTP request to obtain demon info in main list
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
                id_display = r_json[4]
                gdbrowser_url = 'https://gdbrowser.com/' + id_display
                creator = r_json[1]
                song = r_json[2]
                officialdiff = r_json[3]
                if r_json[5] != "unrated":
                    tier = r_json[5]
                    tier2dp = r_json[6]
                    ratings = []
                    i = 7
                    try:
                        while r_json[i] != '':
                            ratings.append([r_json[i], r_json[i+1]])
                            i += 2
                    except:
                        pass
                else:
                    tier = 'Unrated'
                    tier2dp = None
                    ratings = None

    # * HTTP request to obtain demon info in side list
    # this code block is still under if demon_no != -1
        row_select = "'Side List'!" + str(row_no) + ":" + str(row_no) # construct area in A1 notation
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/" + row_select + "?key=" + apikey # URL cnstruction again
        print('ladder> Requesting to Google sheets for SIDE list data at row {0}'.format(
            row_no))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']
                r_json = r_json[0]

                if r_json[5] != "unrated":
                    tier_e = r_json[5]
                    tier2dp_e = r_json[6]
                    ratings_e = []
                    i = 7
                    try:
                        while r_json[i] != '':
                            ratings_e.append([r_json[i], r_json[i+1]])
                            i += 2
                    except:
                        pass
                else:
                    tier_e = 'Unrated'
                    tier2dp_e = None
                    ratings_e = None
                    
    # * Constructing embed
    if demon_no != -1:
        if tier != 'Unrated':            
            embed = discord.Embed(title="Level information of {0} ({1})".format(name, id_display), url=gdbrowser_url, color=tierhex[int(tier)])
        else:            
            embed = discord.Embed(title="Level information of {0} ({1})".format(name, id_display), url=gdbrowser_url, color=tierhex[0])

        # * Fun section, TODO rewrite this section so that this obtains info from an external file
        # if id_search == "60660086":
        #    embed.set_footer(text="- Tier what the fuck do you mean multition 6")
        # elif id_search == "76074130":
        #    embed.set_footer(text="i too love consuming vast amounts of chlorine!")
        
        embed.add_field(name="Creator", value=creator, inline=True)
        embed.add_field(name="Song", value=song, inline=True)
        embed.add_field(name="Official Difficulty",
                        value=officialdiff,
                        inline=True)

        # * Setup
        ratings_active = ratings
        tier_active = tier
        tier2dp_active = tier2dp
        tiertext_active = "Tier "
        active = "difficulty"
        switchloop = True
        def replace():
            nonlocal active, ratings_active, tier_active, tier2dp_active, tiertext_active
            if active == "difficulty":
                ratings_active = ratings_e
                tier_active = tier_e
                tier2dp_active = tier2dp_e
                tiertext_active = ""
                active = "enjoyment"
            else:
                ratings_active = ratings
                tier_active = tier
                tier2dp_active = tier2dp
                tiertext_active = "Tier "
                active = "difficulty"
        
        while switchloop == True:
            switchloop = False
            if tier_active != 'Unrated':
                embed.add_field(name="{0} Tier".format(active.title()),
                                value="{0}{1} ({2})".format(tiertext_active, tier_active, tier2dp_active),
                                inline=False)
            else:
                embed.add_field(name="{0} Tier".format(active.title()), value="Unrated", inline=False)
            if ratings_active != None:
                loop = True
                if len(ratings_active) > 10:
                    totalpages = int(math.ceil(len(ratings_active) / 10))
                    page = 0
                    await responsemsg.add_reaction("⬅️")
                    await responsemsg.add_reaction("➡️")
                    await responsemsg.add_reaction("🔁")
                    while loop:
                        if len(ratings_active) < 10 * (page + 1):
                            display_range = range(10 * page, len(ratings_active))
                        else:
                            display_range = range(10 * page, 10 * (page + 1))
                        ratingtext = ""
                        for i in display_range:
                            ratingtext = "".join([ratingtext, "- {0}{1} by {2}\n".format(tiertext_active, ratings_active[i][0], ratings_active[i][1])])
                        embed.add_field(name="Submitted ratings (Page {0} of {1})".format(page + 1, totalpages),
                                    value=ratingtext,
                                    inline=True)
                        await responsemsg.edit(content="", embed=embed)
                        print(
                            "ladder> Command execution complete with samples generated. Printed Page {0}. Awaiting further response."
                            .format((page + 1)))
    
                        def check(reaction, user):
                            return (user == ctx.author and (str(reaction.emoji) == "⬅️" or str(reaction.emoji) == "➡️" or str(reaction.emoji) == "🔁"))
    
                        try:
                            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                            embed.remove_field(-1)
                            if reaction.emoji == "⬅️":
                                if page > 0: page -= 1
                                elif page == 0: page = totalpages - 1
                            elif reaction.emoji == "➡️":
                                if page < (totalpages - 1): page += 1
                                elif page == (totalpages - 1): page = 0
                            elif reaction.emoji == "🔁":
                                print("ladder> Switching between main and side list.")
                                await responsemsg.remove_reaction("🔁", ctx.author)
                                switchloop = True
                                embed.remove_field(-1)
                                replace()
                                break
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
                    ratingtext = ""
                    for i in ratings_active:
                        ratingtext = "".join([ratingtext, "- {0}{1} by {2}\n".format(tiertext_active, i[0], i[1])])
                    embed.add_field(name="Submitted ratings",
                                    value=ratingtext,
                                    inline=True)
                    await responsemsg.edit(content="",embed=embed)

                    await responsemsg.add_reaction("🔁")
                    def check(reaction, user):
                        return (user == ctx.author and (str(reaction.emoji) == "🔁"))

                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                        print("ladder> Switching between main and side list.")
                        await responsemsg.remove_reaction("🔁", ctx.author)
                        embed.remove_field(-1)
                        embed.remove_field(-1)
                        switchloop = True
                        replace()
                    except asyncio.TimeoutError:
                        loop = False
                        print("ladder> Timeout.")
            else:
                await responsemsg.edit(content="",embed=embed)
                await responsemsg.add_reaction("🔁")
                def check(reaction, user):
                    return (user == ctx.author and (str(reaction.emoji) == "🔁"))

                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                    print("ladder> Switching between main and side list.")
                    await responsemsg.remove_reaction("🔁", ctx.author)
                    embed.remove_field(-1)
                    switchloop = True
                    replace()
                except asyncio.TimeoutError:
                    loop = False
                    print("ladder> Timeout.")
    else:
        embed = discord.Embed(title="There is no demon with the ID {0}!".format(id_search), \
        color=0xED4337)
        await responsemsg.edit(content="",embed=embed)

    print('ladder> Command execution complete.')

# * G!NEED: Generates random demons for a specified tier, or unrated demons
@client.command(aliases=['random'])
async def need(ctx, needtier, *needextra):
    global apikey
    print('ladder> Executing command __need__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    try:
        # * Setup
        responsemsg = await ctx.channel.send(content="Processing...")
        needtier = int(needtier)
        if needtier <= 0 or needtier >= 36:
            raise Exception("Tier out of range")

        if needtier <= 10: etitle = prompts_e[random.randrange(len(prompts_e))]
        else: etitle = prompts_h[random.randrange(len(prompts_h))]

        embed = discord.Embed(title=etitle.format(needtier), \
        description="*If you wish to generate a new set of demons, react with :repeat:.*", \
        color=tierhex[needtier])

        try: needenjoy = int(needextra[0])
        except: needenjoy = 0
        
        # * HTTP request and check for requirements

        result = []
        
        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'The List'!A:F?majorDimension=COLUMNS&key=" + apikey
        print(
            'ladder> Requesting to Google sheets for data at Columns A to F.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']

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

        url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'Side List'!A:F?majorDimension=COLUMNS&key=" + apikey
        print(
            'ladder> Requesting to Google sheets for data at Columns A to F.')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("ladder> Status:", response.status)
                r_json = await response.text()
                r_json = json.loads(r_json)
                r_json = r_json['values']

                list = []
                try:
                    while True:
                        check_list = result.pop(0)
                        try:
                            check_try = int(r_json[5][check_list])
                        except:
                            check_try = 0
                        if needenjoy <= check_try:
                            list.append(check_list)  # comparison check
                except:
                    pass
                try:
                    while True:
                        result.append(list.pop(0))
                except:
                    pass

        # * Embed construction
        loop = True
        while loop:  # the loop is for repeated generation of demons
            embed.clear_fields()
            if len(result) >= 5:
                for i in random.sample(result, 5):
                    embed.add_field(name="{0}".format(r_json[0][i]), \
                    value="{0}".format(r_json[4][i]), \
                    inline=True)
            elif len(result) >= 1:
                embed.add_field(name="Only {0} demons are found.".format(len(result)), \
                    value="As such, only 1 demon is shown.", \
                    inline=False)
                for i in random.sample(result, 1):
                    embed.add_field(name="{0}".format(r_json[0][i]), \
                    value="{0}".format(r_json[4][i]), \
                    inline=True)
            else:
                embed = discord.Embed(title="No results are found with your settings!", \
                color=0xED4337)
                await responsemsg.edit(content="", embed=embed)
                print(
                "ladder> Command execution complete as no results are found."
            )
                break
            await responsemsg.edit(content="", embed=embed)
            await responsemsg.add_reaction("🔁")

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

                url = "https://sheets.googleapis.com/v4/spreadsheets/" + sheetid + "/values/'Side List'!A:F?majorDimension=COLUMNS&key=" + apikey
                print(
                    'ladder> Requesting to Google sheets for data at Columns A to F.')
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        print("ladder> Status:", response.status)
                        r_json = await response.text()
                        r_json = json.loads(r_json)
                        r_json = r_json['values']
        
                        list = []
                        try:
                            while True:
                                check_list = result.pop(0)
                                try:
                                    check_try = int(r_json[5][check_list])
                                except:
                                    check_try = 0
                                if needenjoy <= check_try:
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
                embed = discord.Embed(title="Enter the tier as an integer from 1 to 35!", \
                color=0xED4337)
                await responsemsg.edit(content="", embed=embed)
                print(
                    'ladder> Command execution complete as tier is of incorrect syntax.'
                )
        except:
            embed = discord.Embed(title="Enter the tier as an integer from 1 to 35!", \
            color=0xED4337)
            await responsemsg.edit(content="", embed=embed)
            print(
                'ladder> Command execution complete as tier is of incorrect syntax.'
            )

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
New response submitted at {0} UTC by {1}
This is a NORMAL response.
User: {2}
Refresh rate: {3}
Level Name: {4}
ID: {5}
Creator: {6}
Rated Tier: {7}
Rated Enjoyment: {8}
Dropped string: {9}
    """.format(
        str(datetime.datetime.now(tz=pytz.utc))[0:-13], ctx.author, playername,
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
- New response submitted at {0} UTC by {1}
**THIS IS AN ENJOYMENT SUBMISSION**
- User: {2}
- Level Name: {3}
- ID: {4}
- Creator: {5}
- Rated Enjoyment: {6}
- Dropped string: {7}
    """.format(
        str(datetime.datetime.now(tz=pytz.utc))[0:-13], ctx.author, playername,
        levelname, levelid, creator, levelenjoy, dropped))
    print('ladder> Command execution complete.')

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
                    if reaction.emoji == "⬅️":
                        if page > 0: page -= 1
                        elif page == 0: page = totalpages - 1
                    elif reaction.emoji == "➡️":
                        if page < (totalpages - 1): page += 1
                        elif page == (totalpages - 1): page = 0
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

# * G!SEND: GDDL Administrator only, sends ID to boss *
@client.command()
@commands.is_owner()
async def send(ctx, idcall):
    print('ladder> Executing command __send__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(933282895576051792)
    embed = discord.Embed(title="Sending to boss...", color=0xED4337)
    stringcall = "Level ID: " + idcall
    embed.set_footer(text=stringcall)
    await channel.send(embed=embed)
    print('ladder> Command execution complete.')

# * G!MESSAGE: Moderators only, make bot talk *
@client.command()
@commands.has_permissions(manage_messages=True)
async def message(ctx, *, message):
    print('ladder> Executing command __message__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    await ctx.message.delete()
    await ctx.channel.send(message)
    print('ladder> Command execution complete.')

# * G!REMOTE: GDDL Admins only, make bot talk in another channel*
@client.command()
@commands.is_owner()
async def remote(ctx, channelid, *, message):
    print('ladder> Executing command __remote__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(int(channelid))
    await channel.send(message)
    print('ladder> Command execution complete.')

# * G!ANNOUNCE: GDDL Admins only, make bot talk at #announcement*
@client.command()
@commands.is_owner()
async def announce(ctx, *, message):
    print('ladder> Executing command __announce__ in {0}, {1} initiated by {2}'.format(ctx.channel, ctx.guild, ctx.author))
    channel = client.get_channel(756512731124727988)
    await channel.send(message)
    print('ladder> Command execution complete.')

# * G!STATUS: GDDL Administrators only, change the status of the bot *
# this is just for legacy purposes, now the bot does it automatically
@client.command()
@commands.is_owner()
async def status(ctx, playing):
    print('ladder> Executing command __status__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    await client.change_presence(activity=discord.Game(playing))

# * G!HELP: Information about commands *
@client.command(aliases=['info'])
async def help(ctx, *args):
    print('ladder> Executing command __help__ in {0}, {1} initiated by {2}'.
          format(ctx.channel, ctx.guild, ctx.author))
    args = list(args)
    if len(args) == 0:
        embed = discord.Embed(title="LadderBot help", \
        description="This is a list of commands you can use! Parameters are enclosed in <>s.\nFor more info, join the following server: https://discord.gg/gddl", \
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
        embed = discord.Embed(title="g!level <id or name>", \
        description="**Aliases:** g!map\nShows information about the level in the list. This includes the current tier and submitted ratings. Press the :repeat: button to switch between difficulty and enjoyment ratings!\n", \
        color=0xCCFF00)
        await ctx.send(embed=embed)
    elif "need" in args:
        embed = discord.Embed(title="g!need <difficulty> <enjoyment>", \
        description="**Aliases:** g!random\nGet 5 random levels from your specified tier! There is also an `unrated` tier!\n\nIf you also fill in the enjoyment rating, only levels that has the enjoyment tier above it will be shown!", \
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

@tasks.loop(seconds=7200)
async def source_update():
    global sheetid
    print("ladder> 2 hour check on whether main is useable.")
    url = "https://sheets.googleapis.com/v4/spreadsheets/" + original_sheet + "/values/'The List'!E:E?majorDimension=ROWS&key=" + apikey
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == "200":
                sheetid = original_sheet
            else:
                sheetid = bot_sheet
            
    
# ** Events **
@client.event
async def on_ready():
    print('ladder> Logged in as {0.user}'.format(client))
    change_status.start()

@client.event
async def on_message(message):
    global emerald_sleep
    if message.author == client.user:
        return

    if (message.author == client.get_user(556323843925475328) and emerald_sleep == True):
        check_time = datetime.datetime.utcnow().time()
        if check_time >= datetime.time(18,0) and check_time <= datetime.time(23,0):
            response_msg = await message.channel.send('Stop resisting and just sleep, <@556323843925475328>.')
            print('ladder> Asking Emerald to sleep.')
            await asyncio.sleep(15)
            await response_msg.delete()

    if (message.author == client.get_user(439091096287707149) and emerald_sleep == True):
        check_time = datetime.datetime.utcnow().time()
        rd = random.randint(1,100)
        if (check_time >= datetime.time(18,0) and check_time <= datetime.time(23,0)) and rd == 1:
            response_msg = await message.channel.send('Don\'t think you can get away from this, <@439091096287707149>.')
            print('ladder> Asking RFMX to sleep.')
            await asyncio.sleep(15)
            await response_msg.delete()
    
    if message.content.startswith('b!ping'):
        print('ladder> Pinged. Responding.')
        await message.channel.send('Pong!')
    else:
        await client.process_commands(message)


keep_alive.keep_alive()  # putting bot to Flask to keep it alive
# see keep_alive.py

client.run(token)
