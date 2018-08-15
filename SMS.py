#!/usr/bin/python3
# import poplib
import time
# from bs4 import BeautifulSoup
# from try_port import send_message
import serial
import time
import imaplib
import email
import sys

# Mailbox = imaplib.IMAP4("localhost")
# Mailbox.login("test1@my.local", "test")
# t, data = Mailbox.fetch('1', '(RFC822)')



class Alarm_by_SMS:
	email = ''
	password = ''
	imap_server = "" # bool
	port = 0
	ssl = ''
	phone_numbers = []
	retries = 0

	def __init__(self):
		with open ("/home/pi/Alarm_manager/config.ini", 'r') as file:
			self.user_email = file.readline().replace("\n", "")
			self.password = file.readline().replace("\n", "")
			self.imap_server = file.readline().replace("\n", "")
			self.port = int (file.readline().replace("\n", ""))
			self.ssl = file.readline().replace("\n", "")
			self.phone_numbers.append( file.readline().replace("\n", ""))
			self.retries = int (file.readline().replace("\n", ""))
			self.email_DCE = file.readline().replace("\n", "")
			# self.client = file.readline().replace("\n", "")
			# self.COUNT = int (file.readline().replace("\n", ""))
			# print (self.COUNT)
			# self.phone_numbers.append(self.client)
	def logs(self, msg):
		with open ("logs.log", 'a') as file:
			file.write(msg)

	def partition_msg (self, msg):
		if len(msg)%70 != 0:
			return len(msg)//70+1
		else:
			return len(msg)//70

	def polling (self):
		while (1):
			try:
				with open ("//home//pi//Alarm_manager//semaphore", 'r+') as file:
					updates = file.read()
				if updates == "1":
					pass # нет обновлений (прочитано)
				elif updates == "2":
					self.__init__()
					file = open("//home//pi//Alarm_manager//semaphore", "w")
					file.write("1")
					file.close()
					# читать новые значения
				elif updates == "3":
					# идёт запись программой interface.py
					time.sleep(20)
					continue
			except:
				time.sleep(5)
				continue
			# mailbox = poplib.POP3("localhost")
			# mailbox.user("test1@my.local")
			# mailbox.pass_("test")
			mailbox, email_list, num_list = self.get_mailbox(self.imap_server, self.port,
									 self.email, self.password, self.email_DCE)
			# count = mailbox.stat()[0]
			# print (count)
			self.logs(time.ctime(time.time())+'\t\t\t'+ str(len(email_list))+' new email messages\n')
			for msg, num in zip(email_list, num_list):
					# strings = mailbox.retr(count + j) 
					# msg =''
					# for i in strings:
					#       msg += str(i)
					# with open ("msg.html", 'w') as file:
					#       print (msg)
					#       file.write(msg)
					# print (j)
					# self.get_html(mailbox, self.COUNT+j)
##                                        print (new_message)
##                                        msg = self.parser(new_message) # придумать механизм разделения больших сообщений
##                                        print (msg)
					MSG_NUM = self.partition_msg(msg)
					parts = list()
					print (msg)
					while (len(msg)>60):
						print ("OPA")
						parts.append(msg[0:60])
						msg = msg[60:]
						print (len(msg))
					# print (MSG_NUM)
					if len(msg)<=60 and parts == []:
						parts = [msg]
					else:
						parts.append(msg)
					self.logs(time.ctime(time.time())+"\t\t\t"+ str(MSG_NUM) + " SMS will be delivered\n")
					print (parts)
					for part in parts:
						retries = 0
						msg_count = 1
						while (self.send_message(part, self.phone_numbers)!=0 and retries<5):
							retries += 1
							print (retries)
							self.logs(time.ctime(time.time())+"\t\t\t"+ "delivery error for {0}/{1} try {2}/5\n".format(str(msg_count), str(MSG_NUM), str(retries)))
							# time.sleep(10)
						if retries == 5:
							mailbox.store(num,'-FLAGS','\\Seen')
							self.send_message("Сообщение не может быть доставлено!", self.phone_numbers)
							# break
						msg_count += 1

							# pass abs(len(msg)-70*msg_count)
