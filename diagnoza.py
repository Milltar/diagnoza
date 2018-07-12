from flask import Flask, session, render_template,render_template_string, request, redirect, g, url_for,send_from_directory
from datetime import datetime, timedelta
from get_gate import get_gate
from test_ip import test_ping, test_arping, check_host_registration,check_dhcp_registration
from config import *
import os
import paramiko
import threading
import Queue
import time
import progressbar


app =Flask(__name__, static_url_path='')
app.secret_key = os.urandom(24)

def server_connect(adres_bramy):
    ip_serwera=adres_bramy
    remote_conn_pre=paramiko.SSHClient()                                                                             #polaczenie z danym serwerem
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(ip_serwera, serwer_port, serwer_login, serwer_password, look_for_keys=False, allow_agent=False, timeout=5)
    return remote_conn_pre


@app.route('/', methods = ['POST', 'GET'])
def glowna():
    return render_template('index.html')


@app.route('/check_ip', methods = ['POST', 'GET'])
def check_ip():
    threads = []
    queue_ping = Queue.Queue()
    queue_arping = Queue.Queue()
    queue_host_registration = Queue.Queue()
    queue_dhcp_registration = Queue.Queue()
    adres_ip=request.form['adres_ip']
    oktety=adres_ip.split(".")
    if len(oktety[0])>3 or len(oktety[1])>3 or len(oktety[2])>3 or len(oktety[3])>3:
        return "Bledny adres ip"
    else:
        serwery, adres_bramy, vlan= get_gate(adres_ip)                                                  #pobranie listy sererow, serwara(bramy), i vlanu
        if adres_bramy=="IP z poza zakresu sieci":
            return "Adres IP jest z poza zakresu sieci"
        else:
            remote_conn_pre=server_connect(adres_bramy)                                                     #polacznie z aktywnym serwerem
            t1 = threading.Thread(test_ping(remote_conn_pre,adres_ip, queue_ping))                          #
            t2 = threading.Thread(test_arping(remote_conn_pre, adres_ip, queue_arping))
            t3 = threading.Thread(check_host_registration(remote_conn_pre,adres_ip, queue_host_registration))
            t4 = threading.Thread(check_dhcp_registration(adres_ip, adres_bramy, serwery, queue_dhcp_registration))
            threads.append(t1);  threads.append(t2);threads.append(t3);threads.append(t4)

            for t in threads:
                t.start(); t.join()

            result_ping = queue_ping.get()
            result_arping=queue_arping.get()
            result_host_registration=queue_host_registration.get()
            result_dhcp_registration=queue_dhcp_registration.get()
            remote_conn_pre.close()
            return "Statystka dla: "+adres_ip+"<br><br>"+result_ping+"<br><br>"+result_arping+"<br><br>"+result_host_registration+"<br><br>"+result_dhcp_registration
    #return render_template('sprawdz_ip.html',adres_ip=adres_ip)

@app.route('/cos', methods = ['POST', 'GET'])
def cos():
    with progressbar.ProgressBar(max_value=10) as bar:
        for i in range(10):
            time.sleep(0.1)
            bar.update(i)
    return "dupa"


if __name__ == '__main__':
    app.run(host="192.168.1.177", port=8300, threaded=True, debug=True)
