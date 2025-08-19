import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin
from colorama import init, Fore, Style
import sys

# Initialize colorama for Windows
init()


class DarkWebCrawler:
    def __init__(self):
        self.session = requests.Session()
        # Configure Tor proxy
        self.session.proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }
        self.visited_urls = set()
        self.found_urls = set()
        self.max_depth = 2

    def test_tor_connection(self):
        try:
            print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Testing Tor connection...")
            print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Checking SOCKS dependencies...")

            # Test SOCKS import
            import socks
            import socket

            # Test if Tor is running
            sock = socket.socket()
            try:
                sock.connect(("127.0.0.1", 9050))
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Tor service is running")
            except ConnectionRefusedError:
                print(
                    f"{Fore.RED}[-]{Style.RESET_ALL} Tor service is not running. Please start Tor first."
                )
                return False
            finally:
                sock.close()

            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} SOCKS dependencies found")

            response = self.session.get("http://httpbin.org/ip")
            print(
                f"{Fore.GREEN}[+]{Style.RESET_ALL} Connected through: {response.json()['origin']}"
            )
            return True
        except ImportError:
            print(
                f"{Fore.RED}[-]{Style.RESET_ALL} SOCKS dependencies missing. Please run: pip install requests[socks] PySocks"
            )
            return False
        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Tor connection failed: {str(e)}")
            return False

    def crawl_url(self, url, depth=0):
        if depth > self.max_depth or url in self.visited_urls:
            return

        try:
            print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Crawling: {url}")
            response = self.session.get(url, timeout=30)
            self.visited_urls.add(url)

            if response.status_code == 200:
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Successfully accessed: {url}")

                # Parse the HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract all links
                links = soup.find_all("a")
                for link in links:
                    href = link.get("href")
                    if href and ".onion" in href:
                        full_url = urljoin(url, href)
                        if full_url not in self.visited_urls:
                            self.found_urls.add(full_url)
                            print(
                                f"{Fore.GREEN}[+]{Style.RESET_ALL} Found new .onion link: {full_url}"
                            )
                            self.crawl_url(full_url, depth + 1)
            else:
                print(f"{Fore.RED}[-]{Style.RESET_ALL} Failed to access: {url}")

        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Error crawling {url}: {str(e)}")

    def save_results(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"onion_links_{timestamp}.txt"

        try:
            with open(filename, "w") as f:
                for url in self.found_urls:
                    f.write(url + "\n")
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Results saved to: {filename}")
        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Error saving results: {str(e)}")


def print_banner():
    banner = f"""
{Fore.CYAN}                          @@@@@@@@                @@@@@@@@         
                     @@@@@@@@@@@@@@            @@@@@@@@@@@@@@     
                 @@@@@@@@  @   @@@@@@         @@@@@  @@  @@@@@@@@ 
                 @      @@@@@@@  @@@@@@@@@@@@@@@@  @@@@@@@      @ 
                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      
                   @@@@@@     @@@@@@@@@@@@@@@@@@@@@@     @@@@@@   
                 @@@@@ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@
                @@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   @@@
                     @@@@    @@@@@@@@@@     @@@@@@@@@    @@@@     
                    @@@@     @@@@@@@@@@@    @@@@@@@@@     @@@@    
                  @@@@@  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@  
                 @@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   @@@@ 
                @@@@   @@@@     @@@@@@@@@@@@@@@@@@     @@@@   @@@@
                @@    @@@@          @@@@@@@@@@          @@@@    @@
                    @@@@@                                @@@@@     
                   @@@@                                    @@@@    
                  @@@@                                      @@@@   
                 @@@@                                        @@@@  
                @@@@                                          @@@@ 
                @@@                                            @@@{Style.RESET_ALL}
"""
    print(banner)


def menu():
    while True:
        os.system("cls")
        print_banner()

        print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Start Crawling")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Test Tor Connection")
        print(f"{Fore.RED}[3]{Style.RESET_ALL} Exit")

        choice = input(f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Select an option: ")

        if choice == "1":
            crawler = DarkWebCrawler()
            if crawler.test_tor_connection():
                start_url = input(
                    f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Enter .onion URL to start crawling: "
                )
                if ".onion" in start_url:
                    crawler.crawl_url(start_url)
                    print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Crawling completed!")
                    print(
                        f"{Fore.BLUE}[*]{Style.RESET_ALL} Found {len(crawler.found_urls)} unique .onion links"
                    )
                    crawler.save_results()
                else:
                    print(f"{Fore.RED}[-]{Style.RESET_ALL} Invalid .onion URL")
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        elif choice == "2":
            crawler = DarkWebCrawler()
            crawler.test_tor_connection()
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")

        elif choice == "3":
            print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Exiting...")
            sys.exit(0)

        else:
            print(f"\n{Fore.RED}[-]{Style.RESET_ALL} Invalid option!")
            input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to continue...")


if __name__ == "__main__":
    menu()