##                                                self.logs(time.ctime(time.time())+"\t\t\t"+ str(msg_count)+"/"+str(MSG_NUM)+" SMS delivered\n")
					# self.COUNT+=1

			mailbox.close()
			mailbox.logout()
			time.sleep(2)

		self.COUNT = count
		
		parts = list()
		
		time.sleep(30)                                  

	def get_mailbox(self, imap_server, port, user_email, password, email_DCE):
		try:
			mailbox = imaplib.IMAP4(self.imap_server, self.port)
			mailbox.login(self.user_email, self.password)
			mailbox.select("INBOX")
			data = mailbox.search(None, "INBOX", "UNSEEN", '(FROM "%s")' % (self.email_DCE))[1]
	##                print (data)
			unread_msg_nums = data[0].split()
			# print (unread_msg_nums)
			email_list = list()
			num_list = list()
			for num in data[0].split():
				data = mailbox.fetch(num, '(RFC822)')[1]
				email_message = email.message_from_string(data[0][1].decode("cp1251"))
	##                        print (email_message.is_multipart
				if email_message.is_multipart() is True:
					msg = "New alarm! See in the system of monitoring!"
	##                                print (msg)
				else:
					msg = email_message.get_payload()
	##                        print (msg)
				email_list.append(msg)
				num_list.append(num)
	##                        print (email_list)
				# print (Mailbox.store(num,'+FLAGS','\\SEEN'))
			return (mailbox, email_list, num_list)
		except:
			self.logs(time.ctime(time.time())+"\t\t\t"+"Error in connecting to mailbox\n")
			sys.exit()
		# mailbox = poplib.POP3("localhost")
		# mailbox.user("test1@my.local")
		# mailbox.pass_("test")
		# return mailbox
	# def get_html(self, mailbox, count):
	#       # print (count)
	#       # msg = str(mailbox.retr(count))
	#       # if 'From: "test2@my.local" <test2@my.local>' in msg:
	#       with open ("msg.html", 'w') as file:
	#                       file.write(msg.)
	#       else:
	#               #to receive
	#               pass
	def config(self, phone_numbers):
		with open ("phones.txt", "r") as file:
			phones_text = file.read()
			self.phone_numbers = phones_text.split("\n").remove("")
	def parser(self, msg):
		# file = open("msg.html")
		# doc = file.read()
		# file.close()
		if "<html>" and "</html>" in msg:
			return "Новое оповещение! Смотрите в системе мониторинга!"
		else:
			return msg
		#try:
		#       soup = BeautifulSoup(msg, "html.parser")
		#       listing = soup.find_all("tr")
		#       content = (listing[0].contents)[1].contents[0]
		#       return content
		#except:
		#        soup = BeautifulSoup(msg, "html.parser")
		#       listing = soup.find_all("br")
		#       print ("что-то не так в парсере")
		
	def send_message(self, msg, phone_numbers):
		# try:
			ser = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, 
								stopbits=serial.STOPBITS_ONE, timeout=2,
								xonxoff=True, rtscts=False)

			ser.close()
			ser.open()
##                        ser.write(bytes([26]))
			ser.write(b"ATV0\r")
			ser.write(bytes([26]))
##                        ser.write(bytes([26]))
			# print (ser.readline())
			print (phone_numbers)
			#print (msg)
			for number in phone_numbers:
				ser.write(bytes('AT+CMGS='+'"'+number+'"'+'\r', encoding = "cp1251"))
				print (ser.readline())
				time.sleep(1)
				ser.write(msg.encode()+b"\r")
				time.sleep(1)
				ser.write(bytes([26]))
				time.sleep(1)
				string = ''
				for i in range(0, 4):
					string += ser.readline().decode("utf-8")
				print (string)
				print ("i'm here")
				# print (ord(string))
				if "ERROR" in string or string == "":
					# print (string)
				# print ("SOMETHING WRONG") # нужен флаг, который будет показывать, что на этом номере произошёл сбой
					ser.close()
					return 1
				else:
					# print ("ALL ALRIGHT")
					ser.close()
					return 0
		# except:
			self.logs(time.ctime(time.time())+'\t\t\t'+ 'check your connection\n')
			exit()


new_object = Alarm_by_SMS()
new_object.polling()
print("WTF")



#
# Сделать конфигуратор содержимого СМС
# продумать skip
# 
#
