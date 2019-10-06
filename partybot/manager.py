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
        
        # get the command name
        cmd_name = msg.content.split(" ")[0][len(self.bot.config["prefix"]):]
        executer = await self.get_cmd(cmd_name)
        
        # execute
        await executer.execute(self.bot, msg)
        

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

    async def execute(self, bot, message, parameters={}, *args, **kwargs):
        async def run(bot, message, parameters, fn, *args, **kwargs):
            await fn(self, message=message, *args, **kwargs)
        return await run(bot, message, parameters, self.fn, *args, **kwargs)

    @property
    def command(self):
        return self._command

    @property
    def fn(self):
        return self._fn