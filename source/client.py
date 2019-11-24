import discord
import asyncio
import random
from source.PlayerMaster import PlayerMaster
from source.Commands import Commands


COMMANDS = {
    "HELP": Commands("!help", "今見ているこの画面を表示します。"),
    "JOIN": Commands("!join", "ゲーム参加メンバーリストに追加されます。"),
    "LEAVE": Commands("!leave", "ゲーム参加メンバーリストから除外されます。"),
    "RESET": Commands("!reset", "ゲーム参加メンバーリストを全消去します。"),
    "SHOW_PLAYERS": Commands("!showplayers", "ゲーム参加メンバーリストを表示します。"),
    "SHOW_CODES": Commands("!showcodes", "ゲームに使用するタブーコードの一覧を表示します。"),
    "SET_CODES": Commands("!editcodes", "ゲームに使用するタブーコードの編集モードに移ります。"),
    "REMOVE_CODE": Commands("!removecode", "タブーコードを削除します。後ろに半角スペースを開けて削除するタブーコードを入力してください。"),
    "ADD_CODE": Commands("!addcode", "タブーコードを追加します。後ろに半角スペースを開けて追加するタブーコードを入力してください。"),
    "START": Commands("!startgame", "ゲームを開始します。"),
    "HIT": Commands("!hit", "タブーコードを犯したプレイヤーをIDで指定してください。ヒットマンに殺されます。")
}


