import time
import socket
import serial
#定义一个ip协议版本AF_INET，为IPv4；同时也定义一个传输协议（TCP）SOCK_STREAM
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#定义IP地址与端口号
ip_port=('192.168.65.181', 9988)
#进行连接服务器
#time.sleep(5)
client.connect(ip_port)
ser = serial.Serial('COM3', 9600)
while True:
  a=client.recv(1024)#接受服务端的信息，最大数据为1k
  msg=a.decode('utf-8')
  print(msg)
  if(msg=='w'):
      ser.write('w')
  if (msg == 'a'):
      ser.write('a')
  if (msg == 's'):
      ser.write('s')
  if (msg == 'd'):
      ser.write('d')