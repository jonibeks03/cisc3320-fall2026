import os
import shlex
import signal

jobs = {}
jid = 1


def check():
    while True:
        try:
            pid, stat = os.waitpid(-1, os.WNOHANG)

            if pid == 0:
                break

            for n in jobs:
                if jobs[n]["pid"] == pid:
                    jobs[n]["stat"] = "Done"
                    break

        except ChildProcessError:
            break


def show():
    for n in jobs:
        print("[" + str(n) + "]", jobs[n]["stat"], jobs[n]["cmd"])


def run(parts, cmd, bg):
    global jid

    pid = os.fork()

    if pid == 0:
        try:
            os.execvp(parts[0], parts)

        except FileNotFoundError:
            print("command not found", flush=True)
            os._exit(1)

    else:
        if bg:
            jobs[jid] = {
                "pid": pid,
                "cmd": cmd,
                "stat": "Running"
            }

            print("[" + str(jid) + "]", pid, cmd)
            jid = jid + 1

        else:
            os.waitpid(pid, 0)


def fg(n):
    if n not in jobs:
        print("job not found")
        return

    print(jobs[n]["cmd"])

    if jobs[n]["stat"] == "Done":
        del jobs[n]
        return

    pid = jobs[n]["pid"]

    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass

    del jobs[n]


def stop(n):
    if n not in jobs:
        print("job not found")
        return

    pid = jobs[n]["pid"]

    try:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except:
        pass

    print("Terminated", jobs[n]["cmd"])

    del jobs[n]


while True:

    check()

    try:
        line = input("myshell> ")

    except KeyboardInterrupt:
        print()
        continue

    except EOFError:
        break

    line = line.strip()

    if line == "":
        continue

    try:
        parts = shlex.split(line)

    except:
        print("bad command")
        continue

    bg = False

    if parts[-1] == "&":
        bg = True
        parts.pop()

    if len(parts) == 0:
        continue

    cmd = " ".join(parts)

    if parts[0] == "exit":
        break

    elif parts[0] == "cd":

        if len(parts) == 1:
            os.chdir(os.environ["HOME"])

        else:
            try:
                os.chdir(parts[1])
            except:
                print("folder not found")

    elif parts[0] == "jobs":
        show()

    elif parts[0] == "fg":

        if len(parts) < 2:
            print("enter job number")

        else:
            try:
                n = int(parts[1])
                fg(n)
            except:
                print("bad job number")

    elif parts[0] == "kill":

        if len(parts) < 2:
            print("enter job number")

        else:
            try:
                n = int(parts[1])
                stop(n)
            except:
                print("bad job number")

    else:
        run(parts, cmd, bg)

