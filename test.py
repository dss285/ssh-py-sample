from paramiko import SSHClient, AutoAddPolicy
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
class ClientWrapper:
    def __init__(self, client : SSHClient, extra_info : dict):
        self._ssh_client = client
        self._extra_info = extra_info

        if not self._extra_info:
            self._extra_info = {}
    def disk_space(self):
        stdin, stdout, stderr = self._ssh_client.exec_command('df -h')
        reg = re.compile(r"/dev/sd[a-z]\d")
        lines = []
        for line in stdout.readlines():
             if reg.match(line):
                 lines.append(line)

        return "\n".join(lines)


    def docker_ps(self):
        stdin, stdout, stderr = self._ssh_client.exec_command('docker ps')
        lines = []
        for line in stdout.readlines():
            lines.append(line)
        return "\n".join(lines)

    def psql(self, command):
        print(f'docker exec dockercontainer psql \"postgresql://user:pass@host/dbname\" -c "{command}"')
        stdin, stdout, stderr = self._ssh_client.exec_command(f'docker exec dockercontainer psql "postgresql://user:pass@host/dbname" -c "{command}"')
        lines = []
        for line in stdout.readlines():
            lines.append(line)
        return "\n".join(lines)

    def close(self):
        self._ssh_client.close()

    def __getitem__(self, item):
        return self._extra_info[item]

    def get_custom_name(self):
        return self["custom_name"]


user = ''
passphrase = ''
key_file = ''

hosts = [
    ('', user, passphrase, key_file, ''),
]
clients = []
for host, username, password, key_file_path, custom_name in hosts:
    tmp = SSHClient()
    tmp.load_system_host_keys()
    tmp.set_missing_host_key_policy(AutoAddPolicy)
    tmp.connect(hostname=host, username=username, password=password, key_filename=key_file_path)

    clientWrapper = ClientWrapper(tmp, {
        "host" : host,
        "username" : username,
    })

    clients.append(clientWrapper)

with ThreadPoolExecutor(max_workers=len(hosts)) as pool:
    tasks = []
    for x in clients:
        tasks.append(pool.submit(x.disk_space))
        tasks.append(pool.submit(x.docker_ps))
        tasks.append(pool.submit(x.psql, "SELECT 1;"))
        tasks.append(pool.submit(x.psql, 'SELECT * FROM \\"X\\".\\"X\\";'))
    for x in as_completed(tasks):
        print(x.result())

for x in clients:
    x.close()