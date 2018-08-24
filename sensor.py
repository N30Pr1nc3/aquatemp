import glob
import time
from time import sleep
import RPi.GPIO as GPIO
import httplib

sleeptime = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print 'Warte auf Initialisierung...'
base_dir = '/sys/bus/w1/devices/'

while True:
	try:
		device_folder = glob.glob(base_dir + '28*')[0]
		break
	except IndexError:
		sleep(0.5)
	continue

device_file = device_folder + '/w1_slave'
def TemperaturMessung():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

TemperaturMessung()

def TemperaturAuswertung():
	lines = TemperaturMessung()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = TemperaturMessung()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		return temp_c
try:
	print '---------------------------------------'
	while True:
		sum = 0
		i=0
		while i < 60:
			temp = TemperaturAuswertung()
			sum = sum+temp
			i+=1
			print "\rTemperatur:", temp , "C"
			print "\rAVG       :", sum/i , "C"
                        print "\rSumm      :", sum , "C"
			time.sleep(sleeptime)
		try:
			conn = httplib.HTTPConnection("ts.myralia.de")
			conn.request("HEAD","/set.php?data=[{%22type%22:3,%22value%22:%22"+str(sum/60)+"%22}]")
			res = conn.getresponse()
			print res.status, res.reason
		except:
			print 'fehlerhafte Uebertragung'
except KeyboardInterrupt:
	PIO.cleanup()
