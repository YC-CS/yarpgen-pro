import os
import shutil
import zipfile

from utils import *
from StateEnum import State
from StateEnum import state_to_str
from StateEnum import Language


# 语言设置
language = Language.cpp

# 代码生成器的可执行文件路径
GENERATOR_ELF = '/home/workspace/yarpgen-pro/build/yarpgen'

# 测试文件夹路径
TEST_PATH = '/home/workspace/Testing/'

# 库的路径
LIB_PATH = '/home/workspace/CompilerTestingRunner/lib/'

TIME_STR = get_current_time_str()
TEST_FOLDER = TEST_PATH + 'Testing-' + TIME_STR + '/'

GENERATOR_OUTPUT_FOLDER = TEST_FOLDER + 'cases/'
BACKUP_FOLDER = TEST_FOLDER + 'backup/'
LOG_FOLDER = TEST_FOLDER + 'log/'

if not os.path.exists(TEST_FOLDER):
    os.makedirs(TEST_FOLDER)

if not os.path.exists(GENERATOR_OUTPUT_FOLDER):
    os.makedirs(GENERATOR_OUTPUT_FOLDER)

if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)


def generator_runner(test_num: int = 1):

    global GENERATOR_ELF, GENERATOR_OUTPUT_FOLDER

    if not os.path.exists(GENERATOR_ELF):
        raise ValueError('You must have a legal generator elf')

    if not os.path.exists(GENERATOR_OUTPUT_FOLDER):
        raise ValueError('You should have a legal generator output root')

    if language == Language.c:
        file_ext = '.c'
    else:
        file_ext = '.cpp'

    for i in range(test_num):
        output_file = GENERATOR_OUTPUT_FOLDER + TIME_STR + '--' + str(i+1) + file_ext
        print("generating " + output_file)
        cmd = GENERATOR_ELF + " -o " + output_file
        os.system(cmd)

def compile_elf(compile_cmd: str):
    global GENERATOR_OUTPUT_FOLDER

    try:
        print("COMPILE: " + compile_cmd)
        ret, _, _ = run_cmd(compile_cmd.split(' '), GENERATOR_OUTPUT_FOLDER, 30)
    except subprocess.TimeoutExpired:
        print("COMPILER TIMEOUT: {}".format(compile_cmd))
        return State.COMPILE_TIMEOUT
    else:
        if ret != 0:
            print("COMPILER CRASH BY CMD: {}".format(compile_cmd))
            return State.COMPILE_CRASH
        else:
            return State.COMPILE_SUCC


def execute_elf(elf_name: str):
    global GENERATOR_OUTPUT_FOLDER
    try:
        exe_cmd = './' + elf_name
        print("RUN TEST: " + exe_cmd)
        ret, stdout, stderr = run_cmd([exe_cmd], GENERATOR_OUTPUT_FOLDER, 30)
    except subprocess.TimeoutExpired:
        print("GENERATED DEAD-LOOP FILE: {}".format(elf_name))
        return State.EXECUTION_TIMEOUT, state_to_str(State.EXECUTION_TIMEOUT)

    if ret != 0:
        print("EXECUTABLE CRASH: {}".format(elf_name))
        return State.EXECUTION_CRASH, state_to_str(State.EXECUTION_CRASH)
    else:
        checksum = stdout[0]
        return State.EXECUTION_SUCC, checksum


def backup_file(case_name: str):
    global BACKUP_FOLDER, GENERATOR_OUTPUT_FOLDER
    output = BACKUP_FOLDER + case_name
    if not os.path.exists(output):
        shutil.copyfile(GENERATOR_OUTPUT_FOLDER + case_name, BACKUP_FOLDER + case_name)


