from source.client import TCClient

tcclient = TCClient()

with open("./local_settings.txt", "r") as f:
    token = f.readline().rstrip("\n")
    channelID = int(f.readline())

tcclient.load_channel(channelID)
tcclient.load_codes("./codes.txt")
tcclient.run(token)