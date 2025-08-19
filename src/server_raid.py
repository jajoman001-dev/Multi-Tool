try:
    from colorama import init, Fore
    import requests
    import datetime
    import threading
    import random
except Exception as e:
    print(f"Required modules not installed: {e}")
    exit(1)

init(autoreset=True)

# Color constants
color = Fore
red = color.RED
white = color.WHITE
green = color.GREEN

reset = color.RESET

# Status prefix constants
BEFORE = f"{red}[{white}"
AFTER = f"{red}]"
BEFORE_GREEN = f"{red}[{white}"  # Changed from green to red
AFTER_GREEN = f"{red}]"  # Changed from green to red
INPUT = f"{BEFORE}>{AFTER} |"
GEN_VALID = f"{BEFORE}+{AFTER} |"  # Removed _GREEN variants
GEN_INVALID = f"{BEFORE}x{AFTER} |"


def current_time_hour():
    return datetime.datetime.now().strftime("%H:%M:%S")


def print_banner():
    print(
        f"{red}"
        + """
                                              @@@@                @%@@                                      
                                       @@@@@@@@@@@@               @@@@@@@@@@%                               
                                  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                          
                                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                         
                                %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        
                               @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                       
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                      
                             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     
                            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                    
                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                   
                          %@@@@@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@@@%                  
                          %@@@@@@@@@@@@@@@@        %@@@@@@@@@@@%@        @@@@@@@@@@@@@@@@@                  
                          %@@@@@@@@@@@@@@@          @@@@@@@@@@@@          @@@@@@@@@@@@@@@%                  
                         %@@@@@@@@@@@@@@@@          @@@@@@@@@@@%          %@@@@@@@@@@@@@@@@                 
                         @@@@@@@@@@@@@@@@@%         @@@@@@@@@@@%         %@@@@@@@@@@@@@@@@@                 
                         @@@@@@@@@@@@@@@@@@@      %@@@@@@@@@@@@@@@      @@@@@@@@@@@@@@@@@@%                 
                         %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                 
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                 
                           @%@@@@@@@@@@@@@%@@   @@@@%@@@@@@@@@%%%@%@@  @@@@@@@@@@@@@@@@@@                   
                              @@%@@@@@@@@@@@@@                        @%@@@@@@@@@@@%@@                      
                                   @%@@@@@@@                            @@@@@@%%@                           
                                         @@                              @@                           
           """
    )


def get_tokens():
    tokens = []
    try:
        num_tokens = int(
            input(
                f"{BEFORE + current_time_hour() + AFTER} {INPUT} How many tokens? -> {reset}"
            )
        )
        print(f"\n{BEFORE + current_time_hour() + AFTER} {INPUT} Enter your tokens:")

        for i in range(num_tokens):
            token = input(
                f"{BEFORE + current_time_hour() + AFTER} {INPUT} Token {i+1}/{num_tokens} -> {reset}"
            )

            # Verify token
            response = requests.get(
                "https://discord.com/api/v8/users/@me", headers={"Authorization": token}
            )

            if response.status_code == 200:
                user = response.json()
                username = user["username"]
                tokens.append(token)
                print(
                    f" {BEFORE}{i+1}{AFTER} -> {red}Status: {white}Valid{red} | User: {white}{username}"
                )
            else:
                print(f" {BEFORE}{i+1}{AFTER} -> {red}Status: {white}Invalid{red}")

        return tokens
    except ValueError:
        print(f"{BEFORE + current_time_hour() + AFTER} {GEN_INVALID} Invalid number")
        exit(1)


def get_channels():
    channels = []
    try:
        num_channels = int(
            input(
                f"{BEFORE + current_time_hour() + AFTER} {INPUT} How many channels? -> {reset}"
            )
        )
        for i in range(num_channels):
            channel = input(
                f"{BEFORE + current_time_hour() + AFTER} {INPUT} Channel ID {i+1}/{num_channels} -> {reset}"
            )
            channels.append(channel)
        return channels
    except ValueError:
        print(f"{BEFORE + current_time_hour() + AFTER} {GEN_INVALID} Invalid number")
        exit(1)


def raid(tokens, channels, message):
    try:
        token = random.choice(tokens)
        channel = random.choice(channels)
        response = requests.post(
            f"https://discord.com/api/channels/{channel}/messages",
            data={"content": message},
            headers={
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
        )
        response.raise_for_status()
        message_preview = message[:10] + "..." if len(message) > 10 else message
        print(
            f"{BEFORE + current_time_hour() + AFTER} {GEN_VALID} Message: {white}{message_preview}{red} Channel: {white}{channel}{red} Status: {white}Sent{red}"
        )
    except Exception as e:
        print(
            f"{BEFORE + current_time_hour() + AFTER} {GEN_INVALID} Channel: {white}{channel}{red} Status: {white}Error{red}"
        )


def main():
    print_banner()
    print(
        f"{BEFORE + current_time_hour() + AFTER} {GEN_VALID} {red}Discord Server Raid Tool{reset}"
    )
    print(f"{BEFORE + current_time_hour() + AFTER} {GEN_VALID} {red}By: joshy{reset}")

    tokens = get_tokens()
    if not tokens:
        print(
            f"{BEFORE + current_time_hour() + AFTER} {GEN_INVALID} No valid tokens provided"
        )
        exit(1)

    channels = get_channels()
    message = input(
        f"{BEFORE + current_time_hour() + AFTER} {INPUT} Spam Message -> {reset}"
    )

    try:
        thread_count = int(
            input(
                f"{BEFORE + current_time_hour() + AFTER} {INPUT} Number of threads (recommended: 2-4) -> {reset}"
            )
        )
    except ValueError:
        print(f"{BEFORE + current_time_hour() + AFTER} {GEN_INVALID} Invalid number")
        exit(1)

    print(f"\n{BEFORE + current_time_hour() + AFTER} Starting raid...")

    while True:
        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=raid, args=(tokens, channels, message))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    main()
