import random
import string
import requests
import threading
import os
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

print(
    Fore.MAGENTA
    + Style.BRIGHT
    + rf"""

                                           ╓╖,
               g▄▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▄╬╣╣╣╢╬N╖
              ▐▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╣╣╣╣╣╣╣╣╣╣╢╣╣@,
               ▀▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╣╣╣╣╣╣╣╢╢╣╣╣╣╣@,
                        ╙▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╣╣╣╣╣╣╢╣╣╣╣╣╣╣╣╣╣W
                        g▓▓▓▓▓▓╢▓▓▓▓╩╨╨╩╬╣╢╣╢╣▒╣╣╣╣╣╣╣╣╣╣╣╣
 Æ▓▓▓▓⌐   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╢▓▓╝⌠░░░░░░░░░░╙╨╣╣╣╣╣╣╣╣╣╣╣╣╣╣╣
 ╙▀▓▓▀    ╙▀▓▓▓▓▓▓▓▓▓▓▓▓▓▓╢▓▓╩░░░░░░░░░░░░░░░░╙╣╣╣╣╣╣╣╣╣╣╣╣╣@
                     ▓▓▓▓╢▓▓░░░░░╓╢▒▒▒▒▒▒╢░░░░░╙╣╣╣╣╣╣╣╣╣╣╣╣╢
               g▄▄▄▄▄▓▓▓▓▓▓Ñ░░░░║▒▒▒▒▒▒▒▒▒▒╖░░░░║╣╣╣╣╣╣╣╣╣╣╣╣⌐
              ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░║▒▒▒▒▒▒▒▒▒▒▒▒▒░░░]╣╣╣╣╣╣╣╣╣╣╣╣⌐
               ╙╙▐▓▓▓▓▓▓▓▓▓@░░░░╙▒▒▒▒▒▒▒▒▒▒╜░░░░║╣╣╣╣╣╣╣╣╣╣╣╣
                  ▓▓▓▓▓▓▓╣▓▓░░░░░╙▒▒▒▒▒▒▒▒░░░░░╓╣╣╣╣╣╣╣╣╣╣╣╣Ñ
                  ╚▓▓▓▓▓▓▓▓▓▓@░░░░░░░░░░░░░░░░░░░╢╣╣╣╣╣╣╣╣╣╣
                   ▐▓▓▓▓▓▓▓▓╢▓▓@µ░░░░░░░░░░╓@░░░░░░║╣╣╣╣╣╣╢\`
                    ╙▓▓▓▓▓▓▓▓▓▓╢▓▓▓▓@@@@▓▓▓▓╢▓▄░░░░░░░╜╨╣╢░
                      ▀▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▄░░░░░░░▒
                         ▀▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╜\"░▒░\"
                           ▀▀▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▀╩
                               ╙╙▀▀▀▓▓▓▓▀▀▀╙╙

"""
)

# Make sure the cache folder exists
if not os.path.exists("cache"):
    os.makedirs("cache")

# Open the file in the 'cache' folder
f = open("cache/valid_codes.txt", "w", encoding="utf-8")

CHOISE = input(Fore.YELLOW + "Do you want to use a webhook? (y/n): ").lower()

# Initialize WEBHOOK_URL based on user input
WEBHOOK_URL = None
if CHOISE == "y":
    WEBHOOK_URL = input(Fore.YELLOW + "Enter your Discord webhook URL: ")
elif CHOISE == "n":
    print(Fore.RED + "Webhook disabled. Codes will not be sent to a webhook.")

# Get the thread count from user input
THREAD_COUNT = input(
    Fore.YELLOW + "Enter the number of threads to run (default is 4): "
)
if THREAD_COUNT == "":
    THREAD_COUNT = 4
else:
    THREAD_COUNT = int(THREAD_COUNT)  # Convert to integer


# Function to send valid codes to the webhook
def send_to_webhook(valid_code):
    if WEBHOOK_URL:
        data = {
            "content": f"Valid Nitro Code: {valid_code}",
            "username": "Nitro Checker Bot",
        }
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(Fore.GREEN + f"Successfully sent to webhook: {valid_code}")
        else:
            print(Fore.RED + f"Failed to send to webhook: {valid_code}")
    else:
        print(Fore.RED + "Webhook is not enabled. Not sending the code.")


# Function to check codes continuously without breaks
def check_code():
    while True:  # Infinite loop to continuously generate and check codes
        y = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        full_url = f"https://discord.gift/{y}"

        url = f"https://discord.com/api/v9/entitlements/gift-codes/{y}?with_application=false&with_subscription_plan=true"
        r = requests.get(url)

        if r.status_code == 200:
            print(
                Fore.GREEN + f"VALID {full_url}\r", flush=True
            )  # Ensure the output is printed and flushed to the screen
            f.write(full_url + "\n")  # Write valid code to file in the cache folder
            send_to_webhook(full_url)
        else:
            print(
                Fore.RED + f"NOT VALID {full_url}\r", flush=True
            )  # Ensure the output is printed and flushed to the screen


# Create and start threads
threads = []
for _ in range(THREAD_COUNT):
    thread = threading.Thread(target=check_code)
    threads.append(thread)
    thread.daemon = True  # Ensure threads exit when the program ends
    thread.start()

# Allow the threads to run indefinitely
try:
    while True:
        pass
except KeyboardInterrupt:
    print(Fore.YELLOW + "\nExiting program...")
