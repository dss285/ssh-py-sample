from paramiko import SSHClient, AutoAddPolicy
import re

client = SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(AutoAddPolicy)
client.connect(hostname='127.0.0.1', username='', password='')
stdin, stdout, stderr = client.exec_command('df -h')
reg = re.compile(r"/dev/sd[a-z]\d")
lines = []
for line in stdout.readlines():
    if reg.match(line):
        lines.append(line)

print(lines)

client.close()