import socket
import subprocess
import requests
import subprocess
import time
import re
from pyngrok import ngrok, conf

COMPUTOR = 'RasberryPi5'
COM_USER = 'pi'

def start_jupyter_ngrok(local_ip):

    PORT = "4445"

    # Set the directory where Jupyter should run
    working_dir = f"/home/{COM_USER}/Documents"
    # working_dir = "/mnt/mydisk" 

    pyngrok_config = conf.PyngrokConfig(
        config_path=f"/home/{COM_USER}/.config/ngrok/ngrok.yml"
    )

    # Start ngrok tunnel to port 7779
    tunnel = ngrok.connect(PORT, pyngrok_config=pyngrok_config)
    public_url = str(tunnel.public_url)

    print('public_url',public_url)

    time.sleep(10)

    # Start Jupyter Notebook server in the desired directory
    jupyter_process = subprocess.Popen(
        [
            "jupyter", "notebook",
            "--ip=0.0.0.0",
            f"--port={PORT}",
            "--no-browser"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=working_dir,  # <- Set working directory here
        text=True
    )

    time.sleep(3)

    # Extract token from Jupyter output
    token = None
    for _ in range(20):  # Loop through early lines for the token
        line = jupyter_process.stdout.readline()
        print(line.strip())  # Optional: log for debugging
        match = re.search(r'token=([a-f0-9]+)', line)
        if match:
            token = match.group(1)
            break

    # Build full URL
    if token:
        full_url = f"{public_url}/?token={token}"
        full_url2 = f"http://{local_ip}:{PORT}/?token={token}"
        print("\n✅ Access your Jupyter Notebook here:")
        print(f"🔗 {full_url}")

        return full_url,full_url2
    else:
        print("⚠️ Failed to extract token from Jupyter output.")
        return None,None

def sent_discord(msg):
    url = "https://discord.com/api/v9/channels/1359119036423868629/messages"
    payload = {
        "content": msg
    }
    headers = {
        "Authorization": "MTAyNDEzMjg5MDcwOTIwNTA0Mg.GJzX1W.0jnSTAVK6VnYe67oleOHrnN86RN_1Ks6PZha1E",  # or just the token if it's a user token (not recommended)
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response:", response.json())

def get_anydesk_id():
    try:
        result = subprocess.run(['anydesk', '--get-id'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except FileNotFoundError:
        return "AnyDesk not found. Make sure it's installed and added to PATH."

def get_local_ip():
    try:
        # Connect to a public server but never send data
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Google's DNS
        ip = s.getsockname()[0]
        s.close()

        return ip
        # print(f"Local IP: {ip}")
    except Exception as e:
        print(f"Error: {e}")

time.sleep(10)

print('start!'*10)

local_ip = get_local_ip()
anydesk_id = get_anydesk_id()
jupyter_ngrok_url,jupyter_ngrok_url2 = start_jupyter_ngrok(local_ip)


msg = f"{COMPUTOR} {'-'*25}\nssh -p 32097 {COM_USER}@serveo.net \nAnydesk : {anydesk_id}\nnotebook : \n{jupyter_ngrok_url}\n{jupyter_ngrok_url2}"
msg += f"\n***change dir jupyter edit in >> sudo nano /home/{COM_USER}/Documents/Connection-Config-All/main.py" 

print(msg)
sent_discord(msg)

# Keep alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Shutting down ngrok tunnel...")
    ngrok.kill()
