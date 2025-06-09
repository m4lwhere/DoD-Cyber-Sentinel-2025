import socket
import threading

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 23       # Port for the telnet server
WELCOME_BANNER = b"""
***************************************************
** Welcome to the Unsecured Telnet Server!       **
** This is for authorized personnel only.        **
***************************************************
\r\n"""
PROMPT_PASSWORD = b"Enter the secret password to proceed: "
SECRET_PASSWORD = "password123"
LOGIN_SUCCESS = b"\r\nAccess Granted. Welcome, admin.\r\nType 'help' for a list of commands.\r\n"
LOGIN_FAILURE = b"\r\nIncorrect password. Connection terminated.\r\n"

# --- Fake Filesystem for the CTF ---
FAKE_FILES = {
    "users.txt": b"root\r\nadmin\r\njane\r\n",
    "secret_flag.txt": b"FLAG: C1{c1e4rT3xt_Is_B4d_And_N0w_Y0u_Kn0w!}\r\n",
}

HELP_MESSAGE = b"""
Available commands:
  help          - Show this help message
  ls            - List files in the current directory
  cat [file]    - Display the contents of a file
  exit          - Terminate the connection
\r\n"""

def handle_client(client_socket):
    """
    Handles an interactive client session.
    """
    try:
        # --- Stage 1: Authentication ---
        client_socket.sendall(WELCOME_BANNER)
        client_socket.sendall(PROMPT_PASSWORD)

        # Read a single line for the password
        data = client_socket.recv(1024)
        password = data.decode('utf-8', errors='ignore').strip()

        if password != SECRET_PASSWORD:
            client_socket.sendall(LOGIN_FAILURE)
            print(f"Failed login attempt from {client_socket.getpeername()}")
            return # This terminates the thread and the connection

        client_socket.sendall(LOGIN_SUCCESS)
        print(f"Successful login from {client_socket.getpeername()}")

        # --- Stage 2: Interactive Shell ---
        while True:
            client_socket.sendall(b"admin@server> ")
            # Wait for the next command
            command_data = client_socket.recv(1024)
            if not command_data:
                # Client disconnected
                break
            
            command = command_data.decode('utf-8', errors='ignore').strip()
            print(f"Received command '{command}' from {client_socket.getpeername()}")

            if command.lower() == "exit":
                break
            elif command.lower() == "help":
                client_socket.sendall(HELP_MESSAGE)
            elif command.lower() == "ls":
                files_list = "\r\n".join(FAKE_FILES.keys())
                client_socket.sendall(files_list.encode() + b"\r\n\r\n")
            elif command.lower().startswith("cat "):
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    filename = parts[1].strip()
                    if filename in FAKE_FILES:
                        client_socket.sendall(FAKE_FILES[filename] + b"\r\n")
                    else:
                        client_socket.sendall(f"cat: {filename}: No such file or directory\r\n".encode())
                else:
                    client_socket.sendall(b"Usage: cat [filename]\r\n")
            elif command: # If command is not empty
                client_socket.sendall(f"Command not found: {command}\r\n".encode())

    except (ConnectionResetError, BrokenPipeError):
        print(f"Client {client_socket.getpeername()} disconnected unexpectedly.")
    except Exception as e:
        print(f"An error occurred with client {client_socket.getpeername()}: {e}")
    finally:
        print(f"Closing connection with {client_socket.getpeername()}.")
        client_socket.close()

def main():
    """
    Main function to start the telnet server.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] Interactive telnet server listening on {HOST}:{PORT}")

        while True:
            client_sock, address = server.accept()
            print(f"[*] Accepted connection from: {address[0]}:{address[1]}")
            client_handler = threading.Thread(target=handle_client, args=(client_sock,))
            client_handler.start()

    except KeyboardInterrupt:
        print("\n[*] Server is shutting down.")
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()

