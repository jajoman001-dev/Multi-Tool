# All rights reserved.
# This code is provided for educational purposes only.
# Use it at your own risk.
# Created by: Joshy
# Version: 1.0
# Unauthorized copying or redistribution of this code is strictly prohibited.
# Skidding (copying and using code without understanding it) is not permitted.
# Modifying or redistributing this code without the authors' permission is forbidden.
# For support or inquiries, contact: deadcode .exe

# Import the required libraries

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
from colorama import Fore, Style, init

# Initialize colorama

init(autoreset=True)


# This function maps the number type integer to a string description


def get_number_type_string(number_type):
    if number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
        return "Fixed Line"
    elif number_type == phonenumbers.PhoneNumberType.MOBILE:
        return "Mobile"
    elif number_type == phonenumbers.PhoneNumberType.VOIP:
        return "VoIP"
    else:
        return "Unknown"


# This function sends the message to Discord


def send_to_discord(webhook_url, message):
    try:
        data = {"content": message}
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print(Fore.GREEN + "Message sent to Discord successfully!")
        else:
            print(
                f"Error while sending to Discord: {response.status_code}, {response.text}"
            )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# This function gets the phone number information


def get_phone_number_info():
    first_run = True  # Flag to check if it's the first run

    while True:
        # Display ASCII Art only for the first run
        if first_run:
            print(
                Fore.CYAN
                + """ 
                                                       j@@@@@^                                 
                           _@v   p@@@@j           j@@@@@@@@@@@@@@@;          |@@@@M   v@}      
                          @@@@@} >@@@@    v@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@p    @@@@_ _@@@@@     
                          >@@@v    @@     v@@@@@@@@@@@@      p@@@@@@@@@@@a     @@    j@@@_     
                           ^@@     @@@@   |@@@@@@@@@@^ @@@@@@; @@@@@@@@@@p   p@@@     M@;      
                           ^@@            >@@@@@@@@@@ p@@@@@@@ M@@@@@@@@@j            M@;      
                           ^@@@@@@@@@@@}   @@@@@@@@|            >@@@@@@@@;   @@@@@@@@@@@;      
                                           }@@@@@@@|    O@@@    >@@@@@@@M                      
                          |@@@@             @@@@@@@|     M@     >@@@@@@@^            @@@@j     
                          @@@@@@@@@@@@@@@>   @@@@@@|    O@@@    >@@@@@@    @@@@@@@@@@@@@@@     
                            ^                 @@@@@v            }@@@@@^                ^       
                                 p@@@@@@@@@^   M@@@@@@@@@@@@@@@@@@@@@    @@@@@@@@@p            
                                 p@_            ^@@@@@@@@@@@@@@@@@@>            >@a            
                                @@@@O              @@@@@@@@@@@@@@              J@@@@           
                               ;@@@@@                 J@@@@@@p                 @@@@@>          
                                  ;              p@              p@>  M@@_       ;             
                                          @@@@p  p@_  ;      j_  a@@@@@@@@j                    
                                         ^@@@@@@@@@   v@_   O@}       M@@_                     
                                            ;         p@|   O@}      }}                        
                                                    >@@@@@  O@@@@@@@@@@@J                      
                                                     p@@@j         ;@@@@^                      \n
        """
                + Fore.BLUE
                + Style.RESET_ALL
            )
            first_run = False  # After first run, no banner will be displayed

        # Ask if the user wants to use a webhook first
        use_webhook = input(
            Fore.YELLOW
            + "\nDo you want to use a Discord webhook? (y/n): "
            + Style.RESET_ALL
        )

        if use_webhook.lower() == "y":
            webhook_url = input(
                Fore.YELLOW
                + "\nPlease enter the Discord webhook URL: "
                + Style.RESET_ALL
            )
        else:
            webhook_url = None  # No webhook will be used

        # Ask for the phone number
        number = input(
            Fore.YELLOW + "\nEnter the phone number here: " + Style.RESET_ALL
        )

        # Add a blank line for spacing before the result
        print("\n")

        try:
            # Parse the number
            parsed_number = phonenumbers.parse(number)

            # Fetch phone number details
            country = geocoder.description_for_number(parsed_number, "de")
            service_provider = carrier.name_for_number(parsed_number, "de")
            valid_number = phonenumbers.is_valid_number(parsed_number)
            number_type = phonenumbers.number_type(parsed_number)
            number_type_str = get_number_type_string(
                number_type
            )  # Use the function to get the string representation
            national_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
            )
            international_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            e164_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )

            # Get the country code and area code
            country_code = parsed_number.country_code
            area_code = "N/A"  # Some numbers may not have an area code
            location_data = geocoder.description_for_number(parsed_number, "en")
            lat, lon = (
                51.5,
                10.5,
            )  # Default coordinates for Germany (can be fetched dynamically if needed)
            continent = "Europe"  # We set this as an example, could be dynamically retrieved based on region
            timezone_data = timezone.time_zones_for_number(parsed_number)
            timezone_str = ", ".join(timezone_data) if timezone_data else "N/A"

            # Generate the message to send
            discord_message = (
                f"**Phone Number Information:**\n"
                f"> **Query:** {number}\n"
                f"> **Status:** Success\n"
                f"> **Number Type:** {number_type_str}\n"
                f"> **Number Valid:** {'Yes' if valid_number else 'No'}\n"
                f"> **Is Disposable:** No\n"
                f"> **Number Valid for Region:** {'Yes' if valid_number else 'No'}\n"
                f"> **Country Code:** {country_code}\n"
                f"> **Area Code:** {area_code}\n"
                f"> **Extension:** N/A\n"
                f"> **Format (E.164):** {e164_format}\n"
                f"> **Format (National):** {national_format}\n"
                f"> **Format (International):** {international_format}\n"
                f"> **Dialing from Country:** US\n"
                f"> **Dialing from Country Number:** 011 {country_code} {national_format}\n"
                f"> **Carrier:** {service_provider}\n"
                f"> **Continent:** {continent}\n"
                f"> **Country:** {country}\n"
                f"> **Region:** N/A\n"
                f"> **City:** {location_data}\n"
                f"> **ZIP:** N/A\n"
                f"> **Latitude:** {lat}\n"
                f"> **Longitude:** {lon}\n"
                f"> **Timezone:** {timezone_str}\n"
                f"> **||@everyone||**\n"
            )

            # Plain Text message (for terminal output without webhook)
            plain_message = (
                f"Phone Number Information:\n"
                f"Query: {number}\n"
                f"Status: Success\n"
                f"Number Type: {number_type_str}\n"
                f"Number Valid: {'Yes' if valid_number else 'No'}\n"
                f"Is Disposable: No\n"
                f"Number Valid for Region: {'Yes' if valid_number else 'No'}\n"
                f"Country Code: {country_code}\n"
                f"Area Code: {area_code}\n"
                f"Extension: N/A\n"
                f"Format (E.164): {e164_format}\n"
                f"Format (National): {national_format}\n"
                f"Format (International): {international_format}\n"
                f"Dialing from Country: US\n"
                f"Dialing from Country Number: 011 {country_code} {national_format}\n"
                f"Carrier: {service_provider}\n"
                f"Continent: {continent}\n"
                f"Country: {country}\n"
                f"Region: N/A\n"
                f"City: {location_data}\n"
                f"ZIP: N/A\n"
                f"Latitude: {lat}\n"
                f"Longitude: {lon}\n"
                f"Timezone: {timezone_str}\n"
            )

            if webhook_url:
                # Send the formatted message to Discord if webhook is provided
                send_to_discord(webhook_url, discord_message)
            else:
                # Print the plain message to terminal in blue, formatted without `** >`
                print(Fore.BLUE + plain_message)

        except phonenumbers.NumberParseException:
            print(
                "\nError: The number you entered is not valid. Please enter a valid phone number."
            )

        # Ask user if they want to scan another number
        again = input(
            Fore.YELLOW
            + "\nDo you want to scan another number? (y/n): "
            + Style.RESET_ALL
        )
        if again.lower() != "y":
            break


# Main function
if __name__ == "__main__":
    get_phone_number_info()
