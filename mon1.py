import subprocess, sys, threading, queue, colorama, os, wave, contextlib, time, json, datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from scipy.fft import *
from scipy.io import wavfile
import numpy
assert numpy
# PyDEC Alert Recorder, Written by Aaron s#8638 :3


with open("config.json", "r") as jfile:
    config_file = jfile.read()
    jfile.close()

config_data = json.loads(config_file)

disclogenable = config_data['enable_discord_logger']
webhook_links = config_data['logger_webhook']
webhook_username = config_data['webhook_username']
embed_author = config_data['embed_author']
embed_author_link = config_data['embed_author_link']
embed_color = config_data['logger_color']






def setup():
    global platform
    if sys.platform == "win32":
        platform = "win"
        print("\n[Setup]  Windows Color Mode...")
        colorama.init(convert=True)
    else:
        platform = "other"

    print("[Setup]  Using Default Audio Input...")
    print("[Setup]  Cleaning Up Old Files...")
    files = os.listdir('monitor_1/tmp')
    files_to_del = ["out.wav", "rmend0.wav", "alert.wav"]
    for name in files:
        if name in files_to_del:
            dirr = "monitor_1/tmp/" + name
            os.remove(dirr)


def ready_stat():
    with open("com/working.var") as w:
        stat = w.read()
        w.close()

    if stat == "True":
        return True
    else:
        return False


def writefile(loc, lestr):
    with open(loc, "w") as f:
        f.write(str(lestr))
        f.close()




def rm_end():
    audio = AudioSegment.from_file("monitor_1/tmp/out.wav")
    lengthaudio = len(audio)
    start = 0
    threshold = lengthaudio - 1200
    end = 0
    counter = 0
    end += threshold
    chunk = audio[start:end]
    filename = f'monitor_1/tmp/rmend{counter}.wav'
    chunk.export(filename, format="wav")
    counter +=1
    start += threshold
    print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Removed Recording EOMs")
    

def clr_dir():
    files = os.listdir('monitor_1/tmp')
    for name in files:
        if name != "alert.wav": #Make sure to not delete the output
            dirr = "monitor_1/tmp/" + name
            os.remove(dirr)
    print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Cleaned Up tmp Directory")


def get_len():
    fname = 'monitor_1/tmp/rmend0.wav'
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def freq(file, start_time, end_time):

    sr, data = wavfile.read(file)
    if data.ndim > 1:
        data = data[:, 0]
    else:
        pass

    dataToRead = data[int(start_time * sr / 1000) : int(end_time * sr / 1000) + 1]

    N = len(dataToRead)
    yf = rfft(dataToRead)
    xf = rfftfreq(N, 1 / sr)


    # Get the most dominant frequency and return it
    idx = numpy.argmax(numpy.abs(yf))
    freq = xf[idx]
    return freq


def rm_attn_tone():

    # print("\nGetting attn tone point...")
    timelist = []
    freqlist = []
    ATTNCUT = 0
    file_length = get_len()
    if file_length < 23:
        file_length = round(file_length)
        # print(file_length)
        # print("Using Whole File...")
    else:
        file_length = 80
        # print("Using 25 Sec...")


    cnt = 0

    for e in range(file_length):
        cnt = cnt + 1
        val = 300
        start = e * val
        offset = start + val
        timelist.append(start)
        frequency = freq('monitor_1/tmp/rmend0.wav', start, offset)
        freqlist.append(frequency)





    freqlist = list(freqlist)
    mainlen = len(freqlist)


    found = False
    for e in range(len(freqlist)):
        if found == False:
            if 810 < round(int(freqlist[e])) < 1070:
                if 810 < round(int(freqlist[e + 1])) < 1070 and 810 < round(int(freqlist[e + 2])) < 1070:
                    found = True
        elif found == True:
            if freqlist[e] < 810 or freqlist[e] > 1070:
                if e + 5 < mainlen:
                    if freqlist[e + 1] < 810 or freqlist[e + 1] > 1070 and freqlist[e + 2] < 810 or freqlist[e + 2] > 1070 and freqlist[e + 3] < 810 or freqlist[e + 3] > 1070 and freqlist[e + 4] < 810 or freqlist[e + 4] > 1070 and freqlist[e + 5] < 810 or freqlist[e + 5] > 1070:
                        end_point = e
                        found = None
    
    if(found == None):
        # print("Cutting Audio...")
        audio = AudioSegment.from_file('monitor_1/tmp/rmend0.wav')
        lengthaudio = len(audio)
        cut = 300 * end_point
        start = cut
        threshold = lengthaudio - cut
        end = lengthaudio
        counter = 0
        while start < len(audio):
            end += threshold
            chunk = audio[start:end]
            filename = f'monitor_1/tmp/alert.wav'
            chunk.export(filename, format="wav")
            counter +=1
            start += threshold
    else:
        gl = round(get_len())
        if(gl > 4):
            end_point = 17 #5 seconds
        else:
            end_point = gl // 2

        # print("Cutting Audio...")
        audio = AudioSegment.from_file('monitor_1/tmp/rmend0.wav')
        lengthaudio = len(audio)
        cut = 300 * end_point
        start = cut
        threshold = lengthaudio - cut
        end = lengthaudio
        counter = 0
        while start < len(audio):
            end += threshold
            chunk = audio[start:end]
            filename = f'monitor_1/tmp/alert.wav'
            chunk.export(filename, format="wav")
            counter +=1
            start += threshold
    
    print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Removed ATTN Tone")


