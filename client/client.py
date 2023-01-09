import socket

SERVER_PORT = 12345
BUFFER_SIZE = 1024
VIDEO_PATH = "client_video.mp4"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", SERVER_PORT))

client.send(b"%VIDEO_ENVIO%")

with open(VIDEO_PATH, "rb") as file:
	file_data = file.read(BUFFER_SIZE)

	while file_data:
		client.send(file_data)
		file_data = file.read(BUFFER_SIZE)

client.send(b"%VIDEO_ENVIADO%")