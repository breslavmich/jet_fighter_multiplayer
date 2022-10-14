# Michael Breslavsky - 12A
# 14.10.2022
# File: chatlib.py
# Description: Dictionaries and functions to format and parse messages and data.

# Protocol Constants
CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message
END_OF_MESSAGE = '$'

# Protocol Messages
# In this dictionary we will have all the client and server command names
PROTOCOL_CLIENT = {
    "disconnect_msg": "DISCONNECT",
    "initial_details": "GET_GAME_DATA",
    "game_status_request": "GET_STATUS",
    "shoot_command": "SHOOT",
    "key_down_msg": "KEY_PRESSED",
    "key_up_msg": "KEY_RELEASED"
}

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "error_msg": "ERROR",
    "connection_limit": "MAX_CONNECTED",
    'winner_msg': "WINNER",
    "connected_successfully": "CONNECT_SUCCESS",
    "ok_msg": "OK",
    "game_starting_message": "GAME_STARTING",
    "game_status_response": "STATUS_RESPONSE",
    "initial_data_response": "START_DATA"
}

# Other constants
ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd: str, data: str) -> str or None:
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occurred
    """
    if len(cmd) >= CMD_FIELD_LENGTH or len(data) >= MAX_DATA_LENGTH:
        # Checking if received parameters are of allowed length
        return None
    while len(cmd) < CMD_FIELD_LENGTH:
        cmd += ' '
    data_len = str(len(data)).zfill(LENGTH_FIELD_LENGTH)
    full_msg = DELIMITER.join((cmd, data_len, data))
    return full_msg


def parse_message(data: str) -> tuple:
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    lst = data.split(DELIMITER)
    if len(lst) != 3:
        print(1)
        return None, None
    cmd, expected_data_len, msg = lst
    if len(cmd) != CMD_FIELD_LENGTH or len(expected_data_len) != LENGTH_FIELD_LENGTH:
        return None, None
    try:
        expected_data_len = int(expected_data_len)
    except Exception as e:
        print(3)
        return None, None
    if expected_data_len != len(msg):
        print(4)
        return None, None
    cmd = cmd.replace(' ', '')
    return cmd, msg


def split_data(msg: str, expected_fields: int) -> list:
    """Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occurred, returns None"""
    lst = msg.split(DATA_DELIMITER)  # Splitting the data into a list
    if len(lst) != expected_fields + 1:  # Checking if expected value matches list length
        return [None]
    return lst


def join_data(msg_fields: list) -> str:
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    str_lst = [str(x) for x in msg_fields]  # Converting all list values to string
    st = DATA_DELIMITER.join(str_lst)  # Joining the list into a string
    return st
