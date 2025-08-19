from scapy.all import sniff, conf
import os
import time
from datetime import datetime
from colorama import init, Fore, Style
import threading
import json
import socket

# Initialize colorama for Windows
init()


class NetworkAnalyzer:
    def __init__(self):
        self.packets = []
        self.is_running = False
        self.current_interface = None
        self.start_time = None

    def get_available_interfaces(self):
        """Get list of available network interfaces"""
        interfaces = []
        for iface in conf.ifaces.values():
            interfaces.append(iface.name)
        return interfaces

    def packet_callback(self, packet):
        """Callback function for each captured packet"""
        try:
            packet_info = {
                "timestamp": time.time(),
                "size": len(packet),
                "type": "Unknown",
            }

            # Check if packet has IP layer
            if packet.haslayer("IP"):
                ip_layer = packet.getlayer("IP")
                packet_info.update(
                    {
                        "src_ip": ip_layer.src,
                        "dst_ip": ip_layer.dst,
                        "protocol": ip_layer.proto,
                    }
                )

                # Try to resolve hostnames with timeout
                try:
                    socket.setdefaulttimeout(1)  # 1 second timeout
                    src_host = socket.gethostbyaddr(ip_layer.src)[0]
                    dst_host = socket.gethostbyaddr(ip_layer.dst)[0]
                except:
                    src_host = "Unknown"
                    dst_host = "Unknown"

                packet_info.update({"src_host": src_host, "dst_host": dst_host})

                # TCP Layer analysis
                if packet.haslayer("TCP"):
                    tcp_layer = packet.getlayer("TCP")
                    packet_info["type"] = "TCP"
                    packet_info["src_port"] = tcp_layer.sport
                    packet_info["dst_port"] = tcp_layer.dport

                    # TCP Flag analysis
                    flags = tcp_layer.flags
                    if flags & 0x02:  # SYN
                        packet_info["type"] = "TCP-SYN"
                    elif flags & 0x10:  # ACK
                        packet_info["type"] = "TCP-ACK"
                    elif flags & 0x01:  # FIN
                        packet_info["type"] = "TCP-FIN"
                    elif flags & 0x04:  # RST
                        packet_info["type"] = "TCP-RST"

                # UDP Layer analysis
                elif packet.haslayer("UDP"):
                    udp_layer = packet.getlayer("UDP")
                    packet_info["type"] = "UDP"
                    packet_info["src_port"] = udp_layer.sport
                    packet_info["dst_port"] = udp_layer.dport

                # ICMP Layer analysis
                elif packet.haslayer("ICMP"):
                    packet_info["type"] = "ICMP"

            # ARP Layer analysis
            elif packet.haslayer("ARP"):
                arp_layer = packet.getlayer("ARP")
                packet_info.update(
                    {
                        "type": "ARP",
                        "src_ip": arp_layer.psrc,
                        "dst_ip": arp_layer.pdst,
                        "src_mac": arp_layer.hwsrc,
                        "dst_mac": arp_layer.hwdst,
                    }
                )

            # Store packet info
            self.packets.append(packet_info)

            # Color selection based on packet type
            color = {
                "TCP": Fore.GREEN,
                "TCP-SYN": Fore.YELLOW,
                "TCP-ACK": Fore.BLUE,
                "TCP-FIN": Fore.MAGENTA,
                "TCP-RST": Fore.RED,
                "UDP": Fore.CYAN,
                "ICMP": Fore.WHITE,
                "ARP": Fore.YELLOW,
                "Unknown": Fore.RED,
            }.get(packet_info["type"], Fore.WHITE)

            # Format and print packet info
            if packet_info["type"] == "ARP":
                print(
                    f"{color}[{packet_info['type']}]{Style.RESET_ALL} "
                    f"{packet_info['src_ip']} ({packet_info['src_mac']}) -> "
                    f"{packet_info['dst_ip']} ({packet_info['dst_mac']})"
                )
            elif "src_ip" in packet_info:
                port_info = (
                    f":{packet_info.get('src_port', '')} -> :{packet_info.get('dst_port', '')}"
                    if "src_port" in packet_info
                    else ""
                )
                print(
                    f"{color}[{packet_info['type']}]{Style.RESET_ALL} "
                    f"{packet_info['src_ip']} ({packet_info.get('src_host', 'Unknown')}) {port_info} -> "
                    f"{packet_info['dst_ip']} ({packet_info.get('dst_host', 'Unknown')}) "
                    f"Size: {packet_info['size']} bytes"
                )

        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Error processing packet: {str(e)}")

    def save_results(self):
        """Save captured packets to file"""
        if not os.path.exists("results"):
            os.makedirs("results")
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Created results directory")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/network_capture_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(self.packets, f, indent=4)
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Results saved to: {filename}")
        except Exception as e:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Error saving results: {str(e)}")

    def start_capture(self, interface):
        """Start packet capture on selected interface"""
        self.is_running = True
        self.current_interface = interface
        self.start_time = time.time()

        print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Starting capture on {interface}")
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to stop capturing...")

        # Start packet capture in a separate thread
        capture_thread = threading.Thread(target=self._capture_packets)
        capture_thread.start()

        # Wait for Enter key
        input()
        self.is_running = False
        capture_thread.join()

        duration = time.time() - self.start_time
        print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Capture stopped")
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Duration: {duration:.2f} seconds")
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Packets captured: {len(self.packets)}")

        save = input(
            f"\n{Fore.YELLOW}[?]{Style.RESET_ALL} Save results? (y/n): "
        ).lower()
        if save == "y":
            self.save_results()

    def _capture_packets(self):
        """Internal method to capture packets"""
        sniff(
            iface=self.current_interface,
            prn=self.packet_callback,
            stop_filter=lambda _: not self.is_running,
        )


def print_banner():
    banner = f"""
{Fore.CYAN}
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
{Style.RESET_ALL}"""
    print(banner)


def main():
    # Check for Npcap/WinPcap
    try:
        from scapy.arch.windows import get_windows_if_list

        interfaces = get_windows_if_list()
        if not interfaces:
            raise ImportError
    except ImportError:
        print(f"{Fore.RED}[-]{Style.RESET_ALL} Npcap/WinPcap not found!")
        print(
            f"{Fore.YELLOW}[!]{Style.RESET_ALL} Please install Npcap from: https://npcap.com/#download"
        )
        input(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to exit...")
        return

    analyzer = NetworkAnalyzer()
    print_banner()

    # Get available interfaces
    interfaces = analyzer.get_available_interfaces()

    print(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Available interfaces:")
    for i, iface in enumerate(interfaces, 1):
        print(f"{Fore.GREEN}[{i}]{Style.RESET_ALL} {iface}")

    while True:
        try:
            choice = int(
                input(
                    f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Select interface (1-{len(interfaces)}): "
                )
            )
            if 1 <= choice <= len(interfaces):
                selected_interface = interfaces[choice - 1]
                analyzer.start_capture(selected_interface)
                break
            else:
                print(f"{Fore.RED}[-]{Style.RESET_ALL} Invalid choice")
        except ValueError:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Please enter a number")


if __name__ == "__main__":
    main()
