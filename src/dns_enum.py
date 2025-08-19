import dns.resolver
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import socket
import ipaddress
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()


class DNSEnum:
    def __init__(self, target):
        self.target = target
        self.record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME", "PTR"]
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 2
        self.resolver.lifetime = 2
        self.results = {}

    def is_ip(self, target):
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            return False

    def get_ptr_record(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return None

    def query_dns(self, record_type):
        try:
            if self.is_ip(self.target) and record_type != "PTR":
                return {record_type: ["Skipped - Target is an IP"]}

            if record_type == "PTR" and self.is_ip(self.target):
                ptr = self.get_ptr_record(self.target)
                return {"PTR": [ptr if ptr else "No PTR record found"]}

            answers = self.resolver.resolve(self.target, record_type)
            results = []
            for answer in answers:
                if record_type == "A":
                    ptr = self.get_ptr_record(str(answer))
                    results.append(f"{answer} --> {ptr if ptr else 'No PTR record'}")
                else:
                    results.append(str(answer))
            return {record_type: results}
        except Exception as e:
            return {record_type: [f"Error: {str(e)}"]}

    def enumerate(self):
        print(
            f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Performing DNS enumeration for: {self.target}"
        )
        print(
            f"{Fore.GREEN}[+]{Style.RESET_ALL} Target type: {'IP Address' if self.is_ip(self.target) else 'Domain'}\n"
        )

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.query_dns, self.record_types))

        for result in results:
            for record_type, values in result.items():
                if not (self.is_ip(self.target) and "Skipped" in values[0]):
                    print(f"{Fore.BLUE}[*]{Style.RESET_ALL} {record_type} Records:")
                    for value in values:
                        print(f"    {value}")
                    print()

        return results


def dns_enum_handler(target):
    try:
        dns_enum = DNSEnum(target)
        return dns_enum.enumerate()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} DNS enumeration interrupted by user")
        return None
    except Exception as e:
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} An error occurred: {str(e)}")
        return None


def print_banner():
    banner = f"""
{Fore.CYAN}      @@@@@@@@@@@@@@                  
             @@@@@@@@@@@@@@@@@@@@@@@@             
          %@@@@@@@@@@  @@@@  @@@@@@@@@@@          
        @@@@@  @@@@    @@@@    @@@@  @@@@@        
       @@@@    @@@     @@@@     @@@@   @@@@       
     @@@@@@@@@@@@      @@@@      @@@@@@@@@@@@     
    @@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@   @@@@    
   @@@@     @@@@@@@@@@@@@@@@@@@@@@@@@@     @@@@   
   @@@      @@@        @@@@        @@@      @@@   
  @@@@     @@@@      @@    @@    %@@@       @@@@  
  @@@      @@@@@@@  @@@@@ @@@@ @@@@@@@@      @@@  
 @@@@ %    @@@ @@@@ @@@@@ @@@@ @@@@ @@@   @@ @@@@ 
 @@@@@@@@@ @@@  @@@ @@@@@@@@@@  @@@@@@@ @@@@@@@@@ 
 @@@@@@@   @@@ @@@@ @@@@@@@@@@ @@@ @@@@   @@@@@@@ 
  @@@      @@@@@@@  @@@@ @@@@@ @@@@@@@@      @@@  
  @@@@     @@@@      @@    @@    %@@@       @@@@  
   @@@      @@@        @@@@        @@@      @@@   
   @@@@     @@@@@@@@@@@@@@@@@@@@@@@@@@     @@@@   
    @@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@   @@@@    
     @@@@@@@@@@@@      @@@@      @@@@@@@@@@@@     
       @@@@    @@@     @@@@     @@@@   @@@@       
        @@@@@  @@@@    @@@@    @@@@  @@@@@        
          @@@@@@@@@@@  @@@@  @@@@@@@@@@@          
             @@@@@@@@@@@@@@@@@@@@@@@@             
                @@@@@@@@@@@@@@@ %
    {Style.RESET_ALL}
"""

    term_width = os.get_terminal_size().columns
    # Split banner into lines and remove empty leading/trailing lines
    banner_lines = [line for line in banner.split("\n") if line.strip()]

    # Print each line centered
    for line in banner_lines:
        padding = (term_width - len(line.strip())) // 2
        print(" " * padding + line.strip())


def menu():
    while True:
        print_banner()
        print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Perform DNS enumeration")
        print(f"{Fore.RED}[2]{Style.RESET_ALL} Exit")

        choice = input(f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Select an option: ")

        if choice == "1":
            target = input(
                f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Enter target domain/IP (e.g., example.com or 8.8.8.8): "
            )
            if target.strip():
                dns_enum_handler(target)
                input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")
            else:
                print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Invalid target")
                input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        elif choice == "2":
            print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Exiting...")
            sys.exit(0)

        else:
            print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Invalid option")
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        os.system("cls")


def main():
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description="DNS Enumeration Tool")
        parser.add_argument(
            "-t", "--target", required=True, help="Target domain or IP address"
        )
        args = parser.parse_args()
        dns_enum_handler(args.target)
    else:
        # Interactive menu mode
        menu()


if __name__ == "__main__":
    import os

    main()

# Remove or comment out these lines as they're not needed anymore
# results = dns_enum_handler("example.com")
# results = dns_enum_handler("8.8.8.8")
