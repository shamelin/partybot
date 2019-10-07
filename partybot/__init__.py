import os
for name in os.listdir("partybot/commands"): # iterate for each file present in the partybot/commands folder
    if name.endswith(".py"): # if it is an importable file
         globals()[name[:-3]] = __import__(os.path.join("partybot.commands." + name[:-3])) # import!