from openai import Client
import subprocess
import re
import sys
import socket
import datetime

# Set your OpenAI API key
api_key = "Your API Key"
client = Client(api_key=api_key)

def is_package_installed(package_name):
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "show", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def get_ip_address():
    try:
        # Get the hostname
        hostname = socket.gethostname()
        # Get the IP address associated with the hostname
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return str(e)

def list_installed_packages():
    try:
        # Execute the pip list command to retrieve information about installed packages
        output = subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode("utf-8")
        # Split the output into lines and skip the first two lines (header)
        lines = output.split('\n')[2:]
        # Extract the package names
        package_info = [line.split()[0] for line in lines if line.strip()]
        return package_info
    except subprocess.CalledProcessError as e:
        return f"An error occurred while listing installed packages: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def list_installed_packages_today():
    try:
        # Execute the pip show command to retrieve information about installed packages
        output = subprocess.check_output([sys.executable, "-m", "pip", "show", "--verbose"]).decode("utf-8")
        # Split the output into sections for each package
        sections = output.split('\n---\n')
        # Filter out the sections containing information about installed packages
        package_sections = [section for section in sections if section.startswith('Name:')]
        # Extract the package names and installation dates
        package_info = []
        for section in package_sections:
            name = section.split('\n')[0].split(': ')[1]
            # Extract the installation date from the section
            date_line = [line for line in section.split('\n') if line.startswith('  Installed:')]
            if date_line:
                install_date_str = date_line[0].split(': ')[1].strip()
                install_date = datetime.datetime.strptime(install_date_str, '%Y-%m-%dT%H:%M:%S')
                # Check if the package was installed today
                if install_date.date() == datetime.datetime.now().date():
                    package_info.append(name)
        return package_info
    except subprocess.CalledProcessError as e:
        return f"An error occurred while listing installed packages today: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def process_input(input_text):
    try:
        # Convert input to lowercase for case-insensitive matching
        input_text_lower = input_text.lower()
        
        if input_text_lower == "what is the current time":
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            return f"The current time is {current_time}."
        elif input_text_lower == "what is today's date":
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            return f"Today's date is {current_date}."
        elif re.match(r'^\d+(\.\d+)?[\+\-\*/]\d+(\.\d+)?$', input_text_lower):
            result = eval(input_text)
            return str(result)
        elif input_text_lower.startswith("what is my ip address"):
            ip_address = get_ip_address()
            return ip_address
        elif "uninstall" in input_text_lower:
            # Extract the package name using regular expression
            match = re.search(r'uninstall\s+(.*)', input_text_lower)
            if match:
                package_name = match.group(1)
                if is_package_installed(package_name):
                    # Uninstall the package using pip
                    subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
                    return f"Package '{package_name}' has been uninstalled successfully."
                else:
                    return f"Package '{package_name}' is not installed."
        elif "install" in input_text_lower:
            # Extract the package name using regular expression
            match = re.search(r'install\s+(.*)', input_text_lower)
            if match:
                package_name = match.group(1)
                # Install the package using pip
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                    return f"Package '{package_name}' has been installed successfully."
                except subprocess.CalledProcessError as e:
                    error_message = str(e)
                    # Provide a solution based on the error message
                    if "No matching distribution found" in error_message:
                        return f"No matching distribution found for '{package_name}'."
                    elif "Permission denied" in error_message:
                        return f"Permission denied while installing '{package_name}'. Try running the command with administrator privileges."
                    else:
                        return f"An error occurred while installing '{package_name}': {error_message}"
                except Exception as e:
                    return f"An unexpected error occurred: {e}"
        elif input_text_lower == "show the list packages":
            installed_packages = list_installed_packages()
            if isinstance(installed_packages, list):
                return "Installed packages:\n" + "\n".join(installed_packages)
            else:
                return installed_packages
        elif input_text_lower == "show the packages installed today":
            installed_packages_today = list_installed_packages_today()
            if isinstance(installed_packages_today, list):
                return "Packages installed today:\n" + "\n".join(installed_packages_today)
            else:
                return installed_packages_today
        else:
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",  # Updated model
                prompt=input_text_lower,  # Use lowercased input for processing
                max_tokens=50
            )
            return response.choices[0].text.strip()
    except Exception as e:
        error_message = str(e)
        return f"An error occurred: {error_message}"

def main():
    while True:
        user_input = input("Enter command: ")
        if user_input.lower() == 'exit':
            break
        processed_input = process_input(user_input)
        print(processed_input)

if __name__ == "__main__":
    main()
