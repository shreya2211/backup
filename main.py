from serverSetup import *
from client.imports import * # client imports
from server.imports import * # server imports
import discord

print("Starting up...") # Notify file was run

@client.event
async def on_ready():
    '''
    Asynchronous function that runs when bot is ready, changes status, and prints message
    Reference: https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    '''
    #await client.change_presence(game=discord.Game(name='with your grades bwahahaha'))
    print("Bot is online")


admin_channel = -1
reporting_channel = -1

@client.event
async def on_message(message):
    '''
    Welcome to the Cyberbullying Detection and Assistance Tool. If you just got started, type `!setup` to initialize the server.
    Commands
    --------
    `!setup`: creates necessary channels, roles, and 
    `!add [str]`: adds the string to the list of bad words
    `!delete [str]`: deletes the string from the list of bad words
    `!print`: sends out the current bad words
    `!names`: list out all users who have sent at least 1 message
    `!swears`: list out swears for all users
    `!swears [user object]`: list out swears for that user
    `!report [message id]`: reports a message
    `!roleAdd [user] [role]`: adds a role to the user
    `!roleDelete [user] [role]`: deletes a role from the user
    `!help`: displays this message
    '''

    global baddiesList
    global users
    global admin_channel
    global users, userIDs

    '''
    Update database if it's a new user
    '''
    if str(message.author.id) not in userIDs:
        if "Seidelion" in [y.name for y in message.author.roles]:
            newUser = seidelions.Seidelion(str(message.author.id),str(message.author),userDatabase,0,"Seidelion",0)
        else:
            newUser = user.User(str(message.author.id),str(message.author),userDatabase,0,"User")
        users.append(newUser)
        userIDs.append(str(message.author.id))
        newUser.insert()

    '''
    Predefine commonly used values to increase reusability
    '''
    inputText = message.content # Text of the message
    currentUser = users[userIDs.index(str(message.author.id))] # The current user typing
    mentionedUser_index = -1 # The index of the user mentioned
    if len(message.mentions) > 0:

        def binarySearch(idList,idToFind): 
            '''Binary Search to get index of mentioned user in the "users" array
            
            Parameters
            ----------
            idList: int[]
                the list of ids
            
            idToFind: int
                the id to be found
            Returns
            -------
            int:
                the index of the mentioned user
                -1 if not found
            '''

            first = 0
            last = len(idList) - 1
            while first <= last: 
        
                mid = (first+last)//2

                if idList[mid] == idToFind: 
                    return mid 
        
                elif idList[mid] < idToFind: 
                    first = mid + 1
        
                else:
                    last = mid - 1

            return -1

        mentionedUser_index = binarySearch(userIDs,message.mentions[0].id)

    admin_channel, reporting_channel = -1, -1
    for channel in message.guild.channels:
        if channel.name == "administration":
            admin_channel = discord.Object(id=channel.id)
            #....
            admin_channel_obj=message.guild.get_channel(channel.id)
        if channel.name == "reporting":
            reporting_channel = discord.Object(id=channel.id)
            #....
            report_channel_obj=message.guild.get_channel(channel.id)

    hasNoChannel = admin_channel == -1 or reporting_channel == -1
    isCommand = inputText.startswith("!") and not inputText == "!setup"
    if hasNoChannel and isCommand:
        await message.channel.send(content="The channels 'administration' and/or 'reporting' are not found. Please initialize setup by typing `!setup`")

    '''
    Administrative Functions
    '''
    # tempUser = message.guild.get_member(int(BOTID))
    # for channel in client.get_all_channels():
    #     channel1=message.guild.get_channel(channel.id)
    #     print(channel1)
    if inputText.startswith("!setup"):
        if hasNoChannel:
            # try:
                # Reusable Components
                server = message.guild
                everyone = discord.PermissionOverwrite(read_messages=False, send_messages=False)
                mine = discord.PermissionOverwrite(read_messages=True)

                # Create Seidelion Role
                role = await server.create_role(name='Seidelion', colour=discord.Colour(0x0FF4C6))
                #role = await server.create_role(message.guild, name='Seidelion', colour=discord.Colour(0x0FF4C6))
                await message.author.add_roles(role)
                #await client.add_roles(message.author, role)

                # Create Administration Channel
                overwrites = {
                    server.default_role: everyone,
                    server.me: mine
                }
                await server.create_text_channel(name='administration', overwrites =overwrites)
                overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                rolesearch = discord.utils.get(server.roles, name="Seidelion")
                #await client.edit_channel_permissions(message.channel, rolesearch, overwrite)
                await message.channel.set_permissions(target =rolesearch, overwrite=overwrite)
                await message.channel.send(content="The 'administration' channel has been added!")

                # Creating Reporting Channel
                await server.create_text_channel(name='reporting', overwrites=overwrites)
                overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                rolesearch = discord.utils.get(server.roles, name="Seidelion")
                await message.channel.set_permissions(target =rolesearch, overwrite=overwrite)
                await message.channel.send(content="The 'reporting' channel has been added!")

                # Add Role to Admin
                currentUser.updateRole("Seidelion")

                # Update User Database for Admin
                currentUser = seidelions.Seidelion(currentUser.id,currentUser.name,userDatabase,currentUser.swearCount,"Seidelion",0)
                await message.channel.send(content="Successfully assigned role %s to %s" % (role, message.author))

                # Add User Role for Mr Seidel
                tempUser = message.guild.get_member(int(BOTID))
                print(BOTID)
                await tempUser.add_roles(role)

                # Update User Database for Mr Seidel
                tempUserObject = users[userIDs.index(BOTID)]
                tempUserObject.updateRole("Seidelion")
                users[mentionedUser_index] = seidelions.Seidelion(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"Seidelion",0)
                await message.channel.send(content="Successfully assigned role 'Seidelion' to self")

                # Initialize custom classifier
                classifiers.qClassifier_init()
                await message.channel.send(content="Successfully created and reset custom classifier")
            # except Exception as e:
            #     print(e)
            #     await client.send_message(message.channel, "Oh no! Something went horrendously wrong.")
        else:
            await message.channel.send(content="Server is already set up")
    
    elif inputText == "!help":
        await message.channel.send(on_message.__doc__)
    
    '''
    Functions relating to users
    '''
    if inputText.startswith("!names"):
        for u in users:
            await message.channel.send(u.display())

    # Add / Remove roles
    if inputText.startswith("!role"):
        isCorrectFormat = inputText.count(' ') == 2 and len(message.mentions) == 1
        isRealRole = inputText.split()[2] in [y.name for y in message.server.roles]
        hasPermissions = currentUser.perms == "Seidelion"

        # Add Roles
        if message.mentions[0].id == BOTID:
            await message.channel.send("Sorry, but you can't edit a bot's roles.")

        elif inputText.startswith("!roleAdd") and isCorrectFormat and isRealRole and hasPermissions:
            tempUser = message.server.get_member(message.mentions[0].id)
            role = message.server.roles[([y.name for y in message.server.roles].index(inputText.split()[2]))]
            try:
                await client.add_roles(tempUser, role)
                await message.channel.send("Successfully assigned role %s to %s" % (role, tempUser))

                if inputText.split()[2] == "Seidelion":
                    tempUserObject = users[mentionedUser_index]
                    tempUserObject.updateRole("Seidelion")

                    users[mentionedUser_index] = seidelions.Seidelion(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"Seidelion",0)
            except Exception as e:
                print(e)
                await message.channel.send("Oh No! Something went wrong!")

        # Remove Role
        elif inputText.startswith("!roleRemove") and isCorrectFormat and isRealRole and hasPermissions:
            tempUser = message.server.get_member(message.mentions[0].id)
            role = message.server.roles[([y.name for y in message.server.roles].index(inputText.split()[2]))]
            try:
                await client.remove_roles(tempUser, role)
                await message.channel.send("Successfully removed role %s from %s" % (role, tempUser))

                if inputText.split()[2] == "Seidelion":
                    tempUserObject = users[mentionedUser_index]
                    tempUserObject.updateRole("User")
                    users[mentionedUser_index] = user.User(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"User")
            except Exception as e:
                print(e)
                await message.channel.send("Oh No! Something went wrong!")

        if not hasPermissions:
            await message.channel.send("You don't have the permissions to do that!")
        if not isCorrectFormat:
            await message.channel.send("There's a problem with your input. Please make sure it's `!roleAdd/roleRemove @user rolename`")
        if not isRealRole:
                await message.channel.send("That's not a real role!")

    elif inputText.startswith("!swears"):

        if len(message.mentions) == 0:
            def quickSort(usersArr):
                '''Recursive quicksort to sort the users by swears
                
                Paramters
                ---------
                usersArr: users[]
                    the user array
                
                Returns:
                    users[]: a sorted user array
                '''

                if len(usersArr)==0: return []
                if len(usersArr)==1: return usersArr
                left = [i for i in usersArr[1:] if i.swearCount > usersArr[0].swearCount]
                right = [i for i in usersArr[1:] if i.swearCount <= usersArr[0].swearCount]
                return quickSort(left)+[usersArr[0]]+quickSort(right)

            users = quickSort(users)
            for u in users:
                await message.channel.send("Swear Count for %s - %s" % (u.name,u.swearCount))

        else:
            try:
                mentionedUser = users[mentionedUser_index]
                await message.channel.send(mentionedUser.swearCount)
            except ValueError as e:
                print(e)
                await message.channel.send("This user does not exist")
    
    '''
    Functions relating to Cyberbullying Reporting
    '''

    # Prints the bad word list
    if inputText.startswith("!print"):
        await message.channel.send(wordFilter.printAll())

    if currentUser.perms == "Seidelion":
        # Add Bad Words
        if inputText.startswith("!add ") and inputText.count(' ') > 0:
            mes = inputText.split()[1]
            if mes in baddiesList:
                await message.channel.send("Word already added")
            else:
                wordFilter.insert(mes,baddiesList) # Run and get status
                await message.channel.send("Successfully added %s to database" % mes)
                baddiesList.append(mes)

        # Remove Bad Words
        elif inputText.startswith("!delete") and inputText.count(' ') > 0:
            mes = inputText.split()[1]

            if mes in baddiesList:
                wordFilter.delete(mes)
                await message.channel.send("Successfully deleted %s from database" % mes)
                baddiesList = wordFilter.fetch()
            else:
                await message.channel.send("You silly. %s is not even a banned word!" % mes)

    # Print Bad Words
    elif inputText.startswith("!print"):
        await message.channel.send(wordFilter.printAll())
    
    # Checks and classifiers messages
    # elif not currentUser.perms == "Seidelion":
    if not message.author.name =="ReplyBot":
        print("check1")
        print(inputText)
        cyberbullying_confidence = classifiers.isCyberbullying(inputText,baddiesList)
        print(cyberbullying_confidence)
        if cyberbullying_confidence > 0:
            print("check3")
            currentUser.updateSwears()
            await message.channel.send("Hey! Don't be such a downer! Confidence: %s %%" % cyberbullying_confidence)
            await report_channel_obj.send("!report %s" % message.id)

    # Classification Feedback Mechanism
    if message.author.id == BOTID and message.channel.id == admin_channel.id and len(message.embeds) > 0:
        reactions = ['👍','👎']
        for emoji in reactions:
            await message.add_reaction(emoji)

        searching_for_a_meaning_in_life = True
        while searching_for_a_meaning_in_life:
            res = await client.wait_for('reaction_add')

            if res.user.id == BOTID: # Prevents time delay glitch where bot recognizes own reaction
                continue

            elif res.reaction.emoji == '👍':
                tempMesID = message.embeds[0]['fields'][0]["value"]
                tempContent = message.embeds[0]['fields'][1]["value"]
                tempChanID = message.embeds[0]['fields'][2]["value"]

                # Delete Message
                tempChan=message.guild.get_channel(tempChanID)
                #...
                #tempMsg = await discord.Object(id=tempChanID).get_message(tempMesID)
                tempMsg = await tempChan.fetch_message(tempMesID)
                await tempMsg.delete_message()

                # Train Classifier
                classifiers.qClassifier_train(tempContent,'neg')

            elif res.reaction.emoji == '👎':
                tempContent = message.embeds[0]['fields'][1]["value"]

                # Train Classifier
                classifiers.qClassifier_train(tempContent,'pos')

    if inputText.startswith("!report") and inputText.count(' ') > 0:
        if "Seidelion" in [y.name for y in message.author.roles]:
            reportID = inputText.split(' ', 1)[1]
            reportMessage = None
            for channel in client.get_all_channels():
                try:
                    channel1=message.guild.get_channel(channel.id)
                    reportMessage = await channel1.fetch_message(reportID)
                    print(reportMessage)
                except Exception as e:
                    continue
            await admin_channel_obj.send(embed=currentUser.report(reportID,reportMessage))

# Run the Bot
client.run(TOKEN)