import subprocess
import os
from collections import deque
import re
from datetime import datetime


class Aircrack:
    def __init__(self, cap_path, word_list_path):
        self.time = datetime(1900, 1, 1, 0, 0, 0)
        self.running = True
        self.__queue = deque(maxlen=2)
        self.aircrack = subprocess.Popen(self.__get_command(cap_path, word_list_path), stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, bufsize=1, text=True)

    def __paths_are_valid(self, cap_path, word_list_path):
        if os.path.isfile(cap_path) and os.path.isfile(word_list_path):
            return True
        return False

    def __get_command(self, cap_path, word_list_path):
        if self.__paths_are_valid(cap_path, word_list_path):
            return ["aircrack-ng", cap_path, "-w", word_list_path]
        # Raise Exception

    def __was_key_found(self, key):
        if key == "KEY NOT FOUND":
            print("bye")
            quit()

    def __format_key(self, key_str):
        key = str(key_str).replace("", "")
        key = key[key.find("KEY"):]
        return key

    def __extract_password_from_key(self, key):
        password = key[key.find("[") + 2:-2]
        return password

    def __get_key(self):
        un_formatted_key = self.__queue[0]
        key = self.__format_key(un_formatted_key)
        self.__was_key_found(key)
        return key

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

    def stop_process(self):
        self.aircrack.terminate()
        quit()

    def run_aircrack(self):
        while self.aircrack.poll() is None:
            for line in iter(self.aircrack.stdout.readline, ""):
                self.__queue.append(line.strip())
                self.__update_time(line.strip())

        password = self.__extract_password_from_key(self.__get_key())
        print(password)


a = Aircrack("./known_pass.cap", "./test.txt")
