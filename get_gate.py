
from config import *
import MySQLdb
import sys


def get_gate(ip):
    
    baza=[]; baza2=[]; serwery=[]; vlan=""; adres_bramy=""; status_ip="";
    con_mysql = MySQLdb.connect(sql_ip, sql_login, sql_pass, sql_baza)
    c = con_mysql.cursor()
    
    try:
        ip=ip.split(".")                                                                                        #pobranie adresu IP
        oktet=int(ip[2])-1                                                                              
        ip2=(ip[0]+"."+ip[1]+"."+str(oktet)+"."+ip[3]).split(".")                                               #kopia IP z pomniejszonym trzecim oktetem o 1    
        
        c.execute("SELECT DISTINCT(brama) FROM  widok_adreacje")                                                #pobanie listy bram z tabeli
        for i in range(c.rowcount):
            if (i<c.rowcount):
                rec = c.fetchone()                                                                              #pobranie pierwszego ip bramy do zmiennej                                          
                brama=rec[0].split(".")                                                                         #podzial ip bramy na oktety                
                if (int(brama[0])==int(ip[0]) and int(brama[1])==int(ip[1]) and int(brama[2])==int(ip[2])):     #porownanie pierwszych 3 oktetow bramy i ip
                    if (int(brama[3])<=int(ip[3])):                                                             #wpisanie do listy 4 oktetu (bramy) mniejszego od 4 oktetu ip    
                        baza.append(int(brama[3]))
                        #baza=rec[0]
                if (int(brama[0])==int(ip2[0]) and int(brama[1])==int(ip2[1]) and int(brama[2])==int(ip2[2])):  #sprawdzenie dla IP2 z mniejszym 3 oktetem
                    if (int(brama[3])<=int(ip2[3])):
                        baza2.append(int(brama[3]))
                        #baza2=rec[0]

        if not baza:                                                                                           #Brama z mniejszym 3 oktetem niz u IP
            baza2=sorted(baza2)                                                                               
            adres_bramy=str(ip2[0])+"."+str(ip2[1])+"."+str(ip2[2])+"."+str(baza2[-1])                               
        else:                                                                   
            baza=sorted(baza)                                                                                  #posortowanie potencjalnych bram (4 oktetow) rosnaco
            adres_bramy=str(ip[0])+"."+str(ip[1])+"."+str(ip[2])+"."+str(baza[-1])                             #zlozenie adresu IP bramy 
        
        
        zapytanie="SELECT DISTINCT(vlan) FROM  widok_adreacje WHERE brama='"+str(adres_bramy)+"'"              #pobranie vlanu na podstawie bramy
        c.execute(zapytanie)
        rec2= c.fetchone()
        vlan=rec2[0]

        zapytanie2="SELECT DISTINCT(ip) FROM  widok_adreacje WHERE vlan='"+str(vlan)+"'"                       #pobranie ip serwerow na podstawie vlanu
        c.execute(zapytanie2)
        for i in range(c.rowcount):
            if (i<c.rowcount):
                rec3= c.fetchone()
                temp= rec3[0].split(".")                                                                       
                #if temp[0]=="213" and temp[1]=="92" and temp[2]=="190":                                       #Wybranie serwerow z puli 213.92.190
                serwery.append(str(rec3[0]))   
        status_ip="ok"                                                                                         #status dla prawidlowo pobranej listy serwerow 
    except (ValueError,IndexError):
        adres_bramy="IP z poza zakresu sieci"
        
    
    return serwery, str(adres_bramy), str(vlan)


    