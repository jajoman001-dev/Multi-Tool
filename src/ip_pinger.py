import os
import platform
import socket
import statistics
import subprocess
import time
from colorama import init, Fore, Style, AnsiToWin32
from datetime import datetime

# Initialize colorama with Windows support
init(wrap=True)


def print_banner():
    banner = """
                                                 @@@@@@@@@@@@@@@@@@@                                 
                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                         
                                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    
                                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                
                             @@@@@@@@@@@@@@@@@@                       @@@@@@@@@@@@@@@@@@             
                           @@@@@@@@@@@@@@                                   @@@@@@@@@@@@@@@          
                        @@@@@@@@@@@@@              @@@@@@@@@@@@@@@              @@@@@@@@@@@@@        
                       @@@@@@@@@@@          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@          @@@@@@@@@@@       
                       @@@@@@@@         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         @@@@@@@@       
                        @@@@@        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        @@@@@        
                                  @@@@@@@@@@@@@@@                   @@@@@@@@@@@@@@@                  
                                @@@@@@@@@@@@@                           @@@@@@@@@@@@@                
                               @@@@@@@@@@            @@@@@@@@@@@            @@@@@@@@@@               
                                @@@@@@@         @@@@@@@@@@@@@@@@@@@@@         @@@@@@@                
                                            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@                            
                                          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                          
                                         @@@@@@@@@@@             @@@@@@@@@@@                         
                                        @@@@@@@@@                   @@@@@@@@@                        
                                         @@@@@@        @@@@@@@        @@@@@@                         
                                                    @@@@@@@@@@@@@                                    
                                                   @@@@@@@@@@@@@@@                                   
                                                  @@@@@@@@@@@@@@@@@                                  
                                                  @@@@@@@@@@@@@@@@@                                  
                                                   @@@@@@@@@@@@@@@                                   
                                                    @@@@@@@@@@@@@                                    
                                                       @@@@@@@  
    """
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 120}{Style.RESET_ALL}\n")


def resolve_host(target):
    """Resolve hostname to IP address"""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def ping(target, count=4):
    """Ping target and return results"""
    system = platform.system().lower()

    # Simple command setup
    if system == "windows":
        command = ["ping", "-n", str(count), target]
    else:
        command = ["ping", "-c", str(count), target]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="cp850",  # Changed to Windows codepage
            errors="replace",
        )

        output, _ = process.communicate()

        results = {
            "transmitted": count,
            "received": 0,
            "times": [],
            "min_time": 0,
            "avg_time": 0,
            "max_time": 0,
            "address": "",  # Add resolved address storage
        }

        # Parse each line
        for line in output.splitlines():
            # Get resolved address
            if "Ping wird ausgefuhrt fur" in line:
                try:
                    results["address"] = line.split("[")[1].split("]")[0]
                except:
                    results["address"] = target

            # Count received packets and times
            if "Antwort von" in line:
                print(f"{Fore.GREEN}[+] {line.strip()}{Style.RESET_ALL}")
                results["received"] += 1
                if "Zeit=" in line:
                    try:
                        time = int(line.split("Zeit=")[1].split("ms")[0].strip())
                        results["times"].append(time)
                    except (IndexError, ValueError):
                        pass
            elif "Zeituberschreitung" in line or "Zielhost nicht erreichbar" in line:
                print(f"{Fore.RED}[-] {line.strip()}{Style.RESET_ALL}")

        # Calculate stats if we have times
        if results["times"]:
            results["min_time"] = min(results["times"])
            results["max_time"] = max(results["times"])
            results["avg_time"] = sum(results["times"]) / len(results["times"])

        return results

    except Exception as e:
        print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        return None


def main():
    print_banner()

    while True:
        print(
            f"{Fore.YELLOW}Enter target IP or hostname (or 'exit' to quit):{Style.RESET_ALL}"
        )
        target = input().strip()

        if target.lower() == "exit":
            break

        # Resolve hostname if needed
        if not target.replace(".", "").isnumeric():
            print(f"\n{Fore.CYAN}[*] Resolving hostname...{Style.RESET_ALL}")
            ip = resolve_host(target)
            if not ip:
                print(f"{Fore.RED}[!] Could not resolve hostname{Style.RESET_ALL}")
                continue
            print(f"{Fore.GREEN}[+] Resolved to: {ip}{Style.RESET_ALL}")
        else:
            ip = target

        print(
            f"\n{Fore.CYAN}[*] Starting ping test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}[*] Target: {target} ({ip}){Style.RESET_ALL}\n")

        results = ping(ip)

        if results:
            print(
                f"\n{Fore.CYAN}[*] Ping-Statistik für {results.get('address', ip)}:{Style.RESET_ALL}"
            )
            transmitted = results["transmitted"]
            received = results["received"]
            lost = transmitted - received
            loss_percentage = (lost / transmitted * 100) if transmitted > 0 else 0

            print(
                f"{Fore.GREEN}    Pakete: Gesendet = {transmitted}, "
                f"Empfangen = {received}, Verloren = {lost}"
            )
            print(f"    ({loss_percentage:.0f}% Verlust){Style.RESET_ALL}")

            if results["times"]:
                print(f"{Fore.GREEN}Ca. Zeitangaben in Millisek.:")
                print(
                    f"    Minimum = {results['min_time']}ms, "
                    f"Maximum = {results['max_time']}ms, "
                    f"Mittelwert = {results['avg_time']}ms{Style.RESET_ALL}"
                )

        print(f"\n{Fore.BLUE}{'=' * 120}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