def ZCZC_test(inp):
    inp = inp.split("-")

    num = len(inp) - 6

    if len(inp[num + 3]) != 7:
        return False
    elif len(inp[num + 4]) != 8:
        return False
    elif len(inp[0]) != 4: #ZCZC
        return False
    elif len(inp[1]) != 3: #"EAS"
        return False
    elif len(inp[2]) != 3: #"DMO"
        return False



    if num == 1 and len(inp[3]) == 11:
        return True
    elif num > 1:
        for e in range(num):
            if (e + 1) == num:
                if len(inp[e+3]) == 11:
                    return True
                else:
                    return False
            elif len(inp[e+3]) != 6:
                return False
    else:
        return False



def gen_receipt():
    dtnow = datetime.datetime.now()

    tds = f"{dtnow.strftime(f'%I')}:{dtnow.strftime(f'%M')}:{dtnow.strftime(f'%S')} {dtnow.strftime(f'%p')}"

    receipt = f"Received at {tds} on {dtnow.strftime(f'%A')} {dtnow.strftime(f'%B')} {dtnow.strftime(f'%d')} {dtnow.strftime(f'%Y')}"

    return receipt


def discordlog(ZCZC):
    webhook = DiscordWebhook(url=webhook_links, username=webhook_username)

    embed = DiscordEmbed(title="Emergency Alert Received", color=embed_color)

    with open("discord_bin/clock.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='clock.png')
        f.close()

    embed.set_thumbnail(url='attachment://clock.png')
    embed.set_author(name=embed_author, url=embed_author_link)

    embedreceipt = f"```{gen_receipt()}```"
    ZCZC = f"```{ZCZC}```"

    embed.add_embed_field(name="Receipt:", value=embedreceipt,inline=False)
    embed.add_embed_field(name="ZCZC Data:", value=ZCZC,inline=False)
    embed.set_footer(text='PyDEC')
    embed.set_timestamp()
    
    webhook.add_embed(embed)
    webhook.execute()




def record():
    while True:

        sd.default.reset()
        samplerate = 11025
        file = "monitor_1/tmp/out.wav"
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        with sf.SoundFile(file, mode='x', samplerate=samplerate,channels=2) as file:
            with sd.InputStream(samplerate=samplerate,channels=2,callback=callback):
                print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Recording!")
                while True:
                    file.write(q.get())
                    global stop_threads
                    if stop_threads:
                        exit()

# Main code
if __name__ == "__main__":

    platform = None
    last = None
    setup()



    if platform == "win":
        source_process = subprocess.Popen(["monitor_1/multimon-ng-WIN32/multimon-ng.exe", "-a", "EAS"], stdout=subprocess.PIPE)
    else:
        source_process = subprocess.Popen(["multimon-ng", "-a", "EAS"], stdout=subprocess.PIPE)

    print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.GREEN}  Ready For Alerts...\n{colorama.Fore.BLACK}")

    while True:
        line = source_process.stdout.readline().decode("utf-8")
        decode = line.replace("b'EAS: ", "").replace("\n'", "").replace("'bEnabled Demodulators: EAS", "").replace('EAS:  ', '').replace('EAS: ', '').replace('Enabled demodulators: EAS', '')

        if "ZCZC-" in decode or "NNNN" in decode:
            print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Decoder: {decode}")

        if 'ZCZC-' in str(line):
            if ZCZC_test(decode) == True:
                ZCZCheader = decode
                print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  ZCZC Check OK")


                if(disclogenable):
                    discordlog(decode) #Log to discord
                
                stop_threads = False
                t1 = threading.Thread(target = record)
                t1.start()
            else:
                print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.RED}  WARNING: ZCZC Check FAILED!")
                line = "NNNN"
        elif 'NNNN' not in str(last):
            if 'NNNN' in str(line):
                stop_threads = True
                t1.join()

                print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTBLACK_EX}  Stopped Recording Thread")

                rm_end()
                rm_attn_tone()
                clr_dir()


                writefile("com/alert_des.var", "N/A") #Alert Description
                writefile("com/message_loc.var", "monitor_1/tmp/alert.wav") #Alert audio message location
                writefile("com/alert_ZCZC.var", ZCZCheader) #Alert ZCZC str

                if ready_stat() == True: #If processing alert
                    print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.LIGHTRED_EX}  WARNING: PyDEC is processing an alert! Waiting...")
                    pydec_ready = False
                    while pydec_ready == False:
                        time.sleep(2)
                        if ready_stat() == False:
                            pydec_ready = True
                            print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.GREEN}  Sending...")

                writefile("com/alertready.var", "True")

                print(f"{colorama.Fore.BLUE}[Monitor]{colorama.Fore.GREEN}  Alert Sent!\n\n")

        last = line