class Commands:
    def __init__(self, command, help):
        self.command = command
        self.help = help
    
    def get_command(self):
        return self.command
    
    def get_help(self):
        return self.help