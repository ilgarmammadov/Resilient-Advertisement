import json
import csv
import pprint

ATLAS_API_KEY = "a5827315-a74a-4efd-bcf7-9f0400b2b6f1"
data_to_write = [["Probe_ID", "Probe_IPv4_Address", "Country_Code", "ASN_v4"]]
file_path = "IPv4_Addresses.csv"


def get_probe_addresses(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    
    for i in range(0, len(data["objects"])):
        if(data["objects"][i]["address_v4"] != None and data["objects"][i]["status_name"] == 'Connected'):
            data_to_write.append([data["objects"][i]["id"], data["objects"][i]["address_v4"], data["objects"][i]["country_code"], data["objects"][i]["asn_v4"]])
    with open(file_path, mode = 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(data_to_write)
    print("Data written successfully")
    
    
    
if __name__ == "__main__":
    get_probe_addresses("20240313.json")