import socket
import subprocess
import time
import re
from pyngrok import ngrok, conf
import discord
from discord.ext import commands

# ---------- CONFIG ----------
COMPUTOR = 'RaspberryPi5'
COM_USER = 'pi'
JUPYTER_PORT = "4445"
CHANNEL_NAME = "logservers"

DISCORD_TOKEN = "MTM2MDAzNDI3MDU0NjIzMTQ3Nw.GYG2cv.8l0BpIrWgItV7YS_YIQkERkebqW89dvP6tdxbQ"
NGROK_CONFIG_PATH = f"/home/{COM_USER}/.config/ngrok/ngrok.yml"
WORKING_DIR = f"/home/{COM_USER}/Documents"
# ----------------------------

# Discord Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Send message to Discord log channel
async def bot_send_discord_message(content):
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel:
            await channel.send(content)

# Get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "0.0.0.0"

# Get AnyDesk ID
def get_anydesk_id():
    try:
        result = subprocess.run(['anydesk', '--get-id'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except FileNotFoundError:
        return "AnyDesk not found. Make sure it's installed and added to PATH."

# Start Jupyter Notebook and extract token
def start_jupyter_ngrok(local_ip):
    pyngrok_config = conf.PyngrokConfig(config_path=NGROK_CONFIG_PATH)
    tunnel = ngrok.connect(JUPYTER_PORT, pyngrok_config=pyngrok_config)
    public_url = str(tunnel.public_url)

    time.sleep(10)

    jupyter_process = subprocess.Popen(
        [
            "jupyter", "notebook",
            "--ip=0.0.0.0",
            f"--port={JUPYTER_PORT}",
            "--no-browser"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=WORKING_DIR,
        text=True
    )

    time.sleep(3)

    token = None
    for _ in range(20):
        line = jupyter_process.stdout.readline()
        print(line.strip())
        match = re.search(r'token=([a-f0-9]+)', line)
        if match:
            token = match.group(1)
            break

    if token:
        full_url = f"{public_url}/?token={token}"
        full_url2 = f"http://{local_ip}:{JUPYTER_PORT}/?token={token}"
        return full_url, full_url2
    else:
        print("⚠️ Failed to extract token from Jupyter output.")
        return None, None

# Main process
async def run_main_program():
    time.sleep(10)
    print("✅ Start main program")

    local_ip = get_local_ip()
    anydesk_id = get_anydesk_id()
    jupyter_ngrok_url, jupyter_ngrok_url2 = start_jupyter_ngrok(local_ip)

    msg = (
        f"{COMPUTOR} {'-'*25}\n"
        f"ssh -p 32097 {COM_USER}@serveo.net \n"
        f"Anydesk : {anydesk_id}\n"
        f"notebook : \n{jupyter_ngrok_url}\n{jupyter_ngrok_url2}"
        f"\n***change dir jupyter edit in >> sudo nano {WORKING_DIR}/Connection-Config-All/main.py"
    )

    print(msg)
    await bot_send_discord_message(msg)

    # Keep-alive loop
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down ngrok tunnel...")
        ngrok.kill()

# When bot is ready, start the main program
@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} is ready.")
    bot.loop.create_task(run_main_program())

# Run the bot
bot.run(DISCORD_TOKEN)
