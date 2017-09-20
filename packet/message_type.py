from enum import Enum


class GNRSMessageType(Enum):
    EMPTY = 0
    SIGNUP = 1
    SIGNUP_REPLY = 2
    QUERY_REQUEST = 3
    QUERY_REPLY = 4
    GUID_NA_UPDATE = 5
    GUID_NA_UPDATE_REPLY = 6
