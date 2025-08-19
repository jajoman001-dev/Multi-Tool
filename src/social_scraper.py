import requests
from colorama import Fore, Style, init
import threading
from queue import Queue
from datetime import datetime
import json
import os
import time
from urllib.parse import quote_plus
import concurrent.futures

init(autoreset=True)


def print_banner():
    print(
        Fore.CYAN
        + """
                                          ...:----:...                                              
                                     .:=#@@@@@@@@@@@@@@%*-..                                        
                                  .:#@@@@@@@%#*****#%@@@@@@@+..                                     
                               ..-@@@@@%-...... ........+@@@@@@..                                   
                               :%@@@@=..   .#@@@@@@@@#=....+@@@@*.                                  
                             .+@@@@=.      .*@@@%@@@@@@@@=...*@@@@:.                                
                            .#@@@%.                 .=@@@@@=. .@@@@-.                               
                           .=@@@#.                    .:%@@@*. -@@@%:.                              
                           .%@@@-                       .*@@*. .+@@@=.                              
                           :@@@#.                              .-@@@#.                              
                           -@@@#                                :%@@@.                              
                           :@@@#.                              .-@@@#.                              
                           .%@@@-.                             .+@@@=.                              
                           .+@@@#.                             -@@@%:.                              
                            .*@@@%.                          .:@@@@-.                               
                             .+@@@@=..                     ..*@@@@:.                                 
                               :%@@@@-..                ...+@@@@*.                                  
                               ..-@@@@@%=...         ...*@@@@@@@@#.                                 
                                  .:*@@@@@@@%*++++**@@@@@@@@=:*@@@@#:.                              
                                     ..=%@@@@@@@@@@@@@@%#-.   ..*@@@@%:.                            
                                        .....:::::::....       ...+@@@@%:                           
                                                                  ..+@@@@%-.                        
                                                                    ..=@@@@%-.                      
                                                                      ..=@@@@@=.                    
                                                                         .=%@@@@=.                  
                                                                          ..-%@@@-.                 
                                                                             ....
    """
        + Fore.RESET
    )


def check_rate_limits(headers=None):
    """Basic rate limiting"""
    time.sleep(1)  # Basic delay between requests
    return headers or {"User-Agent": "Mozilla/5.0"}


def scrape_profile(platform, username, results):
    """Scrape individual social media profile"""
    try:
        headers = check_rate_limits()
        platforms = {
            "GitHub": f"https://api.github.com/users/{username}",
            "Twitter": f"https://x.com/{username}",
            "Instagram": f"https://www.instagram.com/{username}",
            "Reddit": f"https://www.reddit.com/user/{username}/about.json",
            "Medium": f"https://medium.com/@{username}",
            "LinkedIn": f"https://www.linkedin.com/in/{username}",
            "Facebook": f"https://www.facebook.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "YouTube": f"https://www.youtube.com/@{username}",
            "Pinterest": f"https://pinterest.com/{username}",
            "Twitch": f"https://www.twitch.tv/{username}",
            "Snapchat": f"https://www.snapchat.com/add/{username}",
            "WhatsApp": f"https://wa.me/{username}",
            "Discord": f"https://discord.com/users/{username}",
            "Vimeo": f"https://vimeo.com/{username}",
            "GitLab": f"https://gitlab.com/{username}",
            "Bitbucket": f"https://bitbucket.org/{username}",
            "Flickr": f"https://www.flickr.com/photos/{username}",
            "SoundCloud": f"https://soundcloud.com/{username}",
            "Vine (archive)": f"https://vine.co/{username}",
            "Behance": f"https://www.behance.net/{username}",
            "Dribbble": f"https://dribbble.com/{username}",
            "Periscope": f"https://www.pscp.tv/{username}",
            "Meetup": f"https://www.meetup.com/members/{username}",
            "Goodreads": f"https://www.goodreads.com/user/show/{username}",
            "Quora": f"https://www.quora.com/profile/{username}",
            "StackOverflow": f"https://stackoverflow.com/users/{username}",
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Trello": f"https://trello.com/{username}",
            "Slack": f"https://{username}.slack.com/",
            "WeChat": f"https://web.wechat.com/{username}",
            "Telegram": f"https://t.me/{username}",
            "Redbubble": f"https://www.redbubble.com/people/{username}",
            "Etsy": f"https://www.etsy.com/shop/{username}",
            "Giphy": f"https://giphy.com/{username}",
            "Patreon": f"https://www.patreon.com/{username}",
            "Ko-fi": f"https://ko-fi.com/{username}",
            "Substack": f"https://{username}.substack.com/",
            "Letterboxd": f"https://letterboxd.com/{username}",
            "Anchor": f"https://anchor.fm/{username}",
            "Mix": f"https://mix.com/{username}",
            "Plurk": f"https://www.plurk.com/{username}",
            "SlideShare": f"https://www.slideshare.net/{username}",
            "Clubhouse": f"https://www.joinclubhouse.com/@{username}",
            "Foursquare": f"https://foursquare.com/{username}",
            "Yelp": f"https://www.yelp.com/user_details?userid={username}",
        }

        if platform not in platforms:
            return

        url = platforms[platform]
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            results[platform] = {"exists": True, "url": url, "status": "Found"}

            # Platform-specific data extraction
            if platform == "GitHub":
                data = response.json()
                results[platform].update(
                    {
                        "name": data.get("name"),
                        "bio": data.get("bio"),
                        "public_repos": data.get("public_repos"),
                        "followers": data.get("followers"),
                    }
                )
            # Add more platform-specific extractors here

        elif response.status_code == 404:
            results[platform] = {"exists": False, "url": url, "status": "Not Found"}
        else:
            results[platform] = {
                "exists": None,
                "url": url,
                "status": f"Error: {response.status_code}",
            }

    except Exception as e:
        results[platform] = {
            "exists": None,
            "url": platforms.get(platform, ""),
            "status": f"Error: {str(e)}",
        }