class TCClient(discord.Client):
    async def on_ready(self):
        print("------------")
        print("Logged in as")
        print(self.user.name)
        print("------------")
        self.initialize()
    
    async def on_message(self, message):
        sep = message.content.split(" ")
        author = message.author
        if message.content == COMMANDS["START"].get_command():
            print(COMMANDS["START"].get_command() + " sent")

        try:
            if sep[0] in self.allowed_commands_per_phase[self.phase]:
                gen = self.function_dictionary[sep[0]](sep[1:], author)
                if gen:
                    for mem, mes in gen:
                        await self.send_message(mem, mes)
        except KeyError:
            pass
    
    async def send_message(self, name, message):
        if name == "gamech":
            await self.get_channel(self.gamech_id).send(message)
        else:
            for member in self.members:
                if member.name == name:
                    dm = await member.create_dm()
                    await dm.send(message)
                    break
    
    def help(self, args, author):
        ret_mes = "\n".join([
            f"{com.get_command()}: {com.get_help()}" for com in COMMANDS.values()
        ])
        yield "gamech", ret_mes
    
    def join(self, args, author):
        if self.playermaster.add_player(author.name):
            ret_mes = f"{author.name}の参加を承りました。"
            yield "gamech", ret_mes
    
    def leave(self, args, author):
        if self.playermaster.remove_player(author.name):
            ret_mes = f"{author.name}の参加を取り消しました。"
            yield "gamech", ret_mes
    
    def reset(self, args, author):
        self.playermaster.remove_all()
        ret_mes = "参加メンバーをリセットしました。"
        yield "gamech", ret_mes
    
    def show_players(self, args, author):
        ret_mes = "ID: 名前\n" \
                + "==========\n" \
                + self.playermaster.display_players()
        yield "gamech", ret_mes
    
    def show_codes(self, args, author):
        ret_mes = "登録されたタブーコードの一覧です。\n" \
                + "===========================\n" \
                + "\n".join([self.codes[i] for i in range(len(self.codes))]) + "\n" \
                + "==========================="
        yield author.name, ret_mes
    
    def set_codes(self, args, author):
        if self.phase == "codes_edit":
            print("Got into \"standby\"")
            with open(self.code_path, "w") as f:
                f.write("\n".join(self.codes))
            self.phase = "standby"
            ret_mes = "待機モードに戻りました。"
        else:
            print("Got into \"codes_edit\"")
            self.phase = "codes_edit"
            ret_mes = "タブーコード編集モードに入りました。待機モードに入るにはもう一度このコマンドを送ってください。"
        yield author.name, ret_mes
    
    def remove_code(self, args, author):
        rem_count = 0
        for arg in args:
            try:
                self.codes.remove(arg)
                rem_count += 1
            except ValueError:
                pass
        yield author.name, f"{rem_count}個のコードを削除しました。"
    
    def add_code(self, args, author):
        for arg in args:
            self.codes.append(arg)
        yield author.name, f"{len(args)}個のコードを追加しました。"
    
    def start_game(self, args, author):
        self.phase = "game"
        ret_mes = "ゲームを開始します。参加者全員の個人チャットに他の人のタブーコードを送信しました\n" \
                 + "誰かがタブーコードを口走ったら、容赦なく" + COMMANDS["HIT"].get_command() \
                 + "するのです。\n" \
                 + "暗殺対象のIDがわからないときは" + COMMANDS["SHOW_PLAYERS"].get_command() \
                 + "で確認しましょう。\n" \
                 + "\n:spy: グッドラック！"
        yield "gamech", ret_mes

        for player in self.playermaster.players:
            randid = random.randrange(len(self.codes))
            player.set_code(self.codes[randid])
            # print cheat sheet
            print(f"{player.get_name()}: {self.codes[randid]}")
        for i, player in enumerate(self.playermaster.players):
            ret_mes = ":page_facing_up: 他のエージェントのタブーコードです。彼らが秘密を漏らさないか、注意深く監視してください。\n"
            other = self.playermaster.players[:]
            del other[i]
            ret_mes += "\n".join([
                f"{other[j].get_name()}: {other[j].get_code()}" for j in range(len(other))
            ])
            yield player.get_name(), ret_mes

    def hit(self, args, author):
        self.phase = "standby"
        for i, player in enumerate(self.playermaster.players):
            if i + 1 == int(args[0]):
                hitname = player.get_name()
        ret_mes = f":boom: バカめ！タブーを犯した{hitname}は処分されてしまった。\nゲーム終了、{hitname}の負け！\n"
        ret_comp = []
        for player in self.playermaster.players:
            ret_comp.append(f"{player.get_name()}: {player.get_code()}")
        ret_mes += "\n".join(ret_comp)
        yield "gamech", ret_mes

    def initialize(self):
        self.members = [member for member in self.get_all_members()]
        self.playermaster = PlayerMaster()

        self.allowed_commands_per_phase = {
            "standby": [
                COMMANDS["HELP"].get_command(),
                COMMANDS["JOIN"].get_command(),
                COMMANDS["LEAVE"].get_command(),
                COMMANDS["RESET"].get_command(),
                COMMANDS["SHOW_PLAYERS"].get_command(),
                COMMANDS["SET_CODES"].get_command(),
                COMMANDS["START"].get_command()
            ],
            "game": [
                COMMANDS["HELP"].get_command(),
                COMMANDS["SHOW_PLAYERS"].get_command(),
                COMMANDS["HIT"].get_command()
            ],
            "codes_edit": [
                COMMANDS["HELP"].get_command(),
                COMMANDS["SHOW_CODES"].get_command(),
                COMMANDS["REMOVE_CODE"].get_command(),
                COMMANDS["ADD_CODE"].get_command(),
                COMMANDS["SET_CODES"].get_command()
            ]
        }

        self.function_dictionary = {
            COMMANDS["HELP"].get_command(): self.help,
            COMMANDS["JOIN"].get_command(): self.join,
            COMMANDS["LEAVE"].get_command(): self.leave,
            COMMANDS["RESET"].get_command(): self.reset,
            COMMANDS["SHOW_PLAYERS"].get_command(): self.show_players,
            COMMANDS["SHOW_CODES"].get_command(): self.show_codes,
            COMMANDS["SET_CODES"].get_command(): self.set_codes,
            COMMANDS["REMOVE_CODE"].get_command(): self.remove_code,
            COMMANDS["ADD_CODE"].get_command(): self.add_code,
            COMMANDS["START"].get_command(): self.start_game,
            COMMANDS["HIT"].get_command(): self.hit
        }

        self.phase = "standby"
    
    def load_channel(self, id):
        self.gamech_id = id
    
    def load_codes(self, code_path):
        self.code_path = code_path

        self.codes = []
        with open(self.code_path, "r") as f:
            for line in f:
                self.codes.append(line.rstrip("\n"))