import Aircrack
from multiprocessing import Process, Manager
import os
from datetime import datetime
import time
import sys


def show_help():
    print("")
    print("usage: multicrack [path to .cap file] [path to directory containing word lists ]")
    print("usage: multicrack [path to .cap file] -w <word list 1> <word list 2> <...>")
    print("")


def is_normal_mode():
    if sys.argv[2] == "-w":
        return False
    return True


class App:
    def __init__(self, *variables):
        print("[+] Initialing multicrack.")
        self.start_time = time.time()
        self.normal_mode = variables[0]
        self.cap_path = variables[1]
        self.is_cap_file()
        self.dir_path = variables[2]
        self.word_list_paths = None
        if self.normal_mode is False:
            self.word_list_paths = variables[3:]
        self.aircrack_objects = self.fill_aircracK_objects()
        self.processes = []
        self.shared_lists = []
        self.paths_of_shared_lists = {}
        self.password = None
        print("[-] Initialisation completed.")

    def calculate_processing_time(self):
        end_time = time.time()
        return end_time - self.start_time

    def is_cap_file(self):
        if self.cap_path[-4:] == ".cap":
            return True
        print("[ERROR] You have to enter a valid .cap file")
        quit(0)

    def paths_are_valid(self):
        if os.path.isdir(self.dir_path) and os.path.isfile(self.cap_path):
            return True
        print("[ERROR] Wrong values!")
        show_help()
        quit(0)

    def is_txt_file(self, path):
        if os.path.isfile(path) and path[-4:].strip() == ".txt":
            return True
        return False

    def fill_aircracK_objects_by_dir(self):
        aircrack_objects = []
        if self.paths_are_valid():
            for file in os.listdir(self.dir_path):
                path = os.path.join(self.dir_path, file)
                if self.is_txt_file(path):
                    aircrack_objects.append(Aircrack.Aircrack(self.cap_path, path))
        return aircrack_objects

    def fill_aircracK_objects_by_files(self):
        aircrack_objects = []
        for path in self.word_list_paths:
            if self.is_txt_file(path) and os.path.isfile(path):
                aircrack_objects.append(Aircrack.Aircrack(self.cap_path, path))
            else:
                print(f"[ERROR] The file: {path} does not exist.")
                print("[+] Proceeding without file.")
        return aircrack_objects

    def fill_aircracK_objects(self):
        if self.normal_mode is False:
            return self.fill_aircracK_objects_by_files()
        return self.fill_aircracK_objects_by_dir()

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
        self.check_password(password)
        if password is not None:
            print(f"\r[+] Password Found in {word_list_path}")
            print(f"\r[+] Terminating multicrack.")
            print(f"\r[+] multicrack finished after {self.calculate_processing_time()} seconds.")
            print("[Estimated Time Left: --:--:--]")
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

    def check_password(self, password):
        if password == "":
            print("")
            print("[+] An Error Occurred.")
            print("\r[+] terminating multicrack.")
            quit(0)

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
            print(f"\r[Estimated Time Left: {average_time}]", end="")

            time.sleep(1)

        print(f"\r[+] multicrack finished after {self.calculate_processing_time()} seconds.")
        print("\r[Estimated Time Left: --:--:--]")
        print("\nNothing Found.")


if __name__ == "__main__":
    arguments = len(sys.argv)
    if arguments < 3 or (arguments > 3 and sys.argv[2] != "-w") or arguments == 1:
        show_help()
        exit(0)

    os.system('cls' if os.name == 'nt' else 'clear')

    normal_mode = is_normal_mode()

    try:
        app = App(normal_mode, sys.argv[1], sys.argv[2], *sys.argv[3:])
        app.run_app()
    except KeyboardInterrupt:
        print("\r[Estimated Time Left: --:--:--]")
        print("[+] terminating multicrack.")
        exit(0)
