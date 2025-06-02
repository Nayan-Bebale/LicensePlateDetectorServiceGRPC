import os
import requests
import time
import json
import csv
from ObjectProcessor import ObjectProcessor
from LogEntry import LogEntry
import subprocess
import psutil

service_data = {}

class ImageProcessor:
    def __init__(self):
        self.object_processor = ObjectProcessor()
        self.log_entry = LogEntry()


    def process_image(self, model_name):
        global model
        try:
            global model

            print(model_name)
            initial_power = self.get_power_usage_nvidia()
            process = psutil.Process(os.getpid())
            cpu_start = process.cpu_percent(interval=None)  # Start measuring CPU
            memory_info_start = process.memory_info().rss
            start_time=time.time()

            # inference start
            self.object_processor.load_model(model_name)
            detections = self.object_processor.detect_objects("received_image.jpg")
            # inference end

            end_time = time.time()
            final_power = self.get_power_usage_nvidia()
            cpu_end = process.cpu_percent(interval=None)  # End measuring CPU
            memory_info_end = process.memory_info().rss

            # Metrics calculation
            process_time = round((end_time - start_time) * 1000, 4)
            avg_power = round(((initial_power + final_power) / 2), 4)
            throughput = round(self.get_throughput(process_time, "received_image.jpg"), 4)
            num_cores = psutil.cpu_count(logical=True)  # Get number of logical cores
            cpu_used_percent = round(cpu_end / num_cores, 2)  # Average per core
            memory_used_mb = round((memory_info_end - memory_info_start) / (1024 * 1024), 4)

            
            print("detections")
            print(detections)
            print(f"process time is {process_time}")
            metrics = {
                "message": "Image Process Successfully",
                "process_time":process_time,
                "throughput":throughput,
                "power":avg_power,
                "cpu_utilized":cpu_used_percent,
                "memory_utilized": memory_used_mb

            }
            print(metrics) 
            return metrics

        except FileNotFoundError as fnf_error:
            # Handle file not found errors
            return fnf_error

        except ValueError as val_error:
            # Handle specific value-related issues
            return val_error

        except AttributeError as attr_error:
            # Handle missing attributes or methods
            return attr_error

        except Exception as e:
            # Catch all other unexpected errors
            return e




    def add_logs(self, log_message):
        print("ot time is")
        print(log_message.process_time)

        self.log_entry.add_to_csv(log_message)
        self.log_entry.add_user_data(log_message)
        self.log_entry.add_model_data(log_message)
        # self.log_entry.add_server_data(log_message)

        log_entry_string = self.log_entry.get_frontend_string(log_message)        
        return log_entry_string


        
    def get_throughput(self,ot_time, video_path):
        file_size_bytes = os.path.getsize(video_path)

        file_size_mb = file_size_bytes / (1024 * 1024)
        if ot_time==0:
            return 'err process time is 0'
        return round((file_size_mb / (ot_time / 1000)) * 8, 4)    #throughput Mbps


    def get_power_usage_nvidia(self):
        try:
           
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'])
            power_watts = float(output.decode('utf-8').strip())
            return power_watts
        except Exception as e:
            print(f"Error fetching power consumption: {e}")
            return 0  