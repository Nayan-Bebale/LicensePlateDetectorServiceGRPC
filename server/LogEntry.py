import os
import csv
import json
import requests
# from ipwhois import IPWhois

LOG_FILE = 'server_logs.csv'

class LogEntry:
    def __init__(self):
        pass

    def add_to_csv(self, log_message):
        log_entry_csv = {
            'service_name': log_message.service_name,
            'ip_address': log_message.ip_address,
            'location': self.get_location_from_ip(log_message.ip_address),
            'grpc_response_time': log_message.grpc_response_time,
            'grpc_system_latency': round(log_message.grpc_response_time - log_message.process_time, 4),
            'total_response_time': log_message.total_response_time,
            'total_latency': round(log_message.total_response_time - log_message.process_time, 4),
            'throughput': log_message.throughput
        }
        # Check if the file already exists
        file_exists = os.path.isfile(LOG_FILE)
        # Define fieldnames to maintain the column order
        fieldnames = [
            'task_name','service_name', 'ip_address', 'location', 
            'grpc_response_time', 'grpc_system_latency', 
            'total_response_time', 'total_latency', 'throughput', 'power'
        ]
        # Open the CSV file in append mode
        with open(LOG_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write header only if file does not exist
            if not file_exists:
                writer.writeheader()
            # Write the log entry as a new row
            writer.writerow(log_entry_csv)


    def get_frontend_string(self, log_message):
        log_entry_frontend = {
            'service_name': log_message.service_name,
            'ip_address': log_message.ip_address,
            'location': self.get_location_from_ip(log_message.ip_address),
            'grpc_response_time': str(round(log_message.grpc_response_time,2)) + " ms",  # Convert to string
            'grpc_system_latency': str(round(log_message.grpc_response_time - log_message.process_time, 2)) + " ms",  # Convert to string
            'total_response_time': str(round(log_message.total_response_time,2)) + " ms",  # Convert to string
            'total_latency': str(round(log_message.total_response_time - log_message.process_time, 2)) + " ms",  # Convert to string
            'throughput': str(round(log_message.throughput,2)) + " Mbps"  # Convert to string
        }
        log_entry_string = json.dumps(log_entry_frontend, indent=4)

        return log_entry_string
    

    # Adding Metrics to DB
#     def add_user_data(self, log_message):
#         if ip_address == '127.0.0.1' or ip_address == 'localhost':
#             subnet = 'Not available'
#             netmask = 'Not available'
#         else:
#             netmask = self.get_default_netmask(ip_address)
#             if netmask != 'Unknown Class or Invalid IP Address':
#                 subnet = f"{self.calculate_subnet(ip_address, netmask)}/{self.calculate_cidr(netmask)}"
#             else:
#                 subnet = 'Not available'
#                 netmask = 'Not available'

#             # Prepare user data
#         asn, asn_description = self.get_asn_info(ip_address)
        
#         ip_info = self.get_ip_info(ip_address)


#     # Ensure ip_info is a dictionary before accessing keys
#         if isinstance(ip_info, dict):
#             location = ip_info.get('loc', 'Not available')
#         else:
#             print(f"Invalid IP info: {ip_info}")
#             location = "Not available"
        
#         # Default values for latitude and longitude if location is not available
#         latitude, longitude = None, None
#         if location != 'Not available':
#             latitude, longitude = map(float, location.split(','))

#         if isinstance(ip_info, dict):
#             city = ip_info.get('city', 'Not available')
#             region = ip_info.get('region', 'Not available')
#             country = ip_info.get('country', 'Not available')
#         else:
#             print("Could not retrieve public IP information.")
#             city, region, country = 'Not available', 'Not available', 'Not available'


#         user_data = {
#             'ip_address': log_message.ip_address,
#             'latitude': latitude,
#             'longitude': longitude,
#             'city': city,
#             'region': region,
#             'country': country,
#             'asn': asn,
#             'asn_description': asn_description,
#             'subnet_mask': netmask,
#             'subnet': subnet
#         }

#         return
    
#     def add_model_data(log_messages):
#         return
    
#     def add_server_data(log_messages):
#         return
    

#     # Getting USER data from ip
#     def get_ip_info(ip):
#         try:
#             if ip == '127.0.0.1' or ip == 'localhost':
#                 return 'Not applicable'
#             response = requests.get(f"https://ipinfo.io/{ip}/json")
#             data = response.json()
#             return data
#         except Exception as e:
#             print("Error fetching IP information:", e)
#             return None
    

# # Get ASN using ipwhois
#     def get_asn_info(ip):
#         try:
#             if ip == '127.0.0.1' or ip == 'localhost':
#                 return 'Not applicable', 'Not applicable'
#             obj = IPWhois(ip)
#             results = obj.lookup_rdap()
#             return results['asn'], results['asn_description']
#         except Exception as e:
#             print("Error fetching ASN information:", e)
#             return None, None


#     def get_default_netmask(ip):
#         try:
#             if ip == '127.0.0.1' or ip == 'localhost':
#                 return 'Not applicable'

#             # Parse the IP address
#             ip_obj = ipaddress.IPv4Address(ip)
            
#             # Determine the class of the IP and return the default subnet mask
#             first_octet = int(str(ip_obj).split('.')[0])

#             if first_octet >= 1 and first_octet <= 126:
#                 return '255.0.0.0'  # Class A
#             elif first_octet >= 128 and first_octet <= 191:
#                 return '255.255.0.0'  # Class B
#             elif first_octet >= 192 and first_octet <= 223:
#                 return '255.255.255.0'  # Class C
#             else:
#                 return 'Unknown Class or Invalid IP Address'
#         except Exception as e:
#             return str(e)



    def get_location_from_ip(self, ip_address):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}")
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data['country'],
                    'region': data['regionName'],
                    'city': data['city']
                }
            else:
                return {"error": "Unable to retrieve location"}
        except Exception as e:
            return {"error": str(e)}
