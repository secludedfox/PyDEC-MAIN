import time, sys, colorama, shutil, json, threading, datetime, smtplib
from EASGen import EASGen
from EAS2Text import EAS2Text
from discord_webhook import DiscordWebhook, DiscordEmbed
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# PyDEC Written by Aaron s#8638 :3

def gen_headers(ZCZC):
    headers = EASGen.genEAS(header=ZCZC, attentionTone=True, endOfMessage=False, sampleRate=48000)
    headers.export("audio/audio/encode.wav", format="wav")


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


def discordlog(dis_ZCZC, alert_des):
    alrdat = EAS2Text(sameData=dis_ZCZC, timeZone=timezone_offset)


    if alrdat.evnt in IconDict:
        alerticon = IconDict[alrdat.evnt][0]
    else:
        alerticon = "https://cdn.discordapp.com/attachments/907457287864590396/907757517751332914/warning.png"


    if alrdat.evnt in colEvtlist:
        if colEvtlist[alrdat.evnt][0] == 0:
            embed_color = "F9F734"
        elif colEvtlist[alrdat.evnt][0] == 1:
            embed_color = "FF930E"
        elif colEvtlist[alrdat.evnt][0] == 2:
            embed_color = "FF1F1F"
        elif colEvtlist[alrdat.evnt][0] == 3:
            embed_color = "10FF35"
    else:
        embed_color = "F9F734"



    alertmessage = f"```{alrdat.EASText}```"
    dis_ZCZC = f"```{dis_ZCZC}```"

    webhook = DiscordWebhook(url=webhook_links, username=webhook_username)

    embed = DiscordEmbed(title="Emergency Alert Forwarded", description=alertmessage, color=embed_color)
    embed.set_thumbnail(url=alerticon)
    embed.set_author(name=embed_author, url=embed_author_link)
    embed.set_image()


    if alert_des != "N/A":
        alert_des = f"```{alert_des}```"
        embed.add_embed_field(name="Alert Description", value=alert_des,inline=False)


    embed.add_embed_field(name="ZCZC Data:", value=dis_ZCZC,inline=False)



    embed.set_footer(text='PyDEC')
    embed.set_timestamp()


    webhook.add_embed(embed)
    webhook.execute()