def process_compiler(compilers: list, options: list):
    global GENERATOR_OUTPUT_FOLDER , LOG_FOLDER

    # for each test case
    files = os.listdir(GENERATOR_OUTPUT_FOLDER)
    sorted_files = sorted(files, key=filename_sort_key)

    for case_file in sorted_files:
        if not (case_file.endswith('.c') or case_file.endswith('.cpp')):
            continue
        execution_res = {}
        compilation_timeout_files = {}
        execution_timeout_files = {}
        compiler_internal_error = {}
        compiler_opt_error = {}
        tail = TIME_STR + '.txt'

        checksum_array = []
        diff_file = LOG_FOLDER + case_file + '.diff'

        cie_file = LOG_FOLDER + 'CIE-' + tail  # compiler_internal_error
        ct_file = LOG_FOLDER + 'CT-' + tail  # compiler_timeout
        coe_file = LOG_FOLDER + 'COE-' + tail  # compiler_opt_error
        et_file = LOG_FOLDER + 'ET-' + tail  # execution_timeout
        er_file = LOG_FOLDER + 'LOG-' + tail  # execution_res

        for compiler in compilers:
            for opt in options:
                elf_name = case_name_to_elf_name(compiler, case_file, opt)
                compile_cmd = compiler + ' -I ' + LIB_PATH + ' -' + opt + " " + case_file + ' -o ' + elf_name

                compile_state = compile_elf(compile_cmd)

                if compile_state == State.COMPILE_TIMEOUT:
                    write_file(compile_cmd + '\n', ct_file)
                    insert_to_dict(case_file, compilation_timeout_files, elf_name)
                    #backup_file(case_file)
                    continue
                elif compile_state == State.COMPILE_CRASH:
                    insert_to_dict(case_file, compiler_internal_error, elf_name)
                    write_file(compile_cmd + '\n', cie_file)

                    cie_log = LOG_FOLDER + "log-cie-" + compiler + case_file + "-" + opt + '.txt'
                    process = subprocess.Popen(compile_cmd, cwd=GENERATOR_OUTPUT_FOLDER, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    output, errors = process.communicate()
                    log_string = "output:" + output + '\n' + "error:" + errors
                    write_file(log_string, cie_log)

                    backup_file(case_file)
                    continue

                execute_state, ret_val = execute_elf(elf_name)
                # record all
                write_file(compile_cmd + ' -> ' + ret_val + '\n', er_file)
                # process state
                if execute_state == State.EXECUTION_SUCC:
                    if case_file not in execution_res:
                        execution_res[case_file] = []
                    elf_and_checksum = (elf_name, ret_val)
                    # compare with timeout historical results
                    if case_file in execution_timeout_files:
                        print("{} OPT ERROR {} AT {}, "
                              "both timeout and checksum are generated!".format(compiler, case_file, opt))
                        insert_to_dict(case_file, compiler_opt_error, elf_name)
                        write_file(compile_cmd + ' -> ' + ret_val + '\n', coe_file)
                        #backup_file(case_file)
                    # compare with historical results
                    for (k, v) in execution_res[case_file]:
                        if ret_val != v:
                            print("{} OPT ERROR {} AT {}!".format(compiler, case_file, opt))
                            insert_to_dict(case_file, compiler_opt_error, elf_name)
                            write_file(compile_cmd + ' -> ' + ret_val + '\n', coe_file)
                            backup_file(case_file)
                    execution_res[case_file].append(elf_and_checksum)
                    checksum_array.append(ret_val)

                elif execute_state == State.EXECUTION_TIMEOUT:
                    insert_to_dict(case_file, execution_timeout_files, elf_name)
                    write_file(compile_cmd + '\n', et_file)
                    # compare with timeout historical results
                    if case_file in execution_res:
                        print("{} OPT ERROR {} AT {}, "
                              "both timeout and checksum are generated!".format(compiler, case_file, opt))
                        insert_to_dict(case_file, compiler_opt_error, elf_name)
                        write_file(compile_cmd + ' -> EXECUTION_TIMEOUT\n', coe_file)
                        #backup_file(case_file)
                elif execute_state == State.EXECUTION_CRASH:
                    insert_to_dict(case_file, compiler_opt_error, elf_name)
                    write_file(compile_cmd + ' -> EXECUTION_CRASH\n', coe_file)

                    gdb_cmd = "gdb -q -batch -ex \"run\" -ex \"bt\" ./" + elf_name
                    crash_log = LOG_FOLDER + "log-crash-" + compiler + case_file + "-" + opt + '.txt'
                    process = subprocess.Popen(gdb_cmd, cwd=GENERATOR_OUTPUT_FOLDER,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
                    output, errors = process.communicate()
                    log_string = "output:" + output + '\n' + "error:" + errors
                    write_file(log_string, crash_log)

                    backup_file(case_file)
        # compare all checksum

        print("comparing checksum from:{}\n".format(case_file))
            # if the checksums are not all same
        if len(checksum_array) != 0:
            if len(set(checksum_array)) != 1:
                print("find checksum difference in {}".format(case_file))
                for checksum in checksum_array:
                    write_file(str(checksum)+"\n", diff_file)
                backup_file(case_file)



def compile_and_execute():
    if language == Language.c:
        compilers = ['clang', 'gcc']
    elif language == Language.cpp:
        compilers = ['clang++', 'g++']
    else :
        raise ValueError('You should choose a supported language')

    options = []
    for level in range(0, 4):
        options.append('O' + str(level))
    process_compiler(compilers, options)


def move_and_compress():
    global GENERATOR_OUTPUT_FOLDER , TEST_FOLDER , BACKUP_FOLDER , LOG_FOLDER

    for ELF_file in os.listdir(GENERATOR_OUTPUT_FOLDER):
        ELF_path = GENERATOR_OUTPUT_FOLDER + ELF_file
        if 'ELF' in ELF_file :
            os.remove(ELF_path)
            continue

    zip_name = TEST_PATH + 'Testing-' + TIME_STR + ".zip"
    zip = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(TEST_FOLDER):
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, file)
            # 将文件写入ZIP文件
            zip.write(file_path, os.path.relpath(file_path, TEST_FOLDER))
    print('zip done')



if __name__ == '__main__':
    generator_runner(100)
    compile_and_execute()
    move_and_compress()

