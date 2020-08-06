import subprocess
from collections import deque
import re
from datetime import datetime


class Aircrack:
    def __init__(self, cap_path, word_list_path):
        self.time = datetime(1900, 1, 1, 0, 0, 0)
        self.password = None
        self.running = True
        self.__queue = deque(maxlen=2)
        self.__cap_path = cap_path
        self.__word_list_path = word_list_path

    def __get_command(self, cap_path, word_list_path):
        return ["aircrack-ng", cap_path, "-w", word_list_path]

    def __was_key_found(self, key, shared_list):
        if key == "KEY NOT FOUND":
            self.running = False
            shared_list[:] = (self.password, self.time, self.running)
            exit(0)

    def __format_key(self, key_str):
        key = str(key_str).replace("", "")
        key = key[key.find("KEY"):]
        return key

    def __extract_password_from_key(self, key):
        password = key[key.find("[") + 2:-2]
        return password

    def __get_key(self, shared_list):
        un_formatted_key = self.__queue[0]
        key = self.__format_key(un_formatted_key)
        self.__was_key_found(key, shared_list)
        return key

    def get_word_list_path(self):
        return self.__word_list_path

    def __update_time(self, line):
        hour = "0"
        minute = "0"
        second = "0"
        if "Time left:" in line:
            if "hour" in line:
                hour = re.findall(r"Time left: (.*) hour", line.strip())[0]
                if "minute" in line:
                    minute = re.findall(r"(?<=, )(.*?)(?=\s)", line.strip())[0]
                if "second" in line and "minute" not in line:
                    second = re.findall(r"(?<=, )(.*?)(?=\s)", line.strip())[0]
                elif "second" in line:
                    second = re.findall(r"(?<=, )(.*?)(?=\s)", line.strip())[-1]
            elif "minute" in line:
                minute = re.findall(r"Time left: (.*) minute", line.strip())[0]
                second = re.findall(r"(?<=, )(.*?)(?=\s)", line.strip())[0]
            elif "second" in line:
                second = re.findall(r"Time left: (.*) second", line.strip())[0]

            self.time = datetime.strptime(f"{hour}:{minute}:{second}", "%H:%M:%S")

    def run_aircrack(self, shared_list):
        aircrack = subprocess.Popen(self.__get_command(self.__cap_path, self.__word_list_path), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, bufsize=1, text=True)

        while aircrack.poll() is None:
            for line in iter(aircrack.stdout.readline, ""):
                self.__queue.append(line.strip())
                self.__update_time(line.strip())
                shared_list[:] = (self.password, self.time, self.running)

        password = self.__extract_password_from_key(self.__get_key(shared_list))
        self.password = password
        self.running = False
        shared_list[:] = (self.password, self.time, self.running)
