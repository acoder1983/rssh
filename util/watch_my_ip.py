import internet_ip
import send_email
import time

myIP = None

while True:
    ip = internet_ip.getInternetIp()
    print 'myip ' + ip
    if ip != myIP and ip:
        myIP = ip
        send_email.send_mail(['acoder1983@163.com'], 'my ip', myIP)
    time.sleep(60)
