import Aircrack
from multiprocessing import Process, Manager
import os
from datetime import datetime
import time


class App:
    def __init__(self, cap_path, word_list_dir_path):
        self.cap_path = cap_path
        self.word_list_dir_path = word_list_dir_path
        self.aircrack_objects = self.fill_aircracK_objects()
        self.processes = []
        self.shared_lists = []
        self.paths_of_shared_lists = {}
        self.password = None

    def paths_are_valid(self):
        if os.path.isdir(self.word_list_dir_path) and os.path.isfile(self.cap_path):
            return True
        return False

    def is_txt_file(self, path):
        if os.path.isfile(path) and path[-4:].strip() == ".txt":
            return True
        return False

    def fill_aircracK_objects(self):
        aircrack_objects = []
        if self.paths_are_valid():
            for file in os.listdir(self.word_list_dir_path):
                path = os.path.join(self.word_list_dir_path, file)
                if self.is_txt_file(path):
                    aircrack_objects.append(Aircrack.Aircrack(self.cap_path, path))
        return aircrack_objects

    def start_processes(self):
        for aircrack in self.aircrack_objects:
            shared_list = Manager().list()
            p = Process(target=aircrack.run_aircrack, daemon=True, args=(shared_list,))
            p.start()
            self.processes.append(p)
            self.shared_lists.append(shared_list)
            self.paths_of_shared_lists[shared_list] = aircrack.get_word_list_path()

            print(f"[+] Started Processing {aircrack.get_word_list_path()}")

    def password_was_found(self, password, word_list_path):
        if password is not None:
            print(f"\r[+] Password Found in {word_list_path}")
            print(f"\r[+] Stopping other Processes.")
            print("[Time Left: --:--:--]")
            print("")
            print("Password Found!".upper())
            print("" + "-" * len(password))
            print(password)
            print("" + "-" * len(password))
            exit(0)

    def password_was_not_found(self, password, is_running):
        if password is None and is_running is False:
            return True
        return False

    def get_average_time(self, datetime_objects):
        average = 0
        if len(datetime_objects) != 0:
            for datetime_object in datetime_objects:
                average += datetime_object.timestamp()
            average = average / len(datetime_objects)
            average = datetime.fromtimestamp(average)
            average = average.strftime("%H:%M:%S")
            return average
        return "00:00:00"

    def run_app(self):
        self.start_processes()
        while self.password is None and len(self.shared_lists) != 0:
            datetime_objects = []
            for shared_list in self.shared_lists:
                if len(shared_list) == 0:
                    continue

                password, time_object, is_running = shared_list
                word_list_path = self.paths_of_shared_lists[shared_list]

                self.password_was_found(password, word_list_path)
                if self.password_was_not_found(password, is_running):
                    self.shared_lists.remove(shared_list)
                    print(f"\r[-] Finished Processing {word_list_path}. No Password Found.")

                if time_object.hour != 0 or time_object.minute != 0 or time_object.second != 0:
                    datetime_objects.append(time_object)

            average_time = self.get_average_time(datetime_objects)
            print(f"\r[Time Left: {average_time}]", end="")

            time.sleep(1)

        print("\r[Time Left: --:--:--]")
        print("\nNothing Found.")


app = App("./known_pass.cap", "./wordlists")
app.run_app()
