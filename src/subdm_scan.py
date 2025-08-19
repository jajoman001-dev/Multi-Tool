import dns.resolver
import sys
import os
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
import time
import msvcrt  # For Windows keyboard input

# Initialize colorama for Windows
init()


class SubdomainScanner:
    def __init__(self, domain, use_online_wordlist=True):
        self.domain = domain
        self.wordlist_url = "https://raw.githubusercontent.com/n0kovo/n0kovo_subdomains/refs/heads/main/n0kovo_subdomains_large.txt"
        self.cache_folder = "cache"
        self.local_wordlist = os.path.join(self.cache_folder, "wordlist_cache.txt")
        self.use_online_wordlist = use_online_wordlist
        self.found_domains = []
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 1
        self.resolver.lifetime = 1

    def download_wordlist(self):
        try:
            # Check if cache folder exists, if not, create it
            if not os.path.exists(self.cache_folder):
                os.makedirs(self.cache_folder)

            print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Downloading wordlist...")
            response = requests.get(self.wordlist_url)
            response.raise_for_status()

            with open(self.local_wordlist, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Wordlist downloaded successfully")
            return True
        except Exception as e:
            print(
                f"{Fore.RED}[-]{Style.RESET_ALL} Error downloading wordlist: {str(e)}"
            )
            return False

    def load_wordlist(self):
        try:
            # Ensure that the wordlist is downloaded or exists locally
            if self.use_online_wordlist and (
                not os.path.exists(self.local_wordlist)
                or os.path.getsize(self.local_wordlist) == 0
            ):
                if not self.download_wordlist():
                    return []

            with open(self.local_wordlist, "r", encoding="utf-8") as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Error loading wordlist: {str(e)}")
            return []

    def check_subdomain(self, subdomain):
        try:
            host = f"{subdomain}.{self.domain}"
            self.resolver.resolve(host, "A")
            ip = self.resolver.resolve(host, "A")[0]
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Found: {host} [{ip}]")
            return host
        except:
            return None

    def scan(self):
        print(
            f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Starting subdomain scan for: {self.domain}"
        )
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to stop the scan")
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Loading wordlist...")

        subdomains = self.load_wordlist()
        if not subdomains:
            return []

        total_subdomains = len(subdomains)
        print(
            f"{Fore.BLUE}[*]{Style.RESET_ALL} Testing {total_subdomains} possible subdomains..."
        )

        start_time = time.time()
        scanned = 0
        scan_stopped = False

        def check_keyboard():
            while not scan_stopped:
                if msvcrt.kbhit():
                    if msvcrt.getch() in [b"\r", b"\n"]:
                        return True
                time.sleep(0.1)
            return False

        def check_and_count(subdomain):
            nonlocal scanned, scan_stopped

            if scan_stopped:
                return None

            result = self.check_subdomain(subdomain)
            scanned += 1

            if scanned % 100 == 0:
                elapsed_time = time.time() - start_time
                scan_rate = scanned / elapsed_time
                print(
                    f"{Fore.YELLOW}[*]{Style.RESET_ALL} Progress: {scanned}/{total_subdomains} ({scan_rate:.2f} scans/sec)"
                )

            return result

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # Start keyboard monitoring in a separate thread
            keyboard_future = executor.submit(check_keyboard)

            # Submit all subdomain checks
            for subdomain in subdomains:
                if scan_stopped:
                    break
                futures.append(executor.submit(check_and_count, subdomain))

            # Process results as they complete
            for future in as_completed(futures):
                try:
                    if keyboard_future.done() and keyboard_future.result():
                        scan_stopped = True
                        break

                    result = future.result()
                    if result:
                        self.found_domains.append(result)

                except Exception as e:
                    continue

                if scan_stopped:
                    break

            # Cancel remaining futures if scan was stopped
            if scan_stopped:
                for future in futures:
                    if not future.done():
                        future.cancel()

        elapsed_time = time.time() - start_time
        final_scan_rate = scanned / elapsed_time if scanned > 0 else 0

        print(
            f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Scan {'stopped' if scan_stopped else 'completed'} in {elapsed_time:.2f} seconds"
        )
        print(
            f"{Fore.BLUE}[*]{Style.RESET_ALL} Average scan rate: {final_scan_rate:.2f} scans/sec"
        )

        return self.found_domains

    def save_results_to_json(self):
        if not os.path.exists("results"):
            os.makedirs("results")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"results/scan_{self.domain}_{timestamp}.json"

        results = {
            "domain": self.domain,
            "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "subdomains": self.found_domains,
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=4)

        return filename


def print_banner():
    banner = f"""
{Fore.CYAN}
                                     %@@@@@@@@@@@@@@@@%                
                                   @@@@@@@@@@@@@@@@@@@@@@@@             
                               @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         
                             %@@@@@@@@@@@@  %@@@@  @@@@@@@@@@@@@@       
                           %@@@@@@%@@@@@@   %@@@@    @@@@@@@@@@@@@%     
                          @@@@@@@@@@@@@     %@@@@     *@@@@%@@@@@@@@    
                         @@@@@@@@@@@@@@@    %@@@@    @@@@@@@@@@@@@@@@   
                        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@  
                       @@@@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   @@@@@@ 
                       @@@@@   @@@@@        %@@@@        @@@@@    @@@@@@
                       @@@@    @@@@@        %@@@@        #@@@@@   %@@@@@
                       @@@     @@@@+        %@@@@         @@@@@    @@@@@
                       @@@@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@
                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                       @@@%%%%%@@@@%%%%%%%%%@@@@@%%%%%%%%%@@@@@%%%%@@@@@
                       @@@     @@@@         %@@@@         @@@@@    @@@@@
                       @@@@    @@@@%        %@@@@         @@@@@   %@@@@@
                       @@@@%   @@@@@        %@@@@        @@@@@    @@@@@@
                       @@@@@   @@@@@% #@@@@@@@@@@@@@@@%  @@@@@   @@@@@@ 
                        @@@@@@ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@  
                         @@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@   
                          @@@@@@@@@@@@#     %@@@@      @@@@@@@@@@@@@    
                           %@@@@@@%@@@@%    %@@@@     @@@@@%@@@@@@%     
                             @@@@@@@@@@@@@  %@@@@   @@@@@@@@@@@@%       
                               @@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@         
                                   @@@@@@@@@@@@@@@@@@@@@@@@             
                                      %@@@@@@@@@@@@@@@@%                
{Style.RESET_ALL}"""
    print(banner)


def menu():
    while True:
        os.system("cls")
        print_banner()
        print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Start Subdomain Scan")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Update Wordlist")
        print(f"{Fore.RED}[3]{Style.RESET_ALL} Exit")

        choice = input(f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Select an option: ")

        if choice == "1":
            domain = input(
                f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Enter target domain (e.g., example.com): "
            )
            scanner = SubdomainScanner(domain)
            found = scanner.scan()

            if found:
                print(
                    f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Found {len(found)} subdomains!"
                )
                print("\nDiscovered subdomains:")
                for subdomain in found:
                    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {subdomain}")

                save_choice = input(
                    f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Do you want to save results to JSON? (y/n): "
                )
                if save_choice.lower() == "y":
                    filename = scanner.save_results_to_json()
                    print(
                        f"{Fore.GREEN}[+]{Style.RESET_ALL} Results saved to: {filename}"
                    )
            else:
                print(f"\n{Fore.RED}[-]{Style.RESET_ALL} No subdomains found.")

            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        elif choice == "2":
            scanner = SubdomainScanner("dummy.com")
            scanner.download_wordlist()
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        elif choice == "3":
            print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Exiting...")
            sys.exit(0)

        else:
            print(f"\n{Fore.RED}[-]{Style.RESET_ALL} Invalid option!")
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")


if __name__ == "__main__":
    menu()
