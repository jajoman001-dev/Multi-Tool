import requests
import socket
import dns.resolver
import whois
from datetime import datetime
from colorama import Fore, Style, init
import os

init(autoreset=True)


if not os.path.exists("results"):
    os.makedirs("results")


def print_banner():
    print(
        Fore.RED
        + """
                                      :**+ :::+*@@.                                                         
                              +: @ = =.  :#@@@@@@@@                 :     .=*@@#     -                      
                 @@@@-. :=: +@@.:% *=@@:   @@@@@@          :#=::     .:@=@@@@@@@@@@@@@@@@@@@@--.-:          
             .#@@@@@@@@@@@@@@@@@@:# .@@   #@@    :@-     +@@:@@@+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*        
             #*   :%@@@@@@@@@@:   .@@#*              ..  ##@ *#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-:- %=         
                   *@@@@@@@@@@@@%@@@@@@@            = @=+@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+   #.        
                   #@@@@@@@@@##@@@@@= =#              #@@@#@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=            
                  @@@@@@@@@@@#+#@@=                 :@@@-.#-*#@.  .@@.=%@@@@%@@@@@@@@@@@@@@@@@=  +          
                 :@@@@@@@@@@@@@@:                   :@@    # - @@@@@@@ =@@@*#*@@@@@@@@@@@@@=.=-  #:         
                  :@@@@@@@@@@@+                     @@@@@@@: :    @@@@@@@@@@@@@@@@@@@@@@@@@@@               
                   #@@@@@    @                     #%@@@@@@@@@@@@@@@@@:@@@@@@@@@@@@#@@@@@@@@@:              
                     @@@     .                    @@@@@@@@@@@@@@@@-%@@@%@#   @@@@@@#=@#@@@@@==              
                     =@@##@   =:*.                @@@@@@*@@@@@@@@@@-=@@@@.    +@@@:  %#@@#=   :             
                         .=@.                     #@@@@@@@@#@@@@@@@@+#:        %@      *%@=                 
                            . @@@@@@               @#@@*@@@@@@@@@@@@@@@=        :-     -       =.           
                             :@@@@@@@#=                   @@@@@@@@@@@@-               :+%  .@=              
                            -@@@@@@@@@@@@                 @+@@@@*+@@#                   @. @@.#   # :       
                             @@@@@@@@@@@@@@@               @@@@@*@@@                     :=.        @@@.    
                              @@@@@@@@@@@@@                #@@@@@@%@.                             :  :      
                               *@@@@@@@@@@%               :@@@@@@@@@ @@.                      .@@@@=:@      
                                :@@@@@@@@@                 #@@@@@@   @:                    .#@@@@@@@@@@     
                                :@@@@%@@                   .@@@@@-   .                     @@@@@@@@@@@@*    
                                :@@@@@@.                    *@@@-                          @@@@#@@@@@@@     
                                .@@@@@                                                           =@@@:    @=
                                 =@@                                                              =    #+   
                                  @%                                                                       
    """
        + Fore.RESET
    )


def get_whois_info(domain):
    """Get WHOIS information for the domain"""
    try:
        import whois

        w = whois.whois(domain)
        if w is None:
            return {"Error": "No WHOIS information found"}

        return {
            "Registrar": w.registrar if hasattr(w, "registrar") else "Unknown",
            "Creation Date": (
                w.creation_date if hasattr(w, "creation_date") else "Unknown"
            ),
            "Expiration Date": (
                w.expiration_date if hasattr(w, "expiration_date") else "Unknown"
            ),
            "Name Servers": w.name_servers if hasattr(w, "name_servers") else [],
            "Status": w.status if hasattr(w, "status") else "Unknown",
            "Emails": w.emails if hasattr(w, "emails") else [],
        }
    except Exception as e:
        return {"Error": str(e)}


def get_dns_records(domain):
    """Get various DNS records for the domain"""
    records = {}
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            records[record_type] = [str(rdata) for rdata in answers]
        except Exception:
            continue

    return records


def check_https(domain):
    """Check if HTTPS is available"""
    try:
        response = requests.get(f"https://{domain}", timeout=5, verify=True)
        return {
            "HTTPS Available": True,
            "Status Code": response.status_code,
            "Server": response.headers.get("Server", "Unknown"),
        }
    except Exception as e:
        return {"HTTPS Available": False, "Error": str(e)}


def print_results(results):
    """Print results in a formatted way"""
    for section, data in results.items():
        print(f"\n{Fore.GREEN}=== {section} ==={Fore.RESET}")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{Fore.CYAN}{key}:{Fore.RESET} {value}")
        elif isinstance(data, list):
            for item in data:
                print(f"{Fore.CYAN}-{Fore.RESET} {item}")
        else:
            print(data)


def send_to_webhook(webhook_url, results):
    """Send results to Discord webhook"""
    try:
        # Format the message
        message = "```ini\n[Domain Reconnaissance Results]\n"
        for section, data in results.items():
            message += f"\n[{section}]\n"
            if isinstance(data, dict):
                for key, value in data.items():
                    message += f"{key}: {value}\n"
            elif isinstance(data, list):
                for item in data:
                    message += f"- {item}\n"
            else:
                message += f"{data}\n"
        message += "```"

        # Split message if it's too long (Discord limit is 2000 characters)
        if len(message) > 1990:
            messages = [message[i : i + 1990] for i in range(0, len(message), 1990)]
        else:
            messages = [message]

        # Send each part
        for msg in messages:
            payload = {"content": msg}
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        return True
    except Exception as e:
        print(f"{Fore.RED}Error sending to webhook: {str(e)}{Fore.RESET}")
        return False


def domain_recon():
    print(f"\n{Fore.YELLOW}Enter domain name (e.g., example.com):{Fore.RESET}")
    domain = input().strip()

    print(f"\n{Fore.CYAN}Gathering information about {domain}...{Fore.RESET}")

    results = {
        "Basic Information": {
            "Domain": domain,
            "IP Address": socket.gethostbyname(domain),
        },
        "WHOIS Information": get_whois_info(domain),
        "DNS Records": get_dns_records(domain),
        "HTTPS Check": check_https(domain),
    }

    print_results(results)

    # Option to save results
    save = input(f"\n{Fore.YELLOW}Save results to file? (y/n):{Fore.RESET} ").lower()
    if save == "y":
        filename = (
            f"domain_recon_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        filepath = os.path.join("results", filename)
        with open(filepath, "w") as f:
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
        print(f"{Fore.GREEN}Results saved to {filepath}{Fore.RESET}")

    # Option to send results to webhook
    webhook = input(
        f"\n{Fore.YELLOW}Send results to Discord webhook? (y/n):{Fore.RESET} "
    ).lower()
    if webhook == "y":
        webhook_url = input(
            f"\n{Fore.YELLOW}Enter Discord webhook URL:{Fore.RESET} "
        ).strip()
        if send_to_webhook(webhook_url, results):
            print(f"{Fore.GREEN}Results sent to Discord webhook{Fore.RESET}")


if __name__ == "__main__":
    print_banner()
    while True:
        domain_recon()
        if (
            input(f"\n{Fore.YELLOW}Scan another domain? (y/n):{Fore.RESET} ").lower()
            != "y"
        ):
            break
