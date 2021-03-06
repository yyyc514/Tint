import os
import sublime
import subprocess
import threading
import time

SHELL_ERROR = "TINT: Could not run your shell: {}\n"


class CommandRunner():
    def __init__(self, working_dir):
        self.working_dir = working_dir

    def build_command(self, string):
        settings = sublime.load_settings("Tint.sublime-settings")
        shell = settings.get("shell")
        # for k, v in os.environ.items():
        #     print("{}: {}".format(k,v))
        if shell == "zsh":
            args = ("-l", "-c")
            prefix = "([[ -f ~/.zshrc ]] && source ~/.zshrc); "
        elif shell == "bash":
            args = ("-l", "-c")
            prefix = ""
        else:
            args = ("-c", )
            prefix = ""
            pass

        cmd = (shell,) + args + (prefix + string, )
        print(cmd)
        return cmd

    def watch(self, process):
        time.sleep(10)
        if process.poll() == None:
            process.kill()

    def run(self, string, stdin=None):
        command = self.build_command(string)
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        env = os.environ.copy()

        settings = sublime.load_settings("Tint.sublime-settings")
        my_env = settings.get("env")
        env.update(my_env)

        try:
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=self.working_dir,
                                 env=env,
                                 startupinfo=startupinfo)
            watcher = threading.Thread(target=self.watch, args=(p,))
            watcher.start()

            stdout, stderr = p.communicate(stdin.encode(encoding="UTF-8") if stdin else None)
            stdout, stderr = stdout.decode(), stderr.decode()

        except Exception as e:
            print(e)
            return "", SHELL_ERROR.format(e.args[1])

        return stdout, stderr

