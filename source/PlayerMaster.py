class Player:
    def __init__(self, name):
        self.name = name
        self.code = "None"
    
    def get_name(self):
        return self.name
    
    def set_code(self, code):
        self.code = code
    
    def get_code(self):
        return self.code


class PlayerMaster:
    def __init__(self):
        self.players = []

    def add_player(self, player_name):
        flag = True
        for player in self.players:
            if player.get_name() == player_name:
                flag = False
        if flag:
            self.players.append(Player(player_name))
        return flag
    
    def remove_player(self, player_name):
        flag = False
        for i, player in enumerate(self.players):
            if player.get_name() == player_name:
                self.players.pop(i)
                flag = True
        return flag
    
    def remove_all(self):
        self.players = []
    
    def display_players(self):
        ret_str = "\n".join([
            f"{i + 1}: {self.players[i].get_name()}"
            for i in range(len(self.players))
        ])
        return ret_str