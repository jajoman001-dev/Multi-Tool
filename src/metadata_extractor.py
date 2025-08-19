import os
from colorama import Fore, Style, init
from PIL import Image
from PIL.ExifTags import TAGS
import magic  # This now uses python-magic-bin
import PyPDF2
from docx import Document  # Changed this line

init(autoreset=True)


def print_banner():
    print(
        Fore.RED
        + """
                                                                                   ^                      
                                                                                 J@@M                     
                                                                        ^         @@@@^                   
                                                                     ;@@@>         J@@@                   
                                                                      ;@@@J      ;j j@@@}                 
                                                                       ^@@@O  ^J@@@@^;@@@}                
                                                                   >@@@; @@@@^;@@@@@> ;@@@O               
                                                                >j _@@@@j p@@@^;@|      @@@>              
                                                              }@@@@  @@@@j J@@@>                          
                                                          ^a@@ _@@@@;_@@@@a }@@@>                         
                                                       ^} v@@@@^;@@@@@@@@@@@ >@@@v                        
                                                     |@@@@ ^@@@@J@@@@@@@@@@@@;^@@@J                       
                                                  J@M }@@@@ _@@@@@@@@@@@@@@j    @@j                       
                                               ; v@@@@ >@@@@@@@@@@@@@@@@j                                 
                                            ^@@@@ ;@@@@v@@@@@@@@@@@@@j^                                   
                                            a@@@@@ >@@@@@@@@@@@@@@a                                       
                                            |@@@@@@@@@@@@@@@@@@J                                          
                                          |a ;@@@@@@@@@@@@@@a;                                            
                                         @@@@ ;@@@@@@@@@@@;                                               
                                        |@@@@@> @@@@@@@>                                                  
                                     }@@@pO@MJ   >pp_                                                     
                                  ;@@@a                                                                   
                               ;@@@p;                                                                     
                            >p@@M>                                                                        
                           }@@>                              
    """
        + Fore.RESET
    )


def get_file_info(file_path):
    """Get basic file information"""
    try:
        # Updated magic usage
        ms = magic.Magic(mime=True)
        file_type = ms.from_file(file_path)
        file_size = os.path.getsize(file_path)
        created_time = os.path.getctime(file_path)
        modified_time = os.path.getmtime(file_path)
        return {
            "Type": file_type,
            "Size": f"{file_size / 1024:.2f} KB",
            "Created": created_time,
            "Modified": modified_time,
        }
    except Exception as e:
        return {"Error": str(e)}


def get_gps_info(exif):
    """Extract GPS information from EXIF data"""
    if not exif:
        return None

    gps_info = {}

    try:
        if "GPSInfo" in exif:
            gps = exif["GPSInfo"]

            # Get latitude
            if 1 in gps and 2 in gps and 3 in gps:
                lat_ref = gps.get(1, "N")
                lat = gps[2]
                lat_deg = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / 3600
                if lat_ref != "N":
                    lat_deg = -lat_deg
                gps_info["Latitude"] = f"{lat_deg:.6f}°"

            # Get longitude
            if 3 in gps and 4 in gps and 5 in gps:
                lon_ref = gps.get(3, "E")
                lon = gps[4]
                lon_deg = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / 3600
                if lon_ref != "E":
                    lon_deg = -lon_deg
                gps_info["Longitude"] = f"{lon_deg:.6f}°"

            # Add Google Maps link if both lat and lon are available
            if "Latitude" in gps_info and "Longitude" in gps_info:
                lat = float(gps_info["Latitude"].strip("°"))
                lon = float(gps_info["Longitude"].strip("°"))
                gps_info["Maps Link"] = f"https://www.google.com/maps?q={lat},{lon}"

    except Exception as e:
        gps_info["Error"] = str(e)

    return gps_info if gps_info else None


def extract_image_metadata(file_path):
    """Extract metadata from image files"""
    try:
        with Image.open(file_path) as img:
            exif_data = {}
            gps_data = None

            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value

                    # Extract GPS data
                    gps_data = get_gps_info(exif_data)

            metadata = {
                "Format": img.format,
                "Mode": img.mode,
                "Size": img.size,
                "EXIF": exif_data,
            }

            if gps_data:
                metadata["GPS Location"] = gps_data

            return metadata
    except Exception as e:
        return {"Error": str(e)}


def extract_pdf_metadata(file_path):
    """Extract metadata from PDF files"""
    try:
        with open(file_path, "rb") as file:
            pdf = PyPDF2.PdfReader(file)
            info = pdf.metadata
            return {
                "Pages": len(pdf.pages),
                "Author": info.get("/Author", "N/A"),
                "Creator": info.get("/Creator", "N/A"),
                "Producer": info.get("/Producer", "N/A"),
                "Subject": info.get("/Subject", "N/A"),
                "Title": info.get("/Title", "N/A"),
                "Creation Date": info.get("/CreationDate", "N/A"),
            }
    except Exception as e:
        return {"Error": str(e)}


def extract_docx_metadata(file_path):
    """Extract metadata from DOCX files"""
    try:
        doc = Document(file_path)  # Changed this line
        core_properties = doc.core_properties
        return {
            "Author": core_properties.author,
            "Created": core_properties.created,
            "Modified": core_properties.modified,
            "Last Modified By": core_properties.last_modified_by,
            "Title": core_properties.title,
            "Subject": core_properties.subject,
        }
    except Exception as e:
        return {"Error": str(e)}


def print_metadata(metadata, indent=""):
    """Print metadata in a formatted way"""
    for key, value in metadata.items():
        if isinstance(value, dict):
            print(f"{indent}{Fore.GREEN}{key}:{Fore.RESET}")
            print_metadata(value, indent + "  ")
        else:
            print(f"{indent}{Fore.GREEN}{key}:{Fore.RESET} {value}")


def metadata_extractor():
    while True:
        print("\n")
        print(f"{Fore.YELLOW}Enter the file path to extract metadata:{Fore.RESET}")
        file_path = input().strip()

        # Remove quotes if present
        file_path = file_path.strip("\"'")

        try:
            if not os.path.exists(file_path):
                print(
                    f"{Fore.RED}Error: File not found at path: {file_path}{Fore.RESET}"
                )
                continue

            print(f"\n{Fore.CYAN}Extracting metadata...{Fore.RESET}\n")

            # Get basic file info
            metadata = {"Basic Info": get_file_info(file_path)}

            # Extract format-specific metadata
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
                metadata["Image Metadata"] = extract_image_metadata(file_path)
            elif file_extension == ".pdf":
                metadata["PDF Metadata"] = extract_pdf_metadata(file_path)
            elif file_extension == ".docx":
                metadata["DOCX Metadata"] = extract_docx_metadata(file_path)
            else:
                print(
                    f"{Fore.YELLOW}Warning: Detailed metadata extraction not supported for this file type{Fore.RESET}"
                )

            print_metadata(metadata)

        except Exception as e:
            print(f"{Fore.RED}Error occurred: {str(e)}{Fore.RESET}")

        while True:
            choice = input(
                f"\n{Fore.YELLOW}Do you want to scan another file? (y/n):{Fore.RESET} "
            ).lower()
            if choice in ["y", "n"]:
                break
            print(f"{Fore.RED}Please enter 'y' or 'n'{Fore.RESET}")

        if choice == "n":
            print(f"{Fore.GREEN}Goodbye!{Fore.RESET}")
            break


if __name__ == "__main__":
    print_banner()
    metadata_extractor()
