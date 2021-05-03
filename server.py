import socket as so

s = so.socket()
port = 42069

s.bind(('', port))
s.listen(5)

#data = control.getsend()
def listen():
    while True:
        try:
            data = c.recv(1024)
            if not data:
                raise
            print(data)
        except:
            print('closed')
            c.close()
            break
while True:
    c, addr = s.accept()
    print(f'connected from {addr}')
    listen()
