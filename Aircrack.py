import subprocess
import os


class Aircrack:
    def __init__(self):
        self.time = None

    def paths_are_valid(self, cap_path, word_list_path):
        if os.path.isfile(cap_path) and os.path.isfile(word_list_path):
            return True
        return False

    def get_command(self, cap_path, word_list_path):
        if self.paths_are_valid(cap_path, word_list_path):
            return ["aircrack-ng", cap_path, "-w", word_list_path]
        # Raise Exception

    def format_key(self, key_str):
        key = str(key_str).replace("", "")
        key = key[key.find("KEY"):]
        return key

    def what_list_to_use(self, normal, back_up):
        if len(back_up) != 0:
            if "KEY FOUND!" in back_up[-2]:
                return back_up
        if len(normal) < 2:
            return back_up
        return normal

    def no_key_found(self, key_list):
        if "KEY NOT FOUND" in key_list[-3]:
            quit()

    def get_key(self, lines, back_up_lines):
        key_list = self.what_list_to_use(lines, back_up_lines)
        self.no_key_found(key_list)
        un_formatted_key = key_list[-2].strip()
        key = self.format_key(un_formatted_key)
        return key

    def run_aircrack(self, cap_path, word_list_path):
        aircrack = subprocess.Popen(self.get_command(cap_path, word_list_path), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, bufsize=1, text=True)
        lines = []
        back_up_lines = []

        while aircrack.poll() is None:
            line = aircrack.stdout.readline()
            lines.append(line.strip())
            print(len(lines))
            if len(lines) == 500:
                back_up_lines = lines.copy()
                lines.clear()

        key = self.get_key(lines, back_up_lines)

        password = key[key.find("[") + 2:-2]
        print(password)


a = Aircrack()
a.run_aircrack("./known_pass.cap", "./test.txt")
