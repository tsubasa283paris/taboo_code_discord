from source.client import TCClient

tcclient = TCClient()

with open("./local_settings.txt", "r") as f:
    token = f.readline()
    channelID = int(f.readline())

codes = []
with open("./codes.txt", "r") as f:
    for line in f:
        codes.append(line)

tcclient.load_channel(channelID)
tcclient.load_codes(codes)
tcclient.run(token)