def sendalertemail(easzczc:str):
    alrdat = EAS2Text(sameData=easzczc, timeZone=timezone_offset)


    x = datetime.datetime.now()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"PyDEC: Alert Forwarded At {x.strftime('%X')}"
    msg['From'] = gmail_user

    if(type(sendto) == list):
        msg['To'] = ",".join(sendto)
    else:
        msg['To'] = sendto


    text = f"An Emergency Alert was forwarded at {x.strftime('%c')}\n{alrdat.EASText}\n{easzczc}"
    html = f"""\
    <html>
      <head></head>
      <body style="height: 100%; margin: 0; padding: 0; width: 100%; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; background-color: #474747;font-family: Arial, Helvetica, sans-serif;">
        <h2 style="color: rgb(255, 0, 0);margin: 5px; margin-top:20px;">{staion} PyDEC Alert Logs</h2>
        <hr>
        <h3 style="margin: 10px; color: white;">An Emergency Alert was forwarded at {x.strftime('%c')}</h3>
        <div style="margin: 10px; margin-top: 20px; padding: 4px; border: 3px solid #ff0000; border-radius: 10px; background-color: #3d3d3d; max-width: 800px; color: white;">
            <h4>{alrdat.EASText}</h4>
            <h4>{easzczc}</h4>
        </div>
        <hr>
        <p style="color: rgb(255,0,0); margin: 10px; font-size: 12px; margin-bottom: 10px;">PyDEC EAS ENDEC</p>
    </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # RFC 2046, the last part of a multipart message is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    mail = smtplib.SMTP(emailserver, emailserverport)
    mail.ehlo()
    mail.starttls()
    mail.login(gmail_user, gmail_password)
    mail.sendmail(gmail_user, sendto, msg.as_string())
    mail.quit()
    print(f"{colorama.Fore.BLUE}\n[PyDEC]{colorama.Fore.LIGHTBLACK_EX}  Email Log Sent")


def addalertlst(ZCZC):
    ZCZC = ZCZC.split("-")
    ZCZC.pop(len(ZCZC) - 1)
    ZCZC.pop(len(ZCZC) - 1)
    ZCZC = '-'.join(ZCZC)
    if(len(alrlist) > 50):
        alrlist.pop(0)
        alrlist.append(ZCZC)
    else:
        alrlist.append(ZCZC)


def dupealrcheck(ZCZC):
    ZCZC = ZCZC.split("-")
    ZCZC.pop(len(ZCZC) - 1)
    ZCZC.pop(len(ZCZC) - 1)
    ZCZC = '-'.join(ZCZC)
    if(ZCZC in alrlist):
        return True
    else:
        return False


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
        colorama.init(convert=True)
        print("\n[Setup]  Windows Color Mode...")

    writefile("com/alertready.var", "False")
    writefile("com/working.var", "False")



if __name__ == "__main__":
    setup()

    colEvtlist = {
        "ADR" : [0],
        "AVA" : [1],
        "AVW" : [2],
        "BLU" : [0],
        "BZW" : [2],
        "CAE" : [0],
        "CDW" : [2],
        "CEM" : [0],
        "CFA" : [1],
        "CFW" : [2],
        "DMO" : [3],
        "DSW" : [2],
        "EAN" : [0],
        "EAT" : [0],
        "EQW" : [2],
        "EVI" : [2],
        "EWW" : [2],
        "FFA" : [1],
        "FFS" : [0],
        "FFW" : [2],
        "FLA" : [1],
        "FLS" : [0],
        "FLW" : [2],
        "FRW" : [2],
        "FSW" : [2],
        "FZW" : [2],
        "HLS" : [0],
        "HMW" : [0],
        "HUA" : [1],
        "HUW" : [2],
        "HWA" : [1],
        "HWW" : [2],
        "LAE" : [0],
        "LEW" : [0],
        "NAT" : [0],
        "NIC" : [0],
        "NMN" : [0],
        "NPT" : [0],
        "NST" : [0],
        "NUW" : [0],
        "RHW" : [2],
        "RMT" : [3],
        "RWT" : [3],
        "SMW" : [2],
        "SPS" : [0],
        "SPW" : [0],
        "SQW" : [2],
        "SSA" : [1],
        "SSW" : [2],
        "SVA" : [1],
        "SVR" : [2],
        "SVS" : [0],
        "TOA" : [1],
        "TOE" : [0],
        "TOR" : [2],
        "TRA" : [1],
        "TRW" : [2],
        "TSA" : [1],
        "TSW" : [2],
        "VOW" : [2],
        "WSA" : [1],
        "WSW" : [2],
    }

    IconDict = {}
    alrlist = []

    with open('discord_bin/Icontable.var') as fp:
       line = fp.readline()
       cnt = 1
       while line:
           line = line.replace('\n', '')
           IconSPLIT = line.split(",")
           IconDict[ IconSPLIT[0] ] = [ IconSPLIT[1]]


           line = fp.readline()
           cnt += 1


    with open("config.json", "r") as jfile:
        config_file = jfile.read()
        jfile.close()

    config_data = json.loads(config_file)

    staion = str(config_data['callsign'])

    disclogenable = config_data['enable_discord_logger']
    webhook_links = config_data['logger_webhook']
    webhook_username = config_data['webhook_username']
    embed_author = config_data['embed_author']
    embed_author_link = config_data['embed_author_link']
    timezone_offset = int(config_data['timezone_offset'])

    emaillogenable = config_data['enable_email_logger']
    emailserver = config_data['email_server']
    emailserverport = config_data['email_server_port']
    gmail_user = config_data['email_user']
    gmail_password = config_data['email_user_pass']
    sendto = config_data['email_sendto']



    print("\n[Setup]  Loaded Config")
    print(f"{colorama.Fore.BLUE}\n[PyDEC]{colorama.Fore.GREEN}  Waiting For Alerts..." )

    while True:
        time.sleep(3)
        if readfile("com/alertready.var") == "True": #If there is an alert 
            writefile("com/working.var", "True") #Tell plugins to not send any alerts
            alert_description = readfile("com/alert_des.var")
            alert_ZCZC = readfile("com/alert_ZCZC.var")
            message_location = readfile("com/message_loc.var")

            if(dupealrcheck(alert_ZCZC)):
                print(f"{colorama.Fore.BLUE}[PyDEC]{colorama.Fore.LIGHTRED_EX}  Duplicate Alert:{colorama.Fore.LIGHTBLACK_EX} {alert_ZCZC}")
            else:
                addalertlst(alert_ZCZC)
                if readfile("audio/var/working.var") == "False":
                    print(f"{colorama.Fore.BLUE}\n[PyDEC]{colorama.Fore.LIGHTBLACK_EX}  New Alert: {alert_ZCZC}")

                    alert_ZCZC = recompile_ZCZC(staion, alert_ZCZC)

                    if(disclogenable):
                        discordlog(alert_ZCZC,alert_description) #log to discord

                    if(emaillogenable):
                        ethread = threading.Thread(target = sendalertemail, args=(alert_ZCZC,)) #Log to email (async)
                        ethread.start()

                    gen_headers(alert_ZCZC)

                    shutil.copyfile(message_location, "audio/audio/alert.wav")

                    writefile("audio/var/new_audio.var", "True")
                elif readfile("audio/var/working.var") == "True":
                    print(f"{colorama.Fore.BLUE}\n[PyDEC]{colorama.Fore.LIGHTBLACK_EX}  New Alert: {alert_ZCZC}")

                    print(f"{colorama.Fore.BLUE}[PyDEC]{colorama.Fore.LIGHTRED_EX}  Overriding Alert!")

                    alert_ZCZC = recompile_ZCZC(staion, alert_ZCZC)

                    if(disclogenable):
                        discordlog(alert_ZCZC,alert_description) #log to discord

                    if(emaillogenable):
                        ethread = threading.Thread(target = sendalertemail, args=[alert_ZCZC]) #Log to email (async)
                        ethread.start()

                    gen_headers(alert_ZCZC)

                    shutil.copyfile(message_location, "audio/audio/alert.wav")

                    writefile("audio/var/over_ride.var", "True")
            writefile("com/alertready.var", "False")
            writefile("com/working.var", "False")


