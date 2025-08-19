import requests
import hashlib
import re
from datetime import datetime
from colorama import Fore, Style, init
import os
from urllib.parse import quote_plus

init(autoreset=True)


def print_banner():
    print(
        Fore.RED
        + """
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                   >|a@@@@@@@@@|                                                 
                                              }@@@@@@@@@@@@@@@@| 000M|                                          
                                          ;@@@@@@O  @@@@@@@@@@@|  j000000_                                      

                                       }@@@@@v   |@@@@@@@@@@@@@| 00J  |00000j                                   
                                     @@@@@_     @@@@@@@@@@@@@@@| 0000    ;00000^                                
                                  ;@@@@v       _@@@@@@@     >@@| 0000v      }0000_                              
                                ^@@@@_         @@@@@@@      ^O@| 00000        ;0000_                            
                                 @@@@;         @@@@@@@      ;p@| 00000         0000^                            
                                   @@@@p       >@@@@@@@^    >@@| 0000v      J0000;                              
                                     O@@@@|     M@@@@@@@@@@@@@@| 0000    >00000                                 
                                       ;@@@@@J^  }@@@@@@@@@@@@@| 00v  j00000}                                   
                                          >@@@@@@@_;@@@@@@@@@@@| ;M000000_                                      
                                              >@@@@@@@@@@@@@@@@| 00000}                                          
                                                   ^jpM@@@@@@@@|                                                 
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                            >@@|                                                 
                                                            >@@| 
    """
        + Fore.RESET
    )


