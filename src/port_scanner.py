import socket
import threading
from queue import Queue, Empty
import queue
from datetime import datetime
import ipaddress
from colorama import Fore, Style, init
import time

init(autoreset=True)


def print_banner():
    print(
        Fore.CYAN
        + """
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
        + Fore.RESET
    )


def check_port(target, port, timeout=0.5):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None


def get_service_name(port):
    """Get service name for a port"""
    try:
        service = socket.getservbyport(port)
        return service
    except:
        return "unknown"


def worker(target, port_queue, open_ports, thread_id, progress, port_timeout):
    """Worker thread to check ports"""
    while True:
        try:
            port = port_queue.get_nowait()
            if port is None:
                port_queue.task_done()
                break

            result = check_port(target, port, timeout=port_timeout)

            if result:
                open_ports.append(result)
                with threading.Lock():
                    print(
                        f"\n{Fore.GREEN}[+] Port {port}/tcp is open - {get_service_name(port)}{Fore.RESET}"
                    )

            with threading.Lock():
                progress["ports_scanned"] += 1

            port_queue.task_done()

        except queue.Empty:
            break


def update_progress_bar(progress):
    """Update progress bar display"""
    percentage = (progress["ports_scanned"] / progress["total_ports"]) * 100
    bar = "=" * int(percentage // 2)
    spaces = " " * (50 - len(bar))
    print(
        f"\r{Fore.CYAN}[*] Progress: [{bar}{spaces}] {percentage:.1f}% ({progress['ports_scanned']}/{progress['total_ports']}){Fore.RESET}",
        flush=True,
        end="",
    )


def port_scanner():
    thread_count = 100  # Number of threads to use

    print(f"\n{Fore.YELLOW}Enter target IP or hostname:{Fore.RESET}")
    target = input().strip()

    try:
        # Validate IP address or resolve hostname
        if not target.replace(".", "").isnumeric():
            target_ip = socket.gethostbyname(target)
        else:
            ipaddress.ip_address(target)
            target_ip = target

        print(f"\n{Fore.YELLOW}Select scan type:")
        print(f"{Fore.CYAN}1) Quick Scan (top 100 ports)")
        print(f"2) Common Scan (top 10000 ports)")
        print(f"3) Full Scan (all ports)")
        print(f"4) Custom port range{Fore.RESET}")

        scan_type = input().strip()

        if scan_type == "1":
            ports = [
                20,
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                111,
                135,
                139,
                143,
                443,
                445,
                993,
                995,
                1723,
                3306,
                3389,
                5500,
                5900,
                8080,
            ]
            thread_count = len(ports)  # One thread per port
            port_timeout = 0.2  # Very short timeout for quick scan
            max_wait_time = 5  # Maximum 5 seconds total for quick scan
        elif scan_type == "2":
            ports = range(1, 10001)
        elif scan_type == "3":
            ports = range(1, 65536)
        elif scan_type == "4":
            start_port = int(input(f"{Fore.YELLOW}Start port:{Fore.RESET} "))
            end_port = int(input(f"{Fore.YELLOW}End port:{Fore.RESET} "))
            ports = range(start_port, end_port + 1)
        else:
            print(f"{Fore.RED}Invalid option!{Fore.RESET}")
            return

        total_ports = (
            len(list(ports)) if hasattr(ports, "__len__") else ports.stop - ports.start
        )
        progress = {"ports_scanned": 0, "total_ports": total_ports}

        print(f"\n{Fore.CYAN}[*] Target: {target_ip}")
        print(f"[*] Total ports to scan: {total_ports}")
        print(f"[*] Threads: {thread_count}")
        print(
            f"[*] Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}"
        )
        print(f"\n{Fore.YELLOW}[*] Scanning in progress...{Fore.RESET}\n")

        # Create a queue with a maximum size
        port_queue = Queue(maxsize=65536)
        open_ports = []
        threads = []

        # Fill queue with ports
        for port in ports:
            port_queue.put(port)

        # Add sentinel values for threads
        for _ in range(thread_count):
            port_queue.put(None)

        # Set timeouts
        max_wait_time = 600  # 10 minutes for total scan
        port_timeout = 1.0  # 1 second per port connection attempt

        # Create threads with the port_timeout
        for i in range(thread_count):
            thread = threading.Thread(
                target=worker,
                args=(target_ip, port_queue, open_ports, i, progress, port_timeout),
                daemon=True,
            )
            thread.start()
            threads.append(thread)

        try:
            # Start progress update thread
            def update_progress():
                while progress["ports_scanned"] < progress["total_ports"]:
                    update_progress_bar(progress)
                    time.sleep(0.1)

            progress_thread = threading.Thread(target=update_progress, daemon=True)
            progress_thread.start()

            # Wait for queue to complete
            port_queue.join()

            # Ensure progress shows 100%
            progress["ports_scanned"] = progress["total_ports"]
            update_progress_bar(progress)

            # Clear screen line and show results
            print("\n")
            # Sort and display results
            open_ports.sort()

            print(f"\n{Fore.GREEN}[+] Scan completed!")
            print(f"[+] Total ports scanned: {progress['ports_scanned']}")
            print(f"[+] Open ports found: {len(open_ports)}{Fore.RESET}")

            if open_ports:
                print(f"\n{Fore.CYAN}[*] Open ports on {target_ip}:{Fore.RESET}")
                for port in open_ports:
                    service = get_service_name(port)
                    print(f"{Fore.GREEN}[+] Port {port}/tcp\t{service}{Fore.RESET}")

            # For quick scan, return immediately
            if scan_type == "1":
                return

            # Option to save results
            save = input(
                f"\n{Fore.YELLOW}Save results to file? (y/n):{Fore.RESET} "
            ).lower()
            if save == "y":
                filename = f"port_scan_{target_ip}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, "w") as f:
                    f.write(f"Port Scan Results for {target_ip}\n")
                    f.write(
                        f"Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )
                    if open_ports:
                        for port in open_ports:
                            service = get_service_name(port)
                            f.write(f"Port {port}/tcp\t{service}\n")
                    else:
                        f.write("No open ports found\n")
                print(f"{Fore.GREEN}Results saved to {filename}{Fore.RESET}")

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Scan interrupted by user")
            print(
                f"[!] Ports scanned before interruption: {progress['ports_scanned']}{Fore.RESET}"
            )
        except Exception as e:
            print(f"\n{Fore.RED}[!] An error occurred: {str(e)}{Fore.RESET}")

    except socket.gaierror:
        print(f"{Fore.RED}Could not resolve hostname{Fore.RESET}")
    except ValueError:
        print(f"{Fore.RED}Invalid IP address{Fore.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Scan interrupted by user{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}{Fore.RESET}")


if __name__ == "__main__":
    print_banner()
    while True:
        port_scanner()
        if (
            input(f"\n{Fore.YELLOW}Scan another target? (y/n):{Fore.RESET} ").lower()
            != "y"
        ):
            break
