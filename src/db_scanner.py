import os
import tkinter as tk
from tkinter import filedialog, messagebox
from colorama import init, Fore, Style
import time

# Initialize colorama for Windows
init()


class DatabaseScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.search_results = []

    def select_source(self):
        """Let user choose between file or directory scanning"""
        print(f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Select scan type:")
        print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Scan single file")
        print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Scan directory")
        print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Exit")

        choice = input(f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Enter choice (1/2): ")

        if choice == "1":
            return self.select_file()
        elif choice == "2":
            return self.select_directory()
        elif choice == "0":
            print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Exiting...")
            exit
        else:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Invalid choice")
            return None, None

    def select_file(self):
        """Open file explorer for file selection"""
        file_path = filedialog.askopenfilename(
            title="Select file to scan",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            return "file", file_path
        return None, None

    def select_directory(self):
        """Open file explorer for directory selection"""
        dir_path = filedialog.askdirectory(title="Select directory to scan")
        if dir_path:
            return "dir", dir_path
        return None, None

    def scan_file(self, file_path, search_term):
        """Scan single file for search term"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    if search_term.lower() in line.lower():
                        # Store only the relevant portion of the line containing the match
                        start_idx = line.lower().find(search_term.lower())
                        context = line.strip()[
                            max(0, start_idx - 40) : start_idx + len(search_term) + 40
                        ]
                        if start_idx > 40:
                            context = f"...{context}"
                        if len(line.strip()) > start_idx + len(search_term) + 40:
                            context = f"{context}..."
                        self.search_results.append((file_path, line_num, context))
        except Exception as e:
            print(
                f"{Fore.RED}[-]{Style.RESET_ALL} Error scanning {file_path}: {str(e)}"
            )

    def scan_directory(self, dir_path, search_term):
        """Recursively scan directory for search term"""
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".txt"):  # Only scan text files
                    file_path = os.path.join(root, file)
                    print(f"{Fore.BLUE}[*]{Style.RESET_ALL} Scanning: {file_path}")
                    self.scan_file(file_path, search_term)

    def start_scan(self):
        """Main scanning function"""
        print_banner()
        scan_type, path = self.select_source()

        if not path:
            return

        search_term = input(f"\n{Fore.BLUE}[?]{Style.RESET_ALL} Enter search term: ")
        if not search_term:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} No search term provided")
            return

        start_time = time.time()
        print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Starting scan...")

        if scan_type == "file":
            self.scan_file(path, search_term)
        else:
            self.scan_directory(path, search_term)

        duration = time.time() - start_time

        # Display results
        if self.search_results:
            print(
                f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Found {len(self.search_results)} matches:"
            )
            current_file = None
            for file_path, line_num, context in self.search_results:
                if current_file != file_path:
                    print(f"\n{Fore.YELLOW}[*]{Style.RESET_ALL} File: {file_path}")
                    current_file = file_path
                highlighted_context = context.replace(
                    search_term, f"{Fore.GREEN}{search_term}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.BLUE}[>]{Style.RESET_ALL} Line {line_num}: {highlighted_context}"
                )
        else:
            print(f"\n{Fore.YELLOW}[!]{Style.RESET_ALL} No matches found")

        print(
            f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Scan completed in {duration:.2f} seconds"
        )
        input(
            f"\n{Fore.BLUE}[*]{Style.RESET_ALL} Press Enter to exit..."
        )  # Added pause


def print_banner():
    banner = f"""
{Fore.CYAN}
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
{Style.RESET_ALL}"""
    print(banner)


def main():
    scanner = DatabaseScanner()
    scanner.start_scan()


if __name__ == "__main__":
    main()
