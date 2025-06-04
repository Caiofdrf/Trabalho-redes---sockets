import socket
import threading

HOST = "0.0.0.0"
PORT = 2077
msg_max_len = 1024

clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_socket):
    with clients_lock:
        for client in clients:
            if client is sender_socket:
                continue
            try:
                client.send(message)
            except:
                try:
                    client.close()
                except:
                    pass
                clients.remove(client)

def player_handler(player_socket, address):
    while True:
        try:
            data = player_socket.recv(msg_max_len)
            if not data:
                print("Erro, dados recebidos vazios")
            text = data.decode('utf-8').strip()
            if text.startswith("CURRENT:") or text.startswith("BOARD:"):
                broadcast(data, player_socket)
            else:
                print(f"Mensagem inesperada de {address}: {repr(text)}")
        except:
            with clients_lock:
                if player_socket in clients:
                    clients.remove(player_socket)
            try:
                player_socket.close()
            except:
                pass
            break

def main():
    # IPv4 e TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        player_socket, address = server.accept()
        print("Player novo conectado")

        with clients_lock:
            clients.append(player_socket)
        thread = threading.Thread(target=player_handler,args=(player_socket, address),daemon=True)
        thread.start()

if __name__ == "__main__":
    main()
