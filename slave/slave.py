import io
import socket
from PIL import Image
from PIL import ImageFilter
from multiprocessing.reduction import recv_handle

SERVER_PORT = 12345
BUFFER_SIZE = 4096
FRAMES_FOLDER_PATH = "frames/"

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

def initConnection():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("localhost", SERVER_PORT))
	client.send(b"%REGISTRO_SLAVE%")

	return client

def recieveFrameFromServer(connection, fileStream, imageLength):
	bytesToRecieve = imageLength
	while bytesToRecieve:
		recv_data = recieveBytes(min(BUFFER_SIZE, bytesToRecieve), connection)
		fileStream.write(recv_data)
		bytesToRecieve -= len(recv_data)

def applyFilterToFrame(fileStream, frameNumber):
	image = Image.open(fileStream)
	image = image.filter(ImageFilter.FIND_EDGES())
	
	image.save(FRAMES_FOLDER_PATH + str(frameNumber) + ".png", format="png")	

def returnFrameToServer(frameNumber, connection):
	with open(FRAMES_FOLDER_PATH + str(frameNumber) + ".png", "rb") as file:
		imageLength = file.seek(0, 2)
		file.seek(0, 0)

		imageLengthBytes = imageLength.to_bytes(4, "big")
		connection.sendall(imageLengthBytes)
		
		data = file.read(BUFFER_SIZE)
		while len(data):
			connection.sendall(data)
			data = file.read(BUFFER_SIZE)

def processFrame(connection):
	imageLengthBytes = recieveBytes(4, connection)
	imageLength = int.from_bytes(imageLengthBytes, 'big')

	frameNumberBytes = recieveBytes(4, connection)
	frameNumber = int.from_bytes(frameNumberBytes, 'big')

	fileStream = io.BytesIO()

	recieveFrameFromServer(connection, fileStream, imageLength)
	applyFilterToFrame(fileStream, frameNumber)
	returnFrameToServer(frameNumber, connection)

	print("Frame procesado y devuelto al servidor")
		

def main():
	connection = initConnection()
	while True:
		processFrame(connection)	
main()