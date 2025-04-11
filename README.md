# Install
## Prepare
### Config Serveo
nano ~/.ssh/config >> add
```
Host serveo.net
    User serveo
    StrictHostKeyChecking no
```
```
# For test
@pi >> ssh -N -R 32097:localhost:22 serveo.net
@from remote >> ssh -p 32097 pi@serveo.net
```
### Set up Anydesk
- Open AnyDesk on your Raspberry Pi
- Go to Settings > Security > three-line menu (≡) or the gear icon. > Settings > Security
- Enable “Allow always” or “Unattended Access”
- Set a strong password in the "Set Password for Unattended Access" section.

### Install ngrok >> install and add token from step in website 
https://dashboard.ngrok.com/signup

### Setup Discord Bot
https://discord.com/developers/applications/1360034270546231477/bot

## Download github and Install virtualenv
```
cd Documents 
git clone ....
cd Connection-Config-All

sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate

pip install -r requirements.txt
```

### Edit in main.py and in crontab -e
```
COMPUTOR = 'RasberryPi5'
COM_USER = 'pi'
SERVEO_PORT = XXXXX
DISCORD_TOKEN = XXXX  # copy token from >> https://discord.com/developers/applications/1360034270546231477/bot
```
Edit Port Servo in crontab same as main.py
crontab -e
```
SHELL=/bin/sh
HOME=/home/pi/Documents/Connection-Config-All
@reboot sleep 15 && ssh -N -R 32097:localhost:22 serveo.net >> /home/pi/serveo.log 2>&1 &
@reboot sleep 30 && /home/pi/Documents/Connection-Config-All/run_all.sh >> /home/pi/cron_reboot_log2.txt 2>&1
```

### Only on Raspberry pi
#### Setup ssh
- sudo raspi-config
- Go to the Interfaces tab.
- Find SSH and select Enable.
- Click OK, then reboot (optional).

#### Switching from Wayland to Xorg (X11)
- sudo raspi-config > Advanced Options > Wayland > Select "X11" to switch from Wayland to the X11 window system.
- sudo reboot



### Setup Discord API
- Right Click > Inspace > Network > Fetch/XHR
- Request URL, authorization



