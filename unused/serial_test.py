import serial

arduino = serial.Serial("COM3", 9600)

while True:
    distance = arduino.readline().decode().strip()
    print(distance)