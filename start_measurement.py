from ripe.atlas.cousteau import Traceroute, AtlasSource, AtlasCreateRequest, AtlasResultsRequest, AtlasLatestRequest
from datetime import datetime, timedelta, timezone
import pprint, json, time, ipaddress
import csv

ATLAS_API_KEY = "a5827315-a74a-4efd-bcf7-9f0400b2b6f1"
MAX_PROBES_COUNT = 1000
MAX_MEASUREMENTS_COUNT = 25
measurement_ids = []
measurement_details = []
file_content = [["Target", "Measurement_ID", "Sources", "Start_time"]]
result_content = [["Destination", "Source", "Probe_ID", "Hops", "ASN"]]
Results_file = "Test_results_1.csv"
Details_file = "Test_details_1.csv"
ASN_results_file = "test.csv"

#Write the "content" to the csv file with "filename"
def write_to_file(filename, content):
    with open(filename, mode = 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(content)
    print("Data written successfully")
    
    
    
#Once measurements are complete, get results and add to an array to save to CSV file
def results_obtain(target):
    for measurement in measurement_details:
        try:
            if(measurement["target"] == target):
                results = fetch_results(measurement["id"], datetime(measurement["start_time"].year, measurement["start_time"].month, measurement["start_time"].day), measurement["sources"])
                if(results != None):
                    result_details = {}
                    for result in results:
                        result_content.append([result["dst_addr"], result["src_addr"], result["prb_id"], result["src_addr"]])
                        if(result["dst_addr"] in result_details):
                            result_details[result["dst_addr"]].append({"source" : result["src_addr"], "probe" : result["prb_id"], "hops" : []})
                            for hop in result["result"]:
                                if('from' in hop["result"][0]):
                                    result_details[result["dst_addr"]][-1]["hops"].append(hop["result"][0]["from"])
                                    result_content.append(["","","",hop["result"][0]["from"]])

                        
                                    
                                    
                        else:
                            result_details[result["dst_addr"]] = [{"source" : result["src_addr"], "probe" : result["prb_id"], "hops" : []}]
                            for hop in result["result"]:
                                if('from' in hop["result"][0]):
                                    result_details[result["dst_addr"]][-1]["hops"].append(hop["result"][0]["from"])
                                    result_content.append(["","","",hop["result"][0]["from"]])

                    time.sleep(60)
                else:
                    continue
        except:
            continue  


#get active probe IDs from ATLAS database
def get_probe_ids(filename, all_targets_list):
    all_sources_list = []
    with open(filename, "r") as file:
        data = json.load(file)
    for i in range(0, len(data["objects"])):
        if(data["objects"][i]["address_v4"] != None and data["objects"][i]["status_name"] == 'Connected'):
            all_sources_list.append(data["objects"][i]["id"])
    multiple_source_destination_measurement(all_sources_list, all_targets_list)
    
    
#Run measurement to all targets specified in "main"
def multiple_source_destination_measurement(all_sources_list, all_targets_list):
    sources_list = []
    for k in all_targets_list:
        #for i in range(0, len(all_sources_list) // MAX_PROBES_COUNT):
        for i in range(0,1):
            sources_list = all_sources_list[MAX_PROBES_COUNT*i : MAX_PROBES_COUNT * (i+1)]
            start_traceroute_measurement(k, sources_list)
        time.sleep(120)
        results_obtain(k)
        
   
            
#start traceroute measurement from given list of sources to a specific target        
def start_traceroute_measurement(target, source_ids):
    traceroute = Traceroute(af = 4, target = target, description = "TraceRoute Test", protocol = "ICMP")
    sources_string = ",".join(str(source) for source in source_ids)
    source = AtlasSource(type = "probes", value = sources_string, requested = 3, packets = 1)
    current_time = datetime.now(timezone.utc)
    current_time = datetime(current_time.year, current_time.month, current_time.day)
    atlas_request = AtlasCreateRequest(
        start_time = datetime.now(timezone.utc) + timedelta(seconds = 30),
        key = ATLAS_API_KEY,
        measurements = [traceroute],
        sources = [source],
        is_oneoff = True
    )
    (is_success, response) = atlas_request.create()
    if is_success:
        print("Successfully started measurement: ")
        print(response["measurements"])
        measurement_ids.append(response["measurements"])
        measurement_details.append({"sources" : source_ids, "target" : target, "start_time": current_time, "id":response["measurements"][0]})
        file_content.append([target, response["measurements"][0], source_ids, current_time])
        
    else:
        print("Error occurred, waiting for 60 seconds")
        print(response)
        print("Data will be written to file for backup")
        filename = Details_file                       #CSV Filename to store target, measurement ID, source IDs, and start time
        write_to_file(filename, file_content)                 #write measurement details to CSV file
        write_to_file(Results_file, result_content)   #Write measurement results to CSV file
        time.sleep(60)
    
    
        
#Fetch results from ATLAS with specified measurement ID, start_time and source IDs   
def fetch_results(msm_id, start_time, probe_ids):
    kwargs = {
        "msm_id": msm_id,
        "start": start_time,
        "probe_ids": probe_ids
    }
    
    (is_success, response) = AtlasLatestRequest(**kwargs).create()
    if is_success:
        return response
    else:
        pprint.pprint(response)
        return None
    
    
    
    
    
    
    
    
    
    
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

def write_to_file_asn(input_filename, output_filename):
    with open(output_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(read_test_result(input_filename))
    print("Data written successfully")


    


if __name__ == "__main__":
    
    all_targets_list = ["www.google.com"] #Give the list of targets to "all_targets_list"
    get_probe_ids("20240313.json", all_targets_list)      #Get the active source IDs from ripe database
    filename = Details_file                       #CSV Filename to store target, measurement ID, source IDs, and start time
    write_to_file(filename, file_content)                 #write measurement details to CSV file
    write_to_file(Results_file, result_content)   #Write measurement results to CSV file
    
    ASN_DATABASE = load_asn_database("csv_files/binary_ip_asn_database.csv")
    write_to_file_asn(Results_file, ASN_results_file)
    
    
    
