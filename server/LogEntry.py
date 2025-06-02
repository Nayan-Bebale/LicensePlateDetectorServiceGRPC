import os
import csv
import json
import requests
from parameters import get_asn_info, get_default_netmask, get_ip_info, calculate_subnet, calculate_cidr
# from ipwhois import IPWhois

# from ipwhois import IPWhois

LOG_FILE = 'server_logs.csv'
CENTRAL_FLASK_APP_URL = 'http://127.0.0.1:8080/' # data base (google Sheets)
service_type = "Sign-Detection"


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
    
    def add_user_data(self, log_message):
        ip_address = log_message.ip_address

        # Default values
        subnet = 'Not available'
        netmask = 'Not available'
        city, region, country = 'Not available', 'Not available', 'Not available'
        longitude, latitude = 0.0, 0.0
        asn, asn_description = 'Not available', 'Not available'

        if ip_address == '127.0.0.1' or ip_address == 'localhost':
            print("YES Boss")
        else:
            netmask = get_default_netmask(ip_address)
            if netmask != 'Unknown Class or Invalid IP Address':
                subnet = f"{calculate_subnet(ip_address, netmask)}/{calculate_cidr(netmask)}"
            else:
                print(f"Invalid netmask: {netmask}")
                netmask = 'Not available'
                subnet = 'Not available'

            # Get ASN info
            asn, asn_description = get_asn_info(ip_address)

            # Get IP info
            ip_info = get_ip_info(ip_address)
            if isinstance(ip_info, dict):
                location = ip_info.get('loc', '0.0,0.0')
                try:
                    latitude, longitude = map(float, location.split(','))
                except ValueError:
                    print(f"Invalid location format: {location}")
                    latitude, longitude = 0.0, 0.0

                city = ip_info.get('city', 'Not available')
                region = ip_info.get('region', 'Not available')
                country = ip_info.get('country', 'Not available')
            else:
                print("Could not retrieve public IP information.")

        # Prepare user data dict
        user_data = {
            'ip_address': ip_address,
            'latitude': latitude,
            'longitude': longitude,
            'city': city,
            'region': region,
            'country': country,
            'asn': asn,
            'asn_description': asn_description,
            'subnet_mask': netmask,
            'subnet': subnet
        }

        # Check if user data already exists in the central Flask app
        try:
            check_response = requests.get(f'{CENTRAL_FLASK_APP_URL}/get_userdata/{ip_address}')
            if check_response.status_code == 200:
                print("User data already exists, skipping addition.")
            else:
                # Send POST request to add user data
                response = requests.post(f'{CENTRAL_FLASK_APP_URL}/add_userdata', json=user_data)
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.text}")
                if response.status_code != 201:
                    print(f"Failed to save user data. Response: {response.text}")
        except requests.RequestException as e:
            print(f"HTTP request failed: {e}")

         
    def add_model_data(self, log_messages):
        model_result = {
                'ip_address': log_messages.ip_address,
                'model_name': log_messages.service_name,
                'service_type': service_type,
                'latency_time': round(log_messages.total_response_time - log_messages.process_time, 4),
                'cpu_usage': round(log_messages.cpu_utilized, 2),
                'memory_usage': round(log_messages.memory_utilized, 2),
                'throughput': round(log_messages.throughput,2),
                'energy_required': 0.0,
                'power_watts': round(log_messages.power, 2),
                'response_time': round(log_messages.total_response_time,2)
            }

            # Send POST request to add model result
        response = requests.post(f'{CENTRAL_FLASK_APP_URL}/modelresult', json=model_result)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        if response.status_code != 201:
            print(f"Failed to save model result. Response: {response.text}")

        return
    




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