def save_results(username, results):
    """Save scan results to file"""
    if not os.path.exists("results"):
        os.makedirs("results")

    filename = f"results/social_scan_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)
    return filename


def social_scraper():
    """Main social media scraping function"""
    print(f"\n{Fore.YELLOW}Enter username to search:{Fore.RESET}")
    username = input().strip()

    if not username:
        print(f"{Fore.RED}Invalid username!{Fore.RESET}")
        return

    print(f"\n{Fore.CYAN}[*] Starting social media scan for: {username}")
    print(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}\n")

    results = {}
    platforms = [
        "GitHub",
        "Twitter",
        "Instagram",
        "Reddit",
        "Medium",
        "LinkedIn",
        "Facebook",
        "TikTok",
        "YouTube",
        "Pinterest",
        "Twitch",
        "Snapchat",
        "WhatsApp",
        "Discord",
        "Vimeo",
        "GitLab",
        "Bitbucket",
        "Flickr",
        "SoundCloud",
        "Vine (archive)",
        "Behance",
        "Dribbble",
        "Periscope",
        "Meetup",
        "Goodreads",
        "Quora",
        "StackOverflow",
        "Steam",
        "Trello",
        "Slack",
        "WeChat",
        "Telegram",
        "Redbubble",
        "Etsy",
        "Giphy",
        "Patreon",
        "Ko-fi",
        "Substack",
        "Letterboxd",
        "Anchor",
        "Mix",
        "Plurk",
        "SlideShare",
        "Clubhouse",
        "Foursquare",
        "Yelp",
    ]

    # Use ThreadPoolExecutor for parallel scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(scrape_profile, platform, username, results)
            for platform in platforms
        ]

        # Show progress
        completed = 0
        total = len(platforms)
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            print(
                f"{Fore.CYAN}[*] Progress: {completed}/{total} platforms scanned{Fore.RESET}",
                end="\r",
            )

    print("\n")  # Clear progress line

    # Display results
    found_count = 0
    print(f"\n{Fore.CYAN}[*] Scan Results:{Fore.RESET}")

    for platform, data in results.items():
        if data["exists"]:
            found_count += 1
            print(f"\n{Fore.GREEN}[+] {platform}: Profile Found{Fore.RESET}")
            for key, value in data.items():
                if key not in ["exists", "status"]:
                    print(f"    {key}: {value}")
        elif data["exists"] is False:
            print(f"{Fore.RED}[-] {platform}: Not Found{Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}[?] {platform}: {data['status']}{Fore.RESET}")

    print(f"\n{Fore.CYAN}[*] Scan Summary:")
    print(f"[*] Total platforms checked: {len(platforms)}")
    print(f"[*] Profiles found: {found_count}{Fore.RESET}")

    # Save option
    save = input(f"\n{Fore.YELLOW}Save results to file? (y/n):{Fore.RESET} ").lower()
    if save == "y":
        filename = save_results(username, results)
        print(f"{Fore.GREEN}[+] Results saved to: {filename}{Fore.RESET}")


if __name__ == "__main__":
    print_banner()
    while True:
        social_scraper()
        if (
            input(f"\n{Fore.YELLOW}Scan another username? (y/n):{Fore.RESET} ").lower()
            != "y"
        ):
            break