def check_email_format(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def check_haveibeenpwned(email):
    """Check if email appears in data breaches"""
    # No API key version - return manual check links
    manual_check_urls = {
        "HaveIBeenPwned": f"https://haveibeenpwned.com/account/{email}",
        "DeHashed": f"https://dehashed.com/search?query={email}",
        "BreachDirectory": f"https://breachdirectory.org/{email}",
        "LeakCheck": f"https://leakcheck.io/search/{email}",
    }
    return {"message": "Please check these sites manually:", "urls": manual_check_urls}


def get_email_hash(email):
    """Generate different hash formats of the email"""
    return {
        "MD5": hashlib.md5(email.encode()).hexdigest(),
        "SHA1": hashlib.sha1(email.encode()).hexdigest(),
        "SHA256": hashlib.sha256(email.encode()).hexdigest(),
    }


def check_social_media(email):
    """Check common social media platforms"""
    username = email.split("@")[0]
    domain = email.split("@")[1]

    platforms = {
        "GitHub": f"https://api.github.com/search/users?q={email}",
        "Gravatar": f"https://en.gravatar.com/{hashlib.md5(email.lower().encode()).hexdigest()}",
        "LinkedIn": f"https://www.linkedin.com/pub/dir?email={email}",
        "Twitter": f"https://twitter.com/search?q={email}",
        "Facebook": f"https://www.facebook.com/search/top?q={email}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Medium": f"https://medium.com/@{username}",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Mastodon": f"https://mastodon.social/@{username}",
    }

    results = {}
    for platform, url in platforms.items():
        try:
            response = requests.get(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5
            )
            results[platform] = {"exists": response.status_code == 200, "url": url}
        except:
            results[platform] = {"exists": False, "url": url}
    return results


def check_paste_sites(email):
    """Check various paste sites for email occurrences"""
    # No API key version - return manual search links
    manual_search_urls = {
        "Google (Pastebin)": f"https://www.google.com/search?q=site:pastebin.com+{quote_plus(email)}",
        "Google (Github Gists)": f"https://www.google.com/search?q=site:gist.github.com+{quote_plus(email)}",
        "Google (Gitlab Snippets)": f"https://www.google.com/search?q=site:gitlab.com+{quote_plus(email)}",
    }
    return {
        "message": "Please check these search engines manually:",
        "urls": manual_search_urls,
        "found_pastes": [],
    }


def check_google_account(email):
    """Check Google account information and connected services"""
    results = {"Account Exists": False, "Services": [], "Profile Info": {}, "Links": {}}

    encoded_email = quote_plus(email)

    # Check Google Account existence
    try:
        response = requests.get(
            f"https://accounts.google.com/_/lookup/accountlookup?hl=en&_reqid=0&rt=j",
            params={"email": email},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if '"errormsg"' not in response.text:
            results["Account Exists"] = True
    except Exception:
        results["Account Exists"] = "Error checking"

    # Generate service check links
    if results["Account Exists"]:
        results["Links"] = {
            "Google Profile": f"https://about.me/{encoded_email}",
            "Google Calendar": f"https://calendar.google.com/calendar/u/0/embed?src={encoded_email}",
            "Google Docs History": f"https://docs.google.com/document/u/0/?usp={encoded_email}",
            "Google Maps Reviews": f"https://www.google.com/maps/contrib/{encoded_email}",
            "Youtube Channel": f"https://www.youtube.com/user/{encoded_email}",
        }

        # Check Google services
        services = [
            ("Google Photos", f"https://get.google.com/albumarchive/{encoded_email}"),
            ("Google Plus", f"https://plus.google.com/{encoded_email}"),
            ("Blogger", f"https://www.blogger.com/profile/{encoded_email}"),
        ]

        for service, url in services:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    results["Services"].append(service)
            except Exception:
                pass

    return results


def save_results(email, results):
    """Save results to file"""
    if not os.path.exists("results"):
        os.makedirs("results")

    filename = (
        f"results/email_osint_{email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    with open(filename, "w") as f:
        f.write(f"Email OSINT Results for {email}\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for section, data in results.items():
            f.write(f"\n=== {section} ===\n")
            if isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
            elif isinstance(data, list):
                for item in data:
                    f.write(f"- {item}\n")
            else:
                f.write(str(data) + "\n")
    return filename


def split_message(message, max_length=1994):
    """Split the message into chunks of max_length (2000 characters for Discord)."""
    return [message[i : i + max_length] for i in range(0, len(message), max_length)]


def format_message_with_codeblock(results, email):
    """Format the message with code blocks and no ANSI color codes."""
    formatted_message = f"[Email OSINT Results]\nEmail: {email}\n\n"

    # Prepare the results in a code block
    formatted_message += f"[Hash Values]\n"
    for hash_type, hash_value in results["Hash Values"].items():
        formatted_message += f"{hash_type}: {hash_value}\n"

    formatted_message += f"\n[Data Breach Check Links]\n"
    for site, url in results["Data Breaches"]["urls"].items():
        formatted_message += f"- {site}: {url}\n"

    formatted_message += f"\n[Social Media Presence]\n"
    for platform, data in results["Social Media Presence"].items():
        status = "Found" if data["exists"] else "Not Found"
        formatted_message += f"{platform}: {status} ({data['url']})\n"

    formatted_message += f"\n[Paste Site Search Links]\n"
    for site, url in results["Paste Sites"]["urls"].items():
        formatted_message += f"- {site}: {url}\n"

    formatted_message += f"\n[Google Account]\n"
    if results["Google Account"]["Account Exists"]:
        formatted_message += f"Account Exists: Yes\n"
        formatted_message += (
            f"Services: {', '.join(results['Google Account']['Services'])}\n"
        )
        for link_name, link_url in results["Google Account"]["Links"].items():
            formatted_message += f"{link_name}: {link_url}\n"
    else:
        formatted_message += f"Account Exists: No\n"

    formatted_message += ""  # End of code block

    return formatted_message


def email_osint():
    print(f"\n{Fore.YELLOW}Enter email address to investigate:{Fore.RESET}")
    email = input().strip()

    if not check_email_format(email):
        print(f"{Fore.RED}Invalid email format!{Fore.RESET}")
        return

    print(f"\n{Fore.CYAN}Investigating {email}...{Fore.RESET}\n")

    # Collect results
    results = {
        "Email": email,
        "Hash Values": get_email_hash(email),
        "Data Breaches": check_haveibeenpwned(email),
        "Social Media Presence": check_social_media(email),
        "Paste Sites": check_paste_sites(email),
        "Google Account": check_google_account(email),
    }

    # Initialize results message without formatting (for terminal output)
    results_message = f"[Email OSINT Results]\nEmail: {email}\n\n"

    # Prepare the results without colors (for terminal printing)
    results_message += "[Hash Values]\n"
    for hash_type, hash_value in results["Hash Values"].items():
        results_message += f"{hash_type}: {hash_value}\n"

    results_message += "\n[Data Breach Check Links]\n"
    for site, url in results["Data Breaches"]["urls"].items():
        results_message += f"- {site}: {url}\n"

    results_message += "\n[Social Media Presence]\n"
    for platform, data in results["Social Media Presence"].items():
        status = "Found" if data["exists"] else "Not Found"
        results_message += f"{platform}: {status} ({data['url']})\n"

    results_message += "\n[Paste Site Search Links]\n"
    for site, url in results["Paste Sites"]["urls"].items():
        results_message += f"- {site}: {url}\n"

    results_message += "\n[Google Account]\n"
    if results["Google Account"]["Account Exists"]:
        results_message += f"Account Exists: Yes\n"
        results_message += (
            f"Services: {', '.join(results['Google Account']['Services'])}\n"
        )
        for link_name, link_url in results["Google Account"]["Links"].items():
            results_message += f"{link_name}: {link_url}\n"
    else:
        results_message += f"Account Exists: No\n"

    # Print results without any formatting
    print(f"{Fore.GREEN}=== Results ==={Fore.RESET}")
    print(results_message)

    # Save option
    save = input(f"\n{Fore.YELLOW}Save results to file? (y/n):{Fore.RESET} ").lower()
    if save == "y":
        filename = save_results(email, results)
        print(f"{Fore.GREEN}Results saved to {filename}{Fore.RESET}")

    # Webhook option
    webhook = input(
        f"\n{Fore.YELLOW}Send results to Discord webhook? (y/n):{Fore.RESET} "
    ).lower()
    if webhook == "y":
        webhook_url = input(f"{Fore.YELLOW}Enter webhook URL:{Fore.RESET} ").strip()
        if webhook_url:
            try:
                # Split the message first (without applying code block)
                message_chunks = split_message(results_message)
                for chunk in message_chunks:
                    formatted_message = f"{chunk}"  # Add code block around each chunk
                    # Send chunk to webhook without any ANSI formatting
                    response = requests.post(
                        webhook_url, json={"content": formatted_message}
                    )

                    # Check the response status code to make sure it was successful
                    if response.status_code == 204:
                        print(
                            f"{Fore.GREEN}Results sent to webhook successfully!{Fore.RESET}"
                        )
                    else:
                        print(
                            f"{Fore.RED}Failed to send results to webhook. Status Code: {response.status_code}{Fore.RESET}"
                        )
                        print(f"Response: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}Error sending to webhook: {str(e)}{Fore.RESET}")


if __name__ == "__main__":
    print_banner()
    while True:
        email_osint()
        if (
            input(
                f"\n{Fore.YELLOW}Investigate another email? (y/n):{Fore.RESET} "
            ).lower()
            != "y"
        ):
            break
