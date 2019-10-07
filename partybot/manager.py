import inspect

cmds = []

class CommandRouter(object):
    """Router used to use the correct function for the command."""
    def __init__(self, bot):
        self._bot = bot

    async def handle(self, msg):
        # Check if the user is addressing to the bot
        if not msg.content.startswith(self.bot.config["prefix"]):
            return

        # Start typing indicator
        await msg.channel.trigger_typing()
        
        # get the command name
        cmd_name = msg.content.split(" ")[0][len(self.bot.config["prefix"]):]
        executer = await self.get_cmd(cmd_name)
        arguments = msg.content.split(" ")
        del arguments[0]
        
        # execute
        try:
            await executer.execute(self.bot, msg, arguments)
        except AttributeError as e:
            if "object has no attribute 'execute'" in str(e):
                print(msg.author,"tried to execute command",self.bot.config["prefix"] + cmd_name,"but command does not exist!")
                await msg.channel.send("**Error:** Command not found.")
            else:
                raise e
        

    async def get_cmd(self, cmd):
        """Returns the function that will handle the command."""
        for command in cmds:
            if command.command.lower() == cmd.lower():
                return command
        
    async def add_cmd(self, cmd):
        """Adds a command to the command handler."""
        for command in cmds:
            if command.command is cmd.command:
                print("Potential endpoint conflict for command {0}".format(cmd.command))
        cmds.append(cmd)

    async def has_command(self, cmd):
        """Checks if the server has a command."""
        return True if self.get_cmd(cmd) is not None else None
    
    @property
    def bot(self):
        return self._bot

class CommandHandler(object):
    """Decorator used to link a command to a function."""
    def __init__(self, command):
        self._command = command
        cmds.append(self)

    def __call__(self, fn, *args, **kwargs):
        self._fn = fn

    async def execute(self, bot, msg, arguments=[], *args, **kwargs):
        async def run(bot, msg, arguments, fn, *args, **kwargs):
            await fn(bot, msg=msg, arguments=arguments, *args, **kwargs)
        return await run(bot, msg, arguments, self.fn, *args, **kwargs)

    @property
    def command(self):
        return self._command

    @property
    def fn(self):
        return self._fn