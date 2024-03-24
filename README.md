# Resilient-Advertisement

The folder contains the start_measurement.py file which is the main file.



In the "main" part of the file, please change the all_targets_list to contain all target
IP Addresses. get_probe_ids function processes the JSON file containing all active probes
in the ATLAS database, you can update the file if needed. Once the measurements are completed
the results will be written to Results_file = "Test_results_1.csv" file, you can change the name in the beginning of the program. 
Similarly, measurement details are written to Details_file = "Test_details_1.csv", which you can modify.
Lastly, ASN lookup function is performed on the results file, and the final results are written to ASN_results_file = "test.csv".



csv_files folder contains the RouteViews database both in binary and in decimal form which is used for ASN lookup.



ASN_lookup.py file is for processing the test results file. Although it has been integrated to the star_measurement.py, 
if any error occurs, this file can be used to reprocess the results file.



Test_details, Test results and test.csv files are sample results for "google.com".
