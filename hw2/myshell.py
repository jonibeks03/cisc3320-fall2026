import os
import shlex
import signal

job_list = {}
next_job = 1


def update_jobs():
    for job_id in list(job_list.keys()):
        process_id = job_list[job_id]["pid"]

        try:
            finished, status = os.waitpid(process_id, os.WNOHANG)

            if finished != 0:
                job_list[job_id]["status"] = "Done"

        except ChildProcessError:
            job_list[job_id]["status"] = "Done"


def print_jobs():
    for job_id in job_list:
        print(
            "[" + str(job_id) + "]",
            job_list[job_id]["status"],
            job_list[job_id]["command"]
        )


def start_command(command_parts, command_name, is_background):
    global next_job

    process_id = os.fork()

    if process_id == 0:
        try:
            os.execvp(command_parts[0], command_parts)

        except FileNotFoundError:
            print(
                "myshell:",
                command_parts[0],
                ": command not found",
                flush=True
            )
            os._exit(1)

    else:
        if is_background:

            job_list[next_job] = {
                "pid": process_id,
                "command": command_name,
                "status": "Running"
            }

            print(
                "[" + str(next_job) + "]",
                process_id,
                command_name
            )

            next_job = next_job + 1

        else:
            os.waitpid(process_id, 0)


def move_to_foreground(job_id):

    if job_id not in job_list:
        print("myshell: job does not exist")
        return

    print(job_list[job_id]["command"])

    process_id = job_list[job_id]["pid"]

    try:
        os.waitpid(process_id, 0)

    except ChildProcessError:
        pass

    del job_list[job_id]


def end_job(job_id):

    if job_id not in job_list:
        print("myshell: job does not exist")
        return

    process_id = job_list[job_id]["pid"]

    try:
        os.kill(process_id, signal.SIGTERM)
        os.waitpid(process_id, 0)

    except:
        pass

    print(
        "[" + str(job_id) + "] Terminated",
        job_list[job_id]["command"]
    )

    del job_list[job_id]


while True:

    update_jobs()

    try:
        command_line = input("myshell> ")

    except KeyboardInterrupt:
        print()
        continue

    except EOFError:
        break

    command_line = command_line.strip()

    if command_line == "":
        continue

    try:
        command_parts = shlex.split(command_line)

    except:
        print("myshell: could not read command")
        continue

    is_background = False

    if command_parts[-1] == "&":
        is_background = True
        command_parts.pop()

    if len(command_parts) == 0:
        continue

    command_name = " ".join(command_parts)


    if command_parts[0] == "exit":
        break


    elif command_parts[0] == "cd":

        if len(command_parts) == 1:
            os.chdir(os.environ["HOME"])

        else:
            try:
                os.chdir(command_parts[1])

            except:
                print("myshell: folder not found")


    elif command_parts[0] == "jobs":

        print_jobs()


    elif command_parts[0] == "fg":

        if len(command_parts) < 2:
            print("myshell: enter job number")

        else:
            try:
                job_id = int(command_parts[1])
                move_to_foreground(job_id)

            except:
                print("myshell: invalid job number")


    elif command_parts[0] == "kill":

        if len(command_parts) < 2:
            print("myshell: enter job number")

        else:
            try:
                job_id = int(command_parts[1])
                end_job(job_id)

            except:
                print("myshell: invalid job number")


    else:

        start_command(
            command_parts,
            command_name,
            is_background
        )

