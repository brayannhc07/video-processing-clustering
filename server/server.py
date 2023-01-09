import io
import os
import cv2
import socket
import numpy as np
import threading
import moviepy.editor as mp
import time

from PIL import Image
from PIL import ImageFilter

# pip install opencv-python
# pip install pillow

SERVER_PORT = 12345
BUFFER_SIZE = 4096
VIDEO_PATH = "server_video.mp4"
VIDEO_EDITED_PATH ="server_video_edited.mp4"
VIDEO_FINAL_PATH = "server_video_final.mp4"
AUDIO_PATH = "server_audio.mp3"
FRAMES_FOLDER_PATH = "frames/"
EDITED_FRAMES_FOLDER_PATH = "edited_frames/"
SLAVES_CONNECTIONS = []


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

def addVideoAudio(audioFilePath,inVideoFilePath,outVideoFilePath):
    audio = mp.AudioFileClip(audioFilePath)
    video1 = mp.VideoFileClip(inVideoFilePath)
    final = video1.set_audio(audio)
    final.write_videofile(outVideoFilePath)

def framesToVideo(framesFolder, framesCount, fps, outVideoFilePath):
    frames = []

    for i in range(0, framesCount):
        print(i)
        imagePath = framesFolder + str(i) + ".png"
        image = cv2.imread(imagePath)
        frames.append(image)
        
    height, width, _ = frames[0].shape
    video = cv2.VideoWriter(outVideoFilePath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    for i in range(0, framesCount - 1):
        print(i)
        video.write(frames[i])

    cv2.destroyAllWindows()
    video.release()

def extractAudio(video_name , loc):
    audio = mp.VideoFileClip(video_name)
    audio.audio.write_audiofile(loc)


def registerSlave(client_socket, client_address):
	SLAVES_CONNECTIONS.append(client_socket)

	address, port = client_address
	print("Slave registrado de {0}:{1}".format(address, port))


def recieveVideoFromClient(client_socket, videoFilePath):
	print("Recibiendo video del cliente")
	with open(videoFilePath, "wb") as file:
		recv_data = client_socket.recv(BUFFER_SIZE)

		while recv_data:
			file.write(recv_data)
			recv_data = client_socket.recv(BUFFER_SIZE)
			
			if recv_data == b"%VIDEO_ENVIADO%":
				break

def saveVideoFrames(videoFilePath, framesFolderPath):
	print("Separando video en frames")

	vidcap = cv2.VideoCapture(videoFilePath)

	fps = vidcap.get(cv2.CAP_PROP_FPS)

	success, image = vidcap.read()
	count = 0

	while success:
		cv2.imwrite(framesFolderPath + str(count) + ".png", image)
		success, image = vidcap.read()
		count += 1
	
	return count, fps
	
def processFramesWithSlaves(inFramesFolderPath, outFramesFolderPath, slavesConnections):
	print("Iniciando envio a slaves")
	frames = [img for img in os.listdir(inFramesFolderPath) if img.endswith(".png")]

	slavesCount = len(slavesConnections)
	frameChunks = np.array_split(frames, slavesCount)

	for i in range(slavesCount):
		processFrameBySlave(frameChunks[i], slavesConnections[i], inFramesFolderPath, outFramesFolderPath)

	print("Se procesaron todas las imágenes")
	
def processFrameBySlave(frames, slaveSocket, inFramesFolderPath, outFramesFolderPath):
	for frame in frames:
		frameNumber = int(frame.split(".png")[0])
		sendFrameToSlave(frameNumber, slaveSocket, inFramesFolderPath)
		recieveProcessedFrameFromSlave(frameNumber, slaveSocket, outFramesFolderPath)

def sendFrameToSlave(frameNumber, slaveConnection, inFramesFolderPath):
	with open(inFramesFolderPath + str(frameNumber) + ".png", "rb") as file:
		imageLength = file.seek(0, 2)
		file.seek(0, 0)

		imageLengthBytes = imageLength.to_bytes(4, "big")
		frameNumberBytes = frameNumber.to_bytes(4, "big")

		slaveConnection.sendall(imageLengthBytes)
		slaveConnection.sendall(frameNumberBytes)
		
		data = file.read(BUFFER_SIZE)

		while len(data):
			slaveConnection.sendall(data)
			data = file.read(BUFFER_SIZE)

def recieveProcessedFrameFromSlave(frameNumber, slaveSocket, outFramesFolderPath):
	imageLengthBytes = recieveBytes(4, slaveSocket)
	imageLength = int.from_bytes(imageLengthBytes, 'big')

	with open( outFramesFolderPath + str(frameNumber) + ".png", "wb") as file:
		bytesToRecieve = imageLength
		while bytesToRecieve:
			recievedData = recieveBytes(min(BUFFER_SIZE, bytesToRecieve), slaveSocket)
			file.write(recievedData)
			bytesToRecieve -= len(recievedData)
	
def initServer():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('localhost', SERVER_PORT))
	server.listen()

	return server

def main():
	server = initServer()

	while True:
		client_socket, client_address = server.accept()

		recv_data = client_socket.recv(BUFFER_SIZE)
		if recv_data == b"%VIDEO_ENVIO%":
			recieveVideoFromClient(client_socket, VIDEO_PATH)

			extractAudio(VIDEO_PATH, AUDIO_PATH)
			frames, fps = saveVideoFrames(VIDEO_PATH, FRAMES_FOLDER_PATH)

			print(str(frames) + " - " + str(fps) )

			processFramesWithSlaves(FRAMES_FOLDER_PATH, EDITED_FRAMES_FOLDER_PATH, SLAVES_CONNECTIONS)

			framesToVideo(EDITED_FRAMES_FOLDER_PATH, frames, fps, VIDEO_EDITED_PATH)
			addVideoAudio(AUDIO_PATH, VIDEO_EDITED_PATH, VIDEO_FINAL_PATH)

			print("Video terminado de procesar")

		if recv_data == b"%REGISTRO_SLAVE%":
			registerSlave(client_socket, client_address)
main()