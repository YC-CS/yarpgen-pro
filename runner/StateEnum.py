from enum import Enum


def state_to_str(state: int):
    if state == State.COMPILE_SUCC:
        return 'COMPILE_SUCC'
    elif state == State.COMPILE_TIMEOUT:
        return 'COMPILE_TIMEOUT'
    elif state == State.COMPILE_CRASH:
        return 'COMPILE_CRASH'
    elif state == State.EXECUTION_SUCC:
        return 'EXECUTION_SUCC'
    elif state == State.EXECUTION_TIMEOUT:
        return 'EXECUTION_TIMEOUT'
    elif state == State.EXECUTION_CRASH:
        return 'EXECUTION_CRASH'
    else:
        raise ValueError('State should in [1, 6] ' + state)


class State(Enum):
    COMPILE_SUCC = 1
    COMPILE_TIMEOUT = 2
    COMPILE_CRASH = 3
    EXECUTION_SUCC = 4
    EXECUTION_TIMEOUT = 5
    EXECUTION_CRASH = 6
