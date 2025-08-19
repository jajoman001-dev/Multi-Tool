# All rights reserved.
# This code is provided for educational purposes only.
# Use it at your own risk.
# Created by: Violett
# Version: 2.0
# Unauthorized copying or redistribution of this code is strictly prohibited.
# Skidding (copying and using code without understanding it) is not permitted.
# Modifying or redistributing this code without the authors' permission is forbidden.
# For support or inquiries, contact: 5gproxy on Discord.

import os
import subprocess
from colorama import init, Fore, Style
import platform

init(autoreset=True)
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")



def gradient_color(y, height, start_rgb=(0, 0, 50), end_rgb=(0, 255, 255)):
    """Generate a color for the gradient based on vertical position"""
    factor = y / height
    r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * factor
    g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * factor
    b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * factor
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"



def horizontal_gradient_color(x, width, start_rgb=(0, 0, 50), end_rgb=(0, 255, 255)):
    """Generate a color for horizontal gradient based on position"""
    factor = x / width
    r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * factor
    g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * factor
    b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * factor
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"



def print_horizontal_gradient_text(text, return_str=False):
    """Print text with horizontal gradient"""
    result = ""
    for i, char in enumerate(text):
        color = horizontal_gradient_color(i, len(text))
        result += color + char
    result += Style.RESET_ALL

    if return_str:
        return result
    print(result)



def print_gradient_text(text, y, height, padding=0):
    """Print text with gradient color and padding"""
    color = gradient_color(y, height)
    print(" " * padding + color + text + Style.RESET_ALL)






def print_banner():
    banner_lines =[
        "██████╗ ███████╗███╗   ██╗████████╗ █████╗  ██████╗ ██████╗ ███╗   ██╗",
        "██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║",
        "██████╔╝█████╗  ██╔██╗ ██║   ██║   ███████║██║     ██║   ██║██╔██╗ ██║",
        "██╔═══╝ ██╔══╝  ██║╚██╗██║   ██║   ██╔══██║██║     ██║   ██║██║╚██╗██║",
        "██║     ███████╗██║ ╚████║   ██║   ██║  ██║╚██████╗╚██████╔╝██║ ╚████║",
        "╚═╝     ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═════╝ ╚═════╝ ╚═╝  ╚╝  ╚═══╝",
]
    






    terminal_width = os.get_terminal_size().columns
    banner_width = len(banner_lines[0])
    padding = (terminal_width - banner_width) // 2

    print()  
    for i, line in enumerate(banner_lines):
        print_gradient_text(line, i, len(banner_lines) + 1, padding)
    print()


def run_tool(tool_path):
    try:
        clear_screen()
        subprocess.run(["python", tool_path], shell=True)
        input(f"\n{Fore.YELLOW}[*] Press Enter to return to menu...{Fore.RESET}")
        clear_screen()
    except Exception as e:
        print(f"{Fore.RED}[!] Error running tool: {e}")
        input(f"{Fore.YELLOW}[*] Press Enter to continue...{Fore.RESET}")
        clear_screen()


def main_menu():
    tools = {
       
        "01": {"name": "Phone Number OSINT", "path": "src/number_osint.py"},
        "02": {"name": "IP Geolocation", "path": "src/ip_geolocation.py"},
        "03": {"name": "Email OSINT", "path": "src/email_osint.py"},
        "04": {"name": "Domain Recon", "path": "src/domain_recon.py"},
        "05": {"name": "Social Media Scraper", "path": "src/social_scraper.py"},
        "06": {"name": "Metadata Extractor", "path": "src/metadata_extractor.py"},
        "07": {"name": "Port Scanner", "path": "src/port_scanner.py"},
        "08": {"name": "Webhook Spammer", "path": "src/webhook_spammer.py"},
        "09": {"name": "Discord Raid", "path": "src/server_raid.py"},
        "10": {"name": "IP Pinger", "path": "src/ip_pinger.py"},
        "11": {"name": "Paysafecard Generator", "path": "src/paysafe_gen.py"},
        "12": {"name": "Nitro Generator", "path": "src/nitro_gen.py"},
        "13": {"name": "DNS Enumeration", "path": "src/dns_enum.py"},
        "14": {"name": "Subdomain Scanner", "path": "src/subdm_scan.py"},
        "15": {"name": "Dark Web Crawler", "path": "src/dw_crawler.py"},
        "16": {"name": "Database Scanner", "path": "src/db_scanner.py"},
        "17": {
            "name": "Network Traffic Analyzer",
            "path": "src/ntwrk_trfc_analyzer.py",
        },
        "18": {"name": "Malware Analysis", "path": "src/malware_analysis.py"},
        "19": {"name": "DDoS Attack", "path": "src/ddos_tool.py"},
        "20": {"name": "Phishing Tool [SOON!]", "path": "src/phishing_tool.py"},
        "21": {
            "name": "RAT (REMOTE ACCESS TROJAN) [SOON!]",
            "path": "src/keylogger.py",
        },
        "00": {"name": "Exit", "path": None},
    }

  
    single_digit_tools = {k.lstrip("0"): v for k, v in tools.items()}
    tools.update(single_digit_tools)
    display_keys = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "00",
    ]

    while True:
        clear_screen()
        print_banner()

        total_width = os.get_terminal_size().columns
        column_width = total_width // 3
        padding = " " * 2

        all_tools = display_keys[:-1]  
        column_size = len(all_tools) // 3 + (1 if len(all_tools) % 3 > 0 else 0)
        col1 = all_tools[:column_size]
        col2 = all_tools[column_size : column_size * 2]
        col3 = all_tools[column_size * 2 :]

       
        menu_height = len(display_keys) // 3 + 4  
        current_line = 0

        for i in range(max(len(col1), len(col2), len(col3))):
            line = []
            for col in [col1, col2, col3]:
                if i < len(col):
                    tool = f"[{col[i]}] {tools[col[i]]['name']}"
                    line.append(tool.ljust(column_width))
                else:
                    line.append(" ".ljust(column_width))
            if any(col[i] for col in [col1, col2, col3] if i < len(col)):
                print_gradient_text(
                    f"{padding}{''.join(line).rstrip()}", current_line, menu_height
                )
                current_line += 1

        print()
        current_line += 1
        exit_text = "[00] Exit"
        padding = (total_width - len(exit_text)) // 2
        print_gradient_text(exit_text, current_line, menu_height, padding)
        print()

        current_line += 2
        prompt1 = f"┌──(admin joshy@pentacon)"
        prompt2 = "└─$ "

        print_horizontal_gradient_text(prompt1)
        
        choice = input(print_horizontal_gradient_text(prompt2, return_str=True))

        if len(choice) == 1 and choice.isdigit():
            choice = f"0{choice}"

        if choice in tools:
            if choice == "00":  
                clear_screen()
                break

            tool_info = tools[choice]
            if "[SOON!]" in tool_info["name"]:
                print(f"\n{Fore.RED}[!] Tool not implemented yet: {tool_info['name']}")
                input(f"\n{Fore.YELLOW}[*] Press Enter to continue...{Fore.RESET}")
            elif tool_info["path"] and os.path.exists(tool_info["path"]):
                run_tool(tool_info["path"])
            else:
                print(f"\n{Fore.RED}[!] Tool file not found: {tool_info['path']}")
                input(f"\n{Fore.YELLOW}[*] Press Enter to continue...{Fore.RESET}")
        else:
            print(f"\n{Fore.RED}[!] Invalid option!")
            input(f"\n{Fore.YELLOW}[*] Press Enter to continue...{Fore.RESET}")


if __name__ == "__main__":
    main_menu()
