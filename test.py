from paramiko import SSHClient, AutoAddPolicy
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
def disk_space(client : SSHClient):
    stdin, stdout, stderr = client.exec_command('df -h')
    reg = re.compile(r"/dev/sd[a-z]\d")
    lines = []
    for line in stdout.readlines():
         if reg.match(line):
             lines.append(line)

    return "\n".join(lines)

def docker_ps(client : SSHClient):
    stdin, stdout, stderr = client.exec_command('docker ps')
    lines = []
    for line in stdout.readlines():
        lines.append(line)

    return "\n".join(lines)


username = ''
password = ''

hosts = [
    '',
]
clients = []
for host in hosts:
    tmp = SSHClient()
    tmp.load_system_host_keys()
    tmp.set_missing_host_key_policy(AutoAddPolicy)
    tmp.connect(hostname=host, username=username, password=password)
    clients.append(tmp)

with ThreadPoolExecutor(max_workers=len(hosts)) as pool:
    tasks = []
    for x in clients:
        tasks.append(pool.submit(disk_space, x))
        tasks.append(pool.submit(docker_ps, x))
    for x in as_completed(tasks):
        print(x.result())

for x in clients:
    x.close()