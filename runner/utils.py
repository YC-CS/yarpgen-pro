import subprocess
import tempfile
import traceback
import time
import datetime


def run_cmd(command: list, working_dir: str, timeout: int = 5):
    try:
        stdout_tmp = tempfile.SpooledTemporaryFile(buffering=16384)
        stderr_tmp = tempfile.SpooledTemporaryFile(buffering=1024)
        stdout_fileno = stdout_tmp.fileno()
        stderr_fileno = stderr_tmp.fileno()
        p = subprocess.Popen(command, cwd=working_dir, stdout=stdout_fileno, stderr=stderr_fileno, shell=False, close_fds=True)

        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()
                raise subprocess.TimeoutExpired(' '.join(command), timeout)
            time.sleep(0.1)
        # return p.stdout.read()

        stdout_tmp.seek(0)
        stdout = stdout_tmp.readlines()
        stdout = [x.decode('utf-8').strip() for x in stdout]

        stderr_tmp.seek(0)
        stderr = stderr_tmp.readlines()
        stderr = [x.decode('utf-8').strip() for x in stderr]
        return p.returncode, stdout, stderr

    except IOError:
        print(traceback.format_exc())
        return -1, [], []
    finally:
        if stdout_tmp:
            stdout_tmp.close()
        if stderr_tmp:
            stderr_tmp.close()


def get_current_time_str():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, '%Y-%m-%d-%H-%M')


def write_file(line: str, path: str, mode: str = 'a'):
    with open(path, mode) as file:
        file.write(line)


def dict_compare(d1: dict, d2: dict):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same



def case_name_to_elf_name(compiler: str, case_file: str, opt: str):
    return 'ELF-' + compiler.upper() + '-' + case_file + '--' + opt


def insert_to_dict(key: str, mapping: dict, new_value):
    if key not in mapping:
        mapping[key] = []
    mapping[key].append(new_value)

def filename_sort_key(filename):
    serial_number = filename.split('--')[-1].split('.')[0]
    return int(serial_number)