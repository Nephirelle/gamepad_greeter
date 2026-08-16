import os
import socket
import json
import sys
import importlib

class UserService:
    def __init__(self, users : list = None):
        self.__users = users

    def get_users(self):
        if self.__users:
            return self.__users

        try:
            pwd = importlib.import_module('pwd')
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError("pwd module not found. Probably not running on Linux.") from e

        self.__users = []

        for user in pwd.getpwall():
            if 1000 <= user.pw_uid < 6000:
                self.__users.append(user.pw_name)
                
        return self.__users

class AuthenticationService:
    def __init__(self): ...
    def init(self): ...
    def create_session(self, username : str): ...
    def send_password(self, password : str): ...
    def start_session(self, cmd : list[str], env : list[str]): ...
    def cancel_session(self): ...

class GreetdAuthenticationService(AuthenticationService):
    def __init__(self):
        self.__client = None

    def init(self):
        greetd_socket = os.getenv("GREETD_SOCK")
        self.__client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__client.connect(greetd_socket)

    def create_session(self, username : str) -> dict[str, str]:
        req = {"type": "create_session", "username": username}
        res = self.__send_and_receive(req)
        return res

    def send_password(self, password : str) -> dict[str, str]:
        req = {"type": "post_auth_message_response", "response": password}
        res = self.__send_and_receive(req)
        return res

    # "cmd": ["startxfce4"], "env": []
    def start_session(self, cmd : list[str], env : list[str]) -> dict[str, str]:
        req = {"type": "start_session", "cmd": cmd, "env": env}
        res = self.__send_and_receive(req)
        return res

    def cancel_session(self) -> dict[str, str]:
        req = {"type": "cancel_session"}
        res = self.__send_and_receive(req)
        return res

    def __send_and_receive(self, json_request : dict[str, str]) -> dict[str, str]:
        req_payload = json.dumps(json_request).encode("utf-8")
        req_header = len(req_payload).to_bytes(4, sys.byteorder)

        self.__client.send(req_header + req_payload)

        res_header = self.__client.recv(4)
        if not res_header:
            return None
        
        res_payload_length = int.from_bytes(res_header, sys.byteorder, signed=False)
        res_payload = self.__client.recv(res_payload_length)
        res_json = json.loads(res_payload.decode("utf-8"))

        if "type" not in res_json or res_json["type"] == "error":
            error_type = res_json["error_type"] if "error_type" in res_json else ""
            description = res_json["description"] if "description" in res_json else ""

            err_msg = f"Error message received. Error Type: {error_type} - {description}"
            print(err_msg)
            raise Exception(err_msg) 

        return res_json