from fbs_runtime.application_context.PyQt5 import ApplicationContext
# coding=utf-8
import base64
import sys
import webbrowser
from datetime import datetime
import configparser
import pickle
import requests
import requests.cookies
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup

online = True  #sayfaları internetten mi alsın, kayıttan mı?
debug = False #konsola bilgi yaz
ayarlar = 'c:\pi\oys-yesevi.ini'
cerezF = 'c:\pi\oys-yesevi-c.ini'
Config = configparser.ConfigParser()
adres = 'https://oys.yesevi.edu.tr'
dersler=[]
otomatik=False  #otomatik ders izleme kapalı
ilkders = -1

class AnaPencere(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = 'OYS-Yesevi otomatik ders izleme'
        self.setWindowTitle(self.title)
        kullanici_adi=self.ayarOku('Login','kullanici_adi')
        anaform = QWidget(self)
        anaLayout = QHBoxLayout(anaform)
        anaform.setLayout(anaLayout)
        self.setCentralWidget(anaform)
        anaLayout.addWidget(QLabel('(Online)' if online else '(Offline)', anaform))
        anaLayout.addWidget(QLabel('Kullanıcı Adı:', anaform))
        self.lbl_KullaniciAd = QLabel(kullanici_adi, anaform)
        anaLayout.addWidget(self.lbl_KullaniciAd)
        if kullanici_adi != None and kullanici_adi.strip() !='':
            self.lbl_KullaniciAd.setText(kullanici_adi)
        else:
            self.btn_Login = QPushButton('Login', self)
            self.btn_Login.clicked.connect(self.btnLoginClicked)
            anaLayout.addWidget(self.btn_Login)
            self.btn_Login.show()
        self.setupMenu()
        self.show()

    @pyqtSlot()
    def btnLoginClicked(self):
        kullanici_adi = self.loginKontrol()
        self.lbl_KullaniciAd.setText(kullanici_adi)
        self.btn_Login.destroy()
        if debug: print('btnLoginClicked: kullanici_adi=', kullanici_adi)

    def ayarlariOku(self):
        if debug: print('ayarlariOku:','şimdilik gereksiz')

    def ayarYaz(self,grup,ayar,deger):
        if 'Ayar' not in Config:
            Config['Ayar'] = {}
            Config['Ayar']['AyarOkundu']='Hayır'
            if debug: print('ayarYaz: Ayarlar dosyadan okunmamış!')
        else:
            Config['Ayar']['AyarOkundu']='Evet'
        if grup not in Config:
            Config[grup]={}
        Config[grup][ayar]=deger
        with open(ayarlar, 'w') as configfile:
            Config.write(configfile)

    def ayarOku(self,grup,ayar):
        if 'Ayar' in Config:
            if grup in Config:
                if ayar in Config[grup]:
                    return Config[grup][ayar]
                else: return None
            else: return None
        else:
            Config['Ayar'] = {}
            Config['Ayar']['AyarOkundu']='Hayır'
            if Config.read(ayarlar) == []:
                if debug: print('ayarOku: Ayarlar dosyası yok')
                self.ayarYaz('Ayar','YeniDosya')
            else:
                return self.ayarOku(grup,ayar)

    def cerezYaz(self,cerezler):
        global cerezF
        with open(cerezF,'wb') as dosya:
            pickle.dump(cerezler,dosya)

    def cerezOku(self):
        global cerezF
        with open(cerezF,'rb') as dosya:
            cerezler=pickle.load(dosya)
        return cerezler

    def responseYaz(self, dosyaadi, icerik):
        with open(dosyaadi, 'w', encoding="utf8") as dosya:
            if debug: print(f'responseYaz: {dosya} yazıldı')
            dosya.write(icerik)
            dosya.close()

    def CloseEvent(self, e):
        e.ignore()

    def dersProgramiAc(self):
        b = dersProgrami()
        #b.show()

    def setupMenu(self):
        menu = self.menuBar().addMenu("&Dosya")
        # ayar menüsü
        ayarlari_ac = QAction('&Ayarlar', self)
        ayarlari_ac.triggered.connect(self.ayarlariOku)
        menu.addAction(ayarlari_ac)
        ders_programi_ac = QAction('&Ders Programı', self)
        ders_programi_ac.triggered.connect(self.dersProgramiAc)
        menu.addAction(ders_programi_ac)
        # çıkış menüsü
        close_action = QAction('&Çıkış', self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        # help menüsü
        help_menu = self.menuBar().addMenu("&Yardım")
        about_action = QAction('&Hakkında', self)
        help_menu.addAction(about_action)

        def show_about_dialog(menu):
            text = "<center>" \
                   "<h1>Yesevi Otomatik Ders İzleme</h1>" \
                   "&#8291;" \
                   "</center>" \
                   "<p>Version 1.0<br/>" \
                   "Copyright &copy; pi511</p>"
            QMessageBox.about(self, "OYS Otomatik Ders İzleme Hakkında", text)

        about_action.triggered.connect(show_about_dialog)

    class KulAd_Sif_Al(QDialog):
        @pyqtSlot()
        def btn_Login_clicked(self):
            self.ayarYaz('Kullanıcı','kullanici_adi', self.txt_KulAd.toPlainText() )
            if debug: print('kuad_sif_al:',self.txt_KulAd.toPlainText())
            self.ayarYaz('Kullanıcı','sifre', str(base64.b64encode(self.txt_KulSif.toPlainText().encode()).decode('utf-8')) )

        def __init__(self, parent):
            super(QDialog, self).__init__()
            dlayout = QVBoxLayout(self)
            lbl_KulAd = QLabel('Kullanıcı adı (TC):', self)
            dlayout.addWidget(lbl_KulAd)
            self.txt_KulAd = QTextEdit(self)
            dlayout.addWidget(self.txt_KulAd)
            self.txt_KulAd.setText(self.ayarOku('Kullanıcı','kullanici_adi'))
            lbl_KulSif = QLabel('Şifre:', self)
            dlayout.addWidget(lbl_KulSif)
            self.txt_KulSif = QTextEdit(self)
            dlayout.addWidget(self.txt_KulSif)
            self.txt_KulSif.setText(self.ayarOku('Kullanıcı','sifre'))
            btn_Login = QPushButton('Login', self)
            btn_Login.clicked.connect(self.btn_Login_clicked)
            dlayout.addWidget(btn_Login)
            self.setWindowModality(Qt.ApplicationModal)
            self.setLayout(dlayout)
            self.setGeometry(0, 0, 150, 150)
            self.exec()

    def ayarLogin(self):
        #b = self.KulAd_Sif_Al(self)
        kullanici = {
            'giris_yap_btn': 'Sisteme Giriş Yap',
            'kullanici_adi': '',
            'sifre': '',
            'sg': '',
            'deger_adi': ''
        }
        if self.ayarOku('Kullanıcı','kullanici_adi')=='':
            self.KulAd_Sif_Al()
        else:
            kullanici['kullanici_adi'] = self.ayarOku('Kullanıcı','kullanici_adi')
            kullanici['sifre'] = base64.b64decode(bytearray(self.ayarOku('Kullanıcı','sifre'),'utf-8'))
            if debug: QMessageBox.question(self, 'Ayar yap', 'Ayarlar Okundu', QMessageBox.Ok)
        return kullanici

    def loginKontrol(self):
        cerezler=self.cerezOku()
        try:
            if online:
                sayfa = requests.get(adres + '/mesajlar', cookies=cerezler)
                self.responseYaz('c:\\pi\\temp\\oys-mesaj.html', sayfa.text)
            else:
                with open('c:\\pi\\temp\\oys-mesaj.html', 'r', encoding="utf8") as dosya:
                    sayfa = dosya.read()
                    dosya.close()
            soup = BeautifulSoup(sayfa.text, features='html.parser')
            if soup.find('span', {'class': 'username username-hide-on-mobile'}):
                kullanici_adi = soup.find('span', {'class': 'username username-hide-on-mobile'}).text
                self.ayarYaz('Login', 'kullanici_adi', kullanici_adi)
            else:
                if debug: print('loginKontrol: kullanici_adi bulunamadı! Giriş yapılacak.')
                kullanici_adi=self.login()
            if debug: print(f'loginKontrol: kullanici_adi={kullanici_adi} status={sayfa.status_code}')
        except requests.exceptions.RequestException as e:
            if debug: print('loginKontrol: HATA e=',e)
            kullanici_adi=self.login()
        return kullanici_adi

    def login(self):
        kullanici = self.ayarLogin()
        if online:
            #sayfa = urllib.request.urlopen(adres)
            sayfa = requests.get(adres).text
            self.responseYaz('c:\\pi\\temp\\oys-ana.html',sayfa)
        else:
            with open('c:\\pi\\temp\\oys-ana.html', 'r', encoding="utf8") as dosya:
                sayfa = dosya.read()
                dosya.close()
        soup = BeautifulSoup(sayfa, features='html.parser')
        Inputs = soup.find_all('input', {'type': 'hidden'})
        if debug: print('login: Inputs=',Inputs) #bulunan tüm gizli Input tagler. bunlar login paketi oluşturmak için
        for gizli in Inputs:
            #if debug: print('login:', gizli)
            if gizli.attrs['name'] == 'sg':
                kullanici['sg'] = gizli.attrs['value']
            if 'id' in gizli.attrs and gizli.attrs['id'] == 'cb':
                kullanici['deger_adi'] = gizli.attrs['name']
                kullanici[gizli.attrs['name']] = ''
            if gizli.attrs['name'] == 'pd':
                kullanici[kullanici['deger_adi']] = gizli.attrs['value']
        if debug: print('login: kullanici=', kullanici)
        if online:
            response = requests.post(adres + '/login', data=kullanici)
            sayfa = response.text
            self.responseYaz('c:\\pi\\temp\\oys-login.html',sayfa)
            #if debug: print('login: sayfa=', sayfa)
            cerezler = response.cookies
        else:
            with open('c:\\pi\\temp\\oys-login.html', 'r', encoding="utf8") as dosya:
                sayfa = dosya.read()
                dosya.close()
                cerezler=window.cerezOku()
        if debug: print('login: çerezler=',cerezler)
        if debug: print('login: type-cerezler=',type(cerezler))
        #self.ayarYaz('Login','cerezler',str(cerezler))
        self.cerezYaz(cerezler)
        soup = BeautifulSoup(sayfa, features='html.parser')
        if soup.find('span', {'class': 'username username-hide-on-mobile'}):
            kullanici_adi = soup.find('span', {'class': 'username username-hide-on-mobile'}).text
            self.ayarYaz('Login', 'kullanici_adi', kullanici_adi)
            if debug: print("login: kullanici_adi=",kullanici_adi)
        else:
            kullanici_adi=None
            if debug: print("login: Kullanıcı/Şifre hatalı? kullanici_adi=",kullanici_adi)
        return kullanici_adi

class dersProgrami(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Ders Programı'
        self.initUI()
        self.ders_programi_getir()
        self.dersProgramDoldur()
        self.exec()

    def dersProgramDoldur(self):
        dersler = self.ders_program_kontrol()
        i = 0
        for ders in dersler:
            self.tableWidget.setItem(i, 0, QTableWidgetItem(ders['ders']))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(ders['tarih']))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(ders['saat']))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(ders['kalan']+' dakika'))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(ders['link']))
            #self.tableWidget.setItem(i, 4, QTableWidgetItem('<a href="' + ders['link'] + '">' + ders['link'] + '</a>'))
            i += 1
        if otomatik:
            self.tableWidget.item(ilkders, 2).setBackground(Qt.green)
        else:
            self.tableWidget.item(ilkders, 2).setBackground(Qt.white)
        if debug: print(f'dersProgramDoldur: {i} ders dolduruldu')

    @pyqtSlot()
    def btn_Baslat_clicked(self):
        global ilkders, dersler, otomatik
        if otomatik:
            self.btn_Baslat.setText('Otomatik İzlemeyi Başlat')
            otomatik=False
            self.ders_zamanla(-1)
        else:
            self.btn_Baslat.setText('Otomatik İzlemeyi İptal Et')
            otomatik = True
            if ilkders>-1:
                if debug: print('Baslat_clicked: okunan=', dersler[ilkders]['kalan'],' dakika')
                #kalan=int(dersler[ilkders]['kalan'])*60
                kalan=self.kalanDakika(dersler[ilkders]['saat'])*60
                if debug: print('Baslat_clicked: hesaplanan=', str(kalan)+' saniye')
                self.ders_zamanla(kalan)
            else:
                if debug: print("Başlat_clicked: Bu hafta ders yok!, ilkders=", ilkders)
                self.ders_zamanla(0)
        window.ayarYaz('DersProgram','Otomatik','Evet' if otomatik else 'Hayır')
        self.dersProgramDoldur()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(6)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['Ders Adı', 'Tarih', 'Saat', 'Kalan Süre', 'Bağlantı'])
        self.tableWidget.setColumnWidth(0, 400)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 50)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setColumnWidth(4, 250)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.btn_Baslat = QPushButton('Otomatik İzlemeyi Başlat', self)
        self.btn_Baslat.clicked.connect(self.btn_Baslat_clicked)
        self.layout.addWidget(self.btn_Baslat)
        self.setLayout(self.layout)
        self.setGeometry(0, 0, 1000, 300)

    def ders_programi_getir(self):
        global dersler, oturum
        dersler=[]
        if online:
            window.loginKontrol()
            cerezler=window.cerezOku()
            response = requests.post(adres + '/ders_islemleri_ekran', cookies=cerezler)
            yanit = response.text
            window.responseYaz('c:\\pi\\temp\\oys-ders.html', yanit)
        else:
            with open('c:\\pi\\temp\\oys-ders.html', 'r', encoding="utf8") as dosya:
                yanit = dosya.read()
                dosya.close()
        soup = BeautifulSoup(yanit, features='html.parser')
        bulunandersler = soup.find_all('div', {'class': 'card hover make-it-slow card-items'})
        i = 0
        for bulunanders in bulunandersler:
            eleman = bulunanders.find('button', {'class': 'btn btn-outline-purple'})
            dersler.append({'ders': eleman['dersadi']})
            eleman = bulunanders.find('button', {'class': 'btn btn-outline-blue lesson-live'})
            if eleman:
                dersler[i]['link'] = eleman['data-link']
            else:
                dersler[i]['link'] = 'no-link'
            eleman = bulunanders.find('span', {'class': 'title-date'})
            if eleman:
                dersler[i]['tarih'] = eleman.text
            else:
                dersler[i]['tarih'] = 'Oturum yok'
            eleman = bulunanders.find('span', {'class': 'title-time'})
            if eleman:
                dersler[i]['saat'] = eleman.text
            else:
                dersler[i]['saat'] = '00:00'
            if dersler[i]['tarih'] >= datetime.now().strftime("%d.%m.%Y"):
                dersler[i]['acildi']=False
            else:
                dersler[i]['acildi'] = True
            if debug: print("dersProgramiGetir:", i, dersler[i])
            i += 1
        Inputs = soup.find_all('input', {'type': 'hidden'})
        for gizli in Inputs:
            if 'id' in gizli.attrs and gizli.attrs['id'] == 'ACSI':
                oturum = gizli.attrs['value']
                window.ayarYaz('Login', 'oturum',oturum)
            else:
                oturum=None
        if debug: print('dersProgramiGetir: session=', oturum)
        window.ayarYaz('DersProgram','tarih',datetime.now().strftime("%d.%m.%Y"))
        window.ayarYaz('DersProgram','saat',datetime.now().strftime('%H:%M'))
        return oturum

    def kalanDakika(self,saat1):
        if datetime.strptime(saat1, '%H:%M') < datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M'):
            kalan=-1 * self.gecenDakika(saat1)
        else:
            kalan = int((datetime.strptime(saat1, '%H:%M') - datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M')).seconds / 60)
        if debug: print('kalanDakika: ',kalan, 'dk. saat1=',saat1,' şimdi=',datetime.now().strftime('%H:%M'))
        return kalan

    def gecenDakika(self,saat1):
        if datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M') < datetime.strptime(saat1, '%H:%M'):
            gecen=-1 * self.kalanDakika(saat1)
        else:
            gecen = int((datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M') - datetime.strptime(saat1, '%H:%M')).seconds / 60)
        if debug: print('gecenDakika: ',gecen, 'dk. saat1=',saat1,' şimdi=',datetime.now().strftime('%H:%M'))
        return gecen

    def ders_program_kontrol(self):
        global ilkders, dersler
        bugunku = 999
        for i in range(len(dersler)):
            if dersler[i]['tarih'] == datetime.now().strftime("%d.%m.%Y"):
                kalan = self.kalanDakika(dersler[i]['saat'])
                if kalan<0:
                    dersler[i]['kalan']=str(kalan)
                else:
                    dersler[i]['kalan'] = str(kalan)
                    if kalan < bugunku:
                        bugunku = kalan
                        ilkders = i
            else:
                dersler[i]['kalan'] = '0'
            if debug: print('ders_program_kontrol: ilkders=',ilkders,'bugunku=',bugunku,'i=', i, dersler[i])
        return dersler

    def ders_program_guncelle(self):
        if window.ayarOku('DersProgram','tarih')==datetime.now().strftime("%d.%m.%Y"):
            if self.gecenDakika(window.ayarOku('DersProgram','saat')) > 60:
                if debug: print('ders_program_guncelle: son saat=',window.ayarOku('DersProgram','saat'))
                self.ders_programi_getir()
        self.ders_program_kontrol()
        self.dersProgramDoldur()

    def dersAc(self,i):
        global dersler
        son=window.ayarOku('DersProgram', 'SonAcilan')
        simdiki=dersler[i]['tarih'] + '/' + dersler[i]['saat']
        if son!=simdiki:
            oturum=self.ders_programi_getir()
            webbrowser.open(dersler[i]['link']+'?session='+oturum+'ok&proto=true')
            dersler[i]['acildi']=True
            window.ayarYaz('DersProgram','SonAcilan',dersler[i]['tarih']+'/'+dersler[i]['saat'])
            if debug: print('DersAc:', dersler[i]['link'], ' açıldı')
        else:
            if debug: print('DersAc:', dersler[i]['link'], ' daha önce açılmış')

    def ders_zamanla(self, kalan):
        #timer = threading.Timer(kalan, dersAc)
        if kalan>-1:
            #self.timer = threading.Timer(60, self.dakikadaBir)
            #self.timer.start()
            self.timer=QTimer()
            self.timer.timeout.connect(self.dakikadaBir)
            self.timer.start(60*1000)
            if debug: print("ders_zamanla: zamanlama başladı, ilkders=", ilkders)
        else:
            if debug: print("ders_zamanla: zamanlama iptal edildi, ilkders=", ilkders)
            #self.timer.cancel()
            self.timer.stop()
            self.timer=None

    def dakikadaBir(self):
        global dersler, ilkders
        i=ilkders
        if debug: print('dakikadaBir: ders=',i,'daha önce','açıldı' if dersler[i]['acildi'] else 'açılmadı')
        if i>-1:
            if not dersler[i]['acildi']:
                if dersler[i]['tarih'] == datetime.now().strftime("%d.%m.%Y"):  #hala bugünde miyiz?
                    if self.kalanDakika(dersler[i]['saat'])<=3:
                        self.dersAc(i)
                else:
                    dersler[i]['acildi'] = True #tarih geçmiş, geçmiş olsun
                    ilkders=-1
        self.ders_program_guncelle()
        #self.ders_zamanla(0)



# login olamadıysa kullanıcı-şifre yanlış mesajı ver
# cookies config yaz
# time-table config yaz
# time-table refresh tarihini config yaz

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('OYS')
    window = AnaPencere()
    sys.exit(app.exec_())


