import time, sys, colorama, shutil, json
from EASGen import EASGen



def gen_headers(ZCZC):
    headers = EASGen.genEAS(header=ZCZC, attentionTone=True, endOfMessage=False, sampleRate=48000)
    headers.export("Audio/audio/encode.wav", format="wav")


def recompile_ZCZC(station, ZCZC):
    if len(station) > 8:
        station = "PYDECEAS"
        print("WARNING: Call sign too long! Setting to default...")
    elif len(station) < 8:
        station = "PYDECEAS"
        print("WARNING: Call sign too short! Setting to default...")
    elif "-" in station:
        station = "PYDECEAS"
        print("WARNING: Call sign contains invalid symbol! Setting to default...")

    ZCZC = ZCZC.split("-")
    ZCZClen = len(ZCZC) - 2
    ZCZC[ZCZClen] = station
    ZCZC = '-'.join(ZCZC)
    return ZCZC


def readfile(loc):
    with open(loc, "r") as f:
        fil = str(f.read())
        f.close()
    return fil


def writefile(loc, le_str):
    with open(loc, "w") as f:
        f.write(str(le_str))
        f.close()


def setup():
    if sys.platform == "win32":
        print("\n[Setup]  Windows Color Mode...")
        colorama.init(convert=True)
    writefile("com/alertready.var", "False")
    writefile("com/working.var", "False")


setup()

with open("config.json", "r") as jfile:
    config_file = jfile.read()
    jfile.close()

config_data = json.loads(config_file)

staion = str(config_data['callsign'])




while True:
    time.sleep(3)
    if readfile("com/alertready.var") == "True": #If there is an alert 
        writefile("com/working.var", "True") #Tell plugins to not send any alerts
        alert_description = readfile("com/alert_des.var")
        alert_ZCZC = readfile("com/alert_ZCZC.var")
        message_location = readfile("com/message_loc.var")

        if readfile("Audio/var/working.var") == "False":
            alert_ZCZC = recompile_ZCZC(staion, alert_ZCZC)
            gen_headers(alert_ZCZC)
            shutil.copyfile(message_location, "Audio/audio/alert.wav")
            writefile("Audio/var/new_audio.var", "True")
        elif readfile("Audio/var/working.var") == "True":
            alert_ZCZC = recompile_ZCZC(staion, alert_ZCZC)
            gen_headers(alert_ZCZC)
            shutil.copyfile(message_location, "Audio/audio/alert.wav")
            writefile("Audio/var/over_ride.var", "True")



        writefile("com/alertready.var", "False")
        writefile("com/working.var", "False")


