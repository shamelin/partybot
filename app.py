# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml

class Lucio(object):
    def __init__(self):
        self.load_config()
        print(self.config["hello"])

    def load_config(self):
        self.file = open("config.txt")
        self.config = yaml.load(self.file, Loader=yaml.FullLoader)

Lucio()