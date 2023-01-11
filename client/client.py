import socket

SERVER_PORT = 12345
BUFFER_SIZE = 4096
VIDEO_PATH = "client_video.mp4"
EDITED_VIDEO_PATH = "edited_client_video.mp4"

def recieveBytes(msg_length, connection):
    chunks = []
    bytes_to_recv = msg_length
    while bytes_to_recv:
        chunk = connection.recv(bytes_to_recv)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_to_recv -= len(chunk)
    return b''.join(chunks)

def sendVideoToServer(connection, videoFilePath):
	connection.send(b"%VIDEO_ENVIO%")

	with open(videoFilePath, "rb") as file:
		fileLength = file.seek(0, 2)
		file.seek(0, 0)

		imageLengthBytes = fileLength.to_bytes(4, "big")

		connection.sendall(imageLengthBytes)
		
		data = file.read(BUFFER_SIZE)

		while len(data):
			connection.sendall(data)
			data = file.read(BUFFER_SIZE)

def recieveVideoFromServer(connection, videoFilePath):
	while True:
		imageLengthBytes = recieveBytes(4, connection)
		imageLength = int.from_bytes(imageLengthBytes, 'big')

		with open( videoFilePath, "wb") as file:
			bytesToRecieve = imageLength
			while bytesToRecieve:
				recievedData = recieveBytes(min(BUFFER_SIZE, bytesToRecieve), connection)
				file.write(recievedData)
				bytesToRecieve -= len(recievedData)
			
		break

	print("Video editado recibido")

def initConnection():
	connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connection.connect(("localhost", SERVER_PORT))
	
	return connection

def main():
	connection = initConnection()
	sendVideoToServer(connection, VIDEO_PATH)
	recieveVideoFromServer(connection, EDITED_VIDEO_PATH)

main()
	