import ipaddress
import csv

# Load ASN database into memory for faster lookups
def load_asn_database(filename):
    asn_db = {}
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            binary_prefix = row[0][0:int(row[1])]
            asn_num = row[2]
            if binary_prefix not in asn_db or len(binary_prefix) > len(asn_db[binary_prefix][0]):
                asn_db[binary_prefix] = (binary_prefix, asn_num)
    return asn_db

ASN_DATABASE = load_asn_database("csv_files/binary_ip_asn_database.csv")

def decimal_ip_to_binary(decimal_ip):
    return bin(int(ipaddress.IPv4Address(decimal_ip)))[2:].zfill(32)

def find_asn_number(binary_ip):
    for prefix_length in range(32, 0, -1):  # Start with longest prefixes
        prefix = binary_ip[:prefix_length]
        if prefix in ASN_DATABASE:
            return ASN_DATABASE[prefix][1]
    return "0"  # If no match found

def read_test_result(filename):
    arr = [["target", "source", "hop", "address", "asn"]]
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if not row:
                break
            binary_ip = decimal_ip_to_binary(row[3])
            asn_number = find_asn_number(binary_ip)
            arr.append([row[0], row[1], row[2], row[3], asn_number])
    return arr

def write_to_file(input_filename, output_filename):
    with open(output_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(read_test_result(input_filename))
    print("Data written successfully")



write_to_file("Test_results_1.csv", "test.csv")
