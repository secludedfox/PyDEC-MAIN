import sounddevice as sd
import soundfile as sf
import datetime, time, threading, colorama, sys, os
# PyDEC Audio Handler, Written by Aaron s#8638 :3


def setup():
    global dev

    if sys.platform == "win32":
        colorama.init(convert=True)
        print("\n[Setup]  Windows Color Mode...")


    with open("var/over_ride.var", "r+") as of:
        of.truncate(0)
        of.close()

    with open("var/new_audio.var", "r+") as na:
        na.truncate(0)
        na.close()

    print("\n[Setup]  Cleared Files...\n\n")
    print(colorama.Fore.CYAN)


    device_list_name = []

    for e in range(len(sd.query_devices())):
        if sd.query_devices(device=e) not in device_list_name:
            device_list_name.append(sd.query_devices(device=e))

    for e in range(len(device_list_name)):
        print(str(e) + " - " + device_list_name[e]["name"])

    print("\n\n------------------------------------------------------------\nWhich Device (Number) do you want to use for audio Output?")

    user_input_good = False
    while user_input_good == False:

        user_input = input(">")
        try:
            user_input = int(user_input)
            if user_input < len(device_list_name):
                user_input_good = True
        except:
            user_input_good = False


    output_device = device_list_name[user_input]["name"]
    dev = output_device
    print(colorama.Fore.BLUE + "\n[Audio]" + colorama.Fore.GREEN + "  Audio Output Device Set To: " + output_device)



    



def play_all():
    global play_done
    device = dev
    np_message = colorama.Fore.BLUE + "[Audio]" + colorama.Fore.LIGHTBLACK_EX + "  Playing: "

    # If there is a pre-alert sound
    if over_ride == False:
        if or_go == False: #Don't play when overriding audio
            if os.path.exists("audio/pre.wav"):
                file = "audio/pre.wav"
                data, fs = sf.read(file, dtype='float32')
                dur = round(int(sf.info(file).duration))
                sd.default.reset()
                sd.default.device = device
                print(np_message + "PreAlert Audio")
                sd.play(data, fs)
                sd.wait()
            




    # Play headers
    if over_ride == False:
        file = "audio/encode.wav"
        data, fs = sf.read(file, dtype='float32')
        dur = round(int(sf.info(file).duration))
        sd.default.reset()
        sd.default.device = device
        print(np_message + "ZCZC + EBS")
        sd.play(data, fs)

        d = datetime.datetime.now()
        s = datetime.timedelta(seconds=dur)
        nt = d + s
        while nt > datetime.datetime.now():
            time.sleep(1)
            if over_ride == True:
                sd.stop()
                break
    
    # Play Alert Audio
    if over_ride == False:
        file = "audio/alert.wav"
        data, fs = sf.read(file, dtype='float32')
        dur = round(int(sf.info(file).duration))
        sd.default.reset()
        sd.default.device = device
        print(np_message + "Alert Audio/Message")
        sd.play(data, fs)

        d = datetime.datetime.now()
        s = datetime.timedelta(seconds=dur)
        nt = d + s
        while nt > datetime.datetime.now():
            time.sleep(1)
            if over_ride == True:
                sd.stop()
                break
    
    # Play EOMs
    if over_ride == False:
        file = "audio/eom.wav"
        data, fs = sf.read(file, dtype='float32')
        dur = round(int(sf.info(file).duration))
        sd.default.reset()
        sd.default.device = device
        print(np_message + "EOMs")
        sd.play(data, fs)

        d = datetime.datetime.now()
        s = datetime.timedelta(seconds=dur)
        nt = d + s
        while nt > datetime.datetime.now():
            time.sleep(1)
            if over_ride == True:
                sd.stop()
                break

    if over_ride == False:
        print(colorama.Fore.BLUE + "[Audio]" + colorama.Fore.GREEN + "  Finished Playing Alert\n")
        play_done = True
        with open("var/working.var", "w") as wo:
            wo.write("False")
            wo.close()



def eom_it():
    device = dev
    np_message = colorama.Fore.BLUE + "[Audio]" + colorama.Fore.LIGHTBLACK_EX + "  Playing: "
    
    # Play EOMs
    file = "audio/eom.wav"
    data, fs = sf.read(file, dtype='float32')
    dur = round(int(sf.info(file).duration))
    sd.default.reset()
    sd.default.device = device
    print(np_message + "EOMs")
    sd.play(data, fs)
    sd.wait()



if __name__ == "__main__":
    setup()
    or_go = False
    print(colorama.Fore.BLUE + "[Audio]" + colorama.Fore.GREEN + "  Waiting For Alerts...\n")


    while True:
        time.sleep(2)

        with open("var/new_audio.var", "r") as na:
            na_stat = na.read()
            na.close()

        if na_stat == "True" or or_go == True:   # If New audio is available

            with open("var/new_audio.var", "r+") as na:
                na.truncate(0)
                na.close()

            with open("var/working.var", "w") as wo:
                wo.write("True")
                wo.close()

            or_go == False
            over_ride = False
            play_done = False
            t1 = threading.Thread(target = play_all)
            t1.start()

            while play_done == False:
                time.sleep(1)
                or_go = False
                with open("var/over_ride.var", "r") as of:
                    of_stat = of.read()
                    of.close()

                if of_stat == "True":
                    print(colorama.Fore.BLUE + "[Audio]" + colorama.Fore.LIGHTRED_EX + "  Overriding Alert!")
                    over_ride = True
                    t1.join()
                    with open("var/over_ride.var", "r+") as of:
                        of.truncate(0)
                        of.close()

                    eom_it()

                    or_go = True
                    play_done = True
                    break

            t1.join()