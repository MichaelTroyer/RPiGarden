from subprocess import Popen

filename = 'main.py'

while True:
    print(f'Starting Process: {filename}')
    p = Popen(f'python {filename}', shell=True)
    p.wait()