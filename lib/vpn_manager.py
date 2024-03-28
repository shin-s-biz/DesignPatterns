import os
import subprocess
import re
import time

# Exception
class NordVpnNotFoundError(Exception):
    def __init__(self):
        message = "VPN Error : The nordvpn command is not available."
        super().__init__(message)
        self.code = 1000

class NordVpnNotLoginError(Exception):
    def __init__(self):
        message = "VPN Error : You are not logged into NordVPN."
        super().__init__(message)
        self.code = 1001

class NordVpnConnectionError(Exception):
    def __init__(self):
        message = "VPN Error : Failed to connect to NordVPN."
        super().__init__(message)
        self.code = 1002

class NordVpnDisconnectionError(Exception):
    def __init__(self):
        message = "VPN Error : Failed to disconnect from NordVPN."
        super().__init__(message)
        self.code = 1002

# Class
class NordVPN():
    def __init__(self):
        nordvpn_bin = '/usr/bin/nordvpn'
        if not os.path.exists(nordvpn_bin):
            raise NordVpnNotFoundError

        self.nordvpn_info = {
            'server_id': '',
            'ip_addr': ''
        }

    def run(self, command: list) -> tuple[list, list]:
        print("Execute ==> %s" % ' '.join(command))
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.splitlines(), result.stderr.splitlines()

    def account(self):
        command = ['nordvpn', 'account']
        stdout_lines, stderr_lines = self.run(command)

        if any('VPN Service: Active' in item for item in stdout_lines):
            print("NordVPN Login OK")
        else:
            raise NordVpnNotLoginError

    def status(self) -> bool:
        command = ['nordvpn', 'status']
        stdout_lines, stderr_lines = self.run(command)

        if any('Status: Connected' in item for item in stdout_lines):
            print("NordVPN Connected")

            for line in stdout_lines:
                if 'Hostname' in line:
                    server_id_pattern = r'Hostname:\s+(.+)\.nordvpn\.com'
                    self.nordvpn_info['server_id'] = re.search(server_id_pattern, line).group(1)

            curl_command = ['curl', '-s', 'ifconfig.me']
            curl_stdout_lines, curl_stderr_lines = self.run(curl_command)

            for curl_line in curl_stdout_lines:
                ip_addr_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
                if re.match(ip_addr_pattern, curl_line):
                    self.nordvpn_info['ip_addr'] = re.search(ip_addr_pattern, curl_line).group()
                    print(self.nordvpn_info['ip_addr'])

            return True

        else:
            print("NordVPN Not Connected")
            return False

    def connect(self, dest_server: str = 'jp', max_retry_count: int = 5, retry_interval: int = 15):
        self.account()
        command = ['nordvpn', 'connect', dest_server]

        for count in range(max_retry_count):
            stdout_lines, stderr_lines = self.run(command)

            if any('You are connected' in item for item in stdout_lines):
                print("NordVPN Connection Success")
                self.status()
                return True

            else:
                print("Retry Count : %s / %s" % (str(count + 1), str(max_retry_count)))
                time.sleep(retry_interval)

        raise NordVpnConnectionError

    def disconnect(self):
        command = ['nordvpn', 'disconnect']
        stdout_lines, stderr_lines = self.run(command)

        if any('You are disconnected' in item for item in stdout_lines):
            print("NordVPN Disconnected")

        elif any('Connected' in item for item in stdout_lines):
            print("NordVPN Not Connected")

        else:
            raise NordVpnDisconnectionError
