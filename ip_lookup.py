import requests
import gzip
from bs4 import BeautifulSoup
from io import BytesIO
import ipaddress
import csv


ip_prefix_asn_array = []


def decimal_ip_to_binary(decimal_ip):
    # Parse the decimal IP address string
    ip = ipaddress.IPv4Address(decimal_ip)
    
    # Convert the IP address to binary format
    binary_ip = bin(int(ip))[2:].zfill(32)
    
    return binary_ip


def find_url(year,month, day):
    base_url = f"http://data.caida.org/datasets/routing/routeviews-prefix2as/{year}/{month:02d}/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raises an HTTPError if the response was an error
    except requests.RequestException as e:
        raise SystemExit(f"Error fetching data: {e}")
    
    # Parse the webpage to find links
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    if(len(str(month)) == 1):
        month = "0" + str(month)
    time = str(year)+str(month)+str(day)
    # Find the first file that matches the date format in its name
    for link in links:
        
        if time in link.text:
            file_name = link.text
            return f"{base_url}{file_name}"
    
    # Return an an empty string as an error
    return ""


def get_content(url_link):
    try:
        
        response = requests.get(url_link)
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as gz_file:
            file_content = gz_file.read().decode('utf-8')  # Assuming it's UTF-8 encoded text
            lines = file_content.split('\n')
            for line in lines:
                ip_prefix_asn_array.append(line.split('\t'))
            return ip_prefix_asn_array
        
    except requests.RequestException as e:
        print("Error:", e)
    except Exception as e:
        print("Error:", e)
        
def write_to_file(filename, content):
    with open(filename, mode = 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(content)
    print("Data written successfully")
    
    
if __name__ == "__main__":
    binary_ip_array = []
    decimal_ip_array = get_content(find_url(2024, 3, 18))
    for ip in decimal_ip_array:
        if(ip[0] != ''):
            binary_ip_array.append([decimal_ip_to_binary(ip[0]), ip[1], ip[2]])
            
    write_to_file("csv_files/binary_ip_asn_database.csv", binary_ip_array)


    