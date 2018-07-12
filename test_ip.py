from config import *
import os
import paramiko


def test_ping(remote_conn_pre, adres_ip, out_queue):
    cmd_ip="ping "+adres_ip+" -c 100 -i 0.2 -s 1024 "
    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_ip)
    exit_status = stdout.channel.recv_exit_status()
    temp=stdout.read().strip()
    wynik_ping=temp.split("ping statistics ---")
    wynik_ping=wynik_ping[1]                                        #pobranie podsumowania testu
    out_queue.put(wynik_ping)

def test_arping(remote_conn_pre, adres_ip, out_queue):
    #pobranie vlanu
    cmd_arp="arp "+adres_ip
    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_arp)
    exit_status = stdout.channel.recv_exit_status()
    temp=stdout.read().strip()
    if "no entry" in temp:
        wynik_arping="Brak widocznego maca"
    elif "incomplete" in temp:
        wynik_arping="Brak widocznego maca"
    else:
        temp=temp.split()
        vlan=temp[10]
        wynik_arping=vlan

        #test arping
        cmd_arping="sudo /sbin/arping -c 30 -I "+vlan+" "+adres_ip
        stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_arping)
        exit_status = stdout.channel.recv_exit_status()
        temp2=stdout.read().strip()
        wynik_arping=temp2.split("Sent")
        wynik_arping="Sent:"+wynik_arping[1]                        #pobranie podsumowania testu

    out_queue.put(wynik_arping)

def check_host_registration(remote_conn_pre, adres_ip, out_queue):

    #sprawdzenei czy jest wpis w pliku users.shaper
    cmd_user_shaper="cat /etc/zapora/users.shaper | grep "+adres_ip+" | wc -l"
    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_user_shaper)
    exit_status = stdout.channel.recv_exit_status()
    temp=stdout.read().strip()
    if temp==0:
        result_users_shaper="Brak wpisu w pliku /etc/zapora/users.shaper"
    else:
        result_users_shaper="Prawidlowy wpis w pliku /etc/zapora/users.shaper"

    #sprawdzenei czy jest wpis w pliku users_sort
    cmd_user_sort="cat /etc/zapora/users_sort | grep "+adres_ip+" | wc -l"
    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_user_sort)
    exit_status = stdout.channel.recv_exit_status()
    temp=stdout.read().strip()
    if temp==0:
        result_users_sort="Brak wpisu w pliku /etc/zapora/users_sort"
        resut_mac_speed=""
    else:
        #pobranie mac i predkosci
        result_users_sort="Prawidlowy wpis w pliku /etc/zapora/users_sort"
        cmd_mac_speed="cat /etc/zapora/users_sort | grep "+adres_ip
        stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_mac_speed)
        exit_status = stdout.channel.recv_exit_status()
        temp2=stdout.read().strip().split()
        adres_mac=temp2[1]
        download=temp2[4]
        upload=temp2[5]
        resut_mac_speed="Aktualny MAC: "+adres_mac+"<br>Predkosc pobierania: "+download+" kb/s<br>Predkosc wysylania: "+upload+" kb/s"

    result="Dane hosta:<br>"+result_users_shaper+"<br>"+result_users_sort+"<br>"+resut_mac_speed
    out_queue.put(result)

def check_dhcp_registration(adres_ip, adres_bramy, serwery, out_queue):
    result=""

    if adres_bramy in bramy_ino:
        remote_conn_pre=paramiko.SSHClient()                                                                             #polaczenie z danym serwerem
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_conn_pre.connect(adres_bramy, serwer_port, serwer_login, serwer_password, look_for_keys=False, allow_agent=False, timeout=5)

        #sprawdzenie wpisu w pliku /etc/zapora/users
        cmd_user="cat /etc/zapora/users | grep "+adres_ip+" | wc -l"
        stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_user)
        exit_status = stdout.channel.recv_exit_status()
        temp=stdout.read().strip()
        if temp==0:
            result_users="Serwer DHCP: "+adres_bramy+" Brak wpisu w pliku /etc/zapora/users"
        else:
            result_users="Serwer DHCP: "+adres_bramy+" Prawidlowy wpis w pliku /etc/zapora/users"

        #sprawdzenie wpisu w pliku /etc/dhcpd/
        cmd_dhcp="grep -ril "+adres_ip+" /etc/dhcpd/ | wc -l"
        stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp)
        exit_status = stdout.channel.recv_exit_status()
        temp2=stdout.read().strip()

        if temp2==0:
            result_dhcp="Serwer DHCP: "+adres_bramy+" Brak wpisu w pliku /etc/dhcpd/"
        else:
            cmd_dhcp2="grep -ril "+adres_ip+" /etc/dhcpd/"
            stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp2)
            exit_status = stdout.channel.recv_exit_status()
            dhcp_conf=stdout.read().strip()

            cmd_dhcp3="cat "+dhcp_conf+" | grep "+adres_ip
            stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp3)
            exit_status = stdout.channel.recv_exit_status()
            temp3=stdout.read().strip().split()
            adres_mac=temp3[5]

            result_dhcp="Serwer DHCP: "+adres_bramy+" Prawidlowy wpis w pliku /etc/dhcpd/ ----> IP: "+adres_ip+" MAC: "+adres_mac
            remote_conn_pre.close()
            result=result+result_users+"<br>"+result_dhcp+"<br>"
    else:
        for serwer in serwery:
            if serwer in serwery_dhcp:                              # wybiera serwery dhcp z listy serwerow
                remote_conn_pre=paramiko.SSHClient()                                                                             #polaczenie z danym serwerem
                remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                remote_conn_pre.connect(serwer, 22, serwer_login, serwer_password, look_for_keys=False, allow_agent=False, timeout=10)

                #sprawdzenie wpisu w pliku /etc/zapora/users
                cmd_user="cat /etc/zapora/users | grep "+adres_ip+" | wc -l"
                stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_user)
                exit_status = stdout.channel.recv_exit_status()
                temp=stdout.read().strip()
                if temp==0:
                    result_users="Serwer DHCP: "+serwer+" Brak wpisu w pliku /etc/zapora/users"
                else:
                    result_users="Serwer DHCP: "+serwer+" Prawidlowy wpis w pliku /etc/zapora/users"

                #sprawdzenie wpisu w pliku /etc/dhcpd/
                cmd_dhcp="grep -ril "+adres_ip+" /etc/dhcpd/ | wc -l"
                stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp)
                exit_status = stdout.channel.recv_exit_status()
                temp2=stdout.read().strip()

                if temp2==0:
                    result_dhcp="Serwer DHCP: "+serwer+" Brak wpisu w pliku /etc/dhcpd/"
                else:
                    cmd_dhcp2="grep -ril "+adres_ip+" /etc/dhcpd/"
                    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp2)
                    exit_status = stdout.channel.recv_exit_status()
                    dhcp_conf=stdout.read().strip()

                    cmd_dhcp3="cat "+dhcp_conf+" | grep "+adres_ip
                    stdin, stdout, stderr = remote_conn_pre.exec_command(cmd_dhcp3)
                    exit_status = stdout.channel.recv_exit_status()
                    temp3=stdout.read().strip().split()
                    adres_mac=temp3[5]

                    result_dhcp="Serwer DHCP: "+serwer+" Prawidlowy wpis w pliku /etc/dhcpd/ ----> IP: "+adres_ip+" MAC: "+adres_mac
                    remote_conn_pre.close()
                    result=result+result_users+"<br>"+result_dhcp+"<br>"
    out_queue.put(result)
