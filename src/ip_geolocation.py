import requests
import json
import os
from datetime import datetime
from colorama import Fore, init
import socket
from urllib.parse import quote_plus
import geocoder  # Add this import

init(autoreset=True)


def print_header():
    ascii_art = rf"""
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
    print(Fore.GREEN + ascii_art)
    print(Fore.MAGENTA + "-" * 120 + "\n")
    print(Fore.BLUE + "Starting... Please provide the necessary inputs.\n")


def save_to_file(data):
    """Save query results to JSON file"""
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    filename = f"query_{data.get('ip')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(results_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(Fore.GREEN + f"Results saved to {filepath}")
    except IOError as e:
        print(Fore.RED + f"Error saving file: {str(e)}")


def get_detailed_location(lat, lon):
    """Get detailed location information including street name"""
    try:
        headers = {"User-Agent": "IP Geolocation Tool"}
        g = geocoder.osm([lat, lon], method="reverse", headers=headers)
        if g.ok:
            return {
                "street": g.street or "N/A",
                "house_number": g.housenumber or "N/A",
                "postal": g.postal or "N/A",
                "neighborhood": g.neighborhood or "N/A",
                "district": g.district or "N/A",
                "county": g.county or "N/A",
            }
    except Exception:
        pass
    return None


def get_ip_geolocation(ip_address):
    """Get geolocation data using free services"""
    try:
        # Try multiple free services
        urls = [
            f"http://ip-api.com/json/{ip_address}",
            f"https://ipapi.co/{ip_address}/json/",
            f"https://freegeoip.app/json/{ip_address}",
        ]

        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()

                    # Get basic location data
                    result = {
                        "ip": ip_address,
                        "country_name": data.get("country") or data.get("country_name"),
                        "state_prov": data.get("regionName")
                        or data.get("region")
                        or data.get("state"),
                        "city": data.get("city"),
                        "latitude": data.get("lat") or data.get("latitude"),
                        "longitude": data.get("lon") or data.get("longitude"),
                        "isp": data.get("isp") or data.get("org"),
                        "timezone": data.get("timezone"),
                        "country_code": data.get("countryCode")
                        or data.get("country_code"),
                        "zip_code": data.get("zip") or data.get("postal"),
                        "asn": data.get("as"),
                        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    # Get detailed location if coordinates are available
                    if result["latitude"] and result["longitude"]:
                        detailed = get_detailed_location(
                            result["latitude"], result["longitude"]
                        )
                        if detailed:
                            result.update(detailed)

                    return result
            except:
                continue

        raise Exception("All geolocation services failed")

    except Exception as e:
        print(Fore.RED + f"Error fetching data: {str(e)}")
        return None


def send_to_discord(webhook_url, data):
    """Format and send data to Discord webhook"""
    if not data:
        return False

    google_maps_url = (
        f"https://www.google.com/maps?q={data.get('latitude')},{data.get('longitude')}"
    )
    osm_maps_url = f"https://www.openstreetmap.org/?mlat={data.get('latitude')}&mlon={data.get('longitude')}&zoom=12"

    # Add new fields for detailed location
    additional_fields = []
    if data.get("street"):
        additional_fields.extend(
            [
                {"name": "Street", "value": f"`{data.get('street')}`", "inline": True},
                {
                    "name": "House Number",
                    "value": f"`{data.get('house_number')}`",
                    "inline": True,
                },
                {
                    "name": "Neighborhood",
                    "value": f"`{data.get('neighborhood')}`",
                    "inline": True,
                },
                {
                    "name": "District",
                    "value": f"`{data.get('district')}`",
                    "inline": True,
                },
                {"name": "County", "value": f"`{data.get('county')}`", "inline": True},
            ]
        )

    message = {
        "embeds": [
            {
                "title": "IP Geolocation Results",
                "color": 3447003,
                "fields": [
                    {
                        "name": "IP Address",
                        "value": f"`{data.get('ip')}`",
                        "inline": True,
                    },
                    {
                        "name": "Country",
                        "value": f"`{data.get('country_name')} ({data.get('country_code')})`",
                        "inline": True,
                    },
                    {
                        "name": "Region",
                        "value": f"`{data.get('state_prov')}`",
                        "inline": True,
                    },
                    {"name": "City", "value": f"`{data.get('city')}`", "inline": True},
                    {
                        "name": "Postal Code",
                        "value": f"`{data.get('zip_code') or 'N/A'}`",
                        "inline": True,
                    },
                    {
                        "name": "ISP/Organization",
                        "value": f"`{data.get('isp') or 'N/A'}`",
                        "inline": True,
                    },
                    {
                        "name": "ASN",
                        "value": f"`{data.get('asn') or 'N/A'}`",
                        "inline": True,
                    },
                    {
                        "name": "Timezone",
                        "value": f"`{data.get('timezone') or 'N/A'}`",
                        "inline": True,
                    },
                    {
                        "name": "Maps",
                        "value": f"[Google]({google_maps_url}) | [OpenStreetMap]({osm_maps_url})",
                        "inline": True,
                    },
                ]
                + additional_fields,
                "footer": {
                    "text": f"Query Time: {data.get('query_time')} • By xtx & Elio"
                },
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        print(Fore.GREEN + "Results sent to Discord successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to send to Discord: {str(e)}")
        return False


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    clear_terminal()
    print_header()

    while True:
        ip_address = input(Fore.CYAN + "Enter the IP address: ").strip()

        if not ip_address:
            print(Fore.RED + "You must enter an IP address.")
            continue

        geolocation_data = get_ip_geolocation(ip_address)

        if geolocation_data:
            use_webhook = (
                input(Fore.YELLOW + "Send results to Discord webhook? (y/n): ").lower()
                == "y"
            )

            if use_webhook:
                webhook_url = input(Fore.CYAN + "Enter Discord webhook URL: ").strip()
                if webhook_url:
                    if not send_to_discord(webhook_url, geolocation_data):
                        save_to_file(geolocation_data)
            else:
                save_to_file(geolocation_data)

        continue_scan = input(Fore.YELLOW + "\nScan another IP? (y/n): ").lower() == "y"
        if not continue_scan:
            print(Fore.BLUE + "\nThanks for using IP Geolocation Tool. Goodbye!")
            break
        clear_terminal()
        print_header()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.BLUE + "\n\nProgram terminated by user. Goodbye!")
