#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QColorDialog, QMainWindow,
    QFileDialog, QMessageBox, QFontDialog
)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QDateTime

# DOSYA YOLLARI
BASE_DIR = "/opt/not_alma_proje" if os.path.exists("/opt/not_alma_proje") else os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, "not.ui")
ICON_PATH = os.path.join(BASE_DIR, "notkapak2.png")

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Arayüzü Yükle
        try:
            uic.loadUi(UI_PATH, self)
        except Exception as e:
            print(f"HATA: {UI_PATH} yüklenemedi! {e}")
            sys.exit(1)

        # Yedekleme Yolu
        home = os.path.expanduser("~")
        self.yedek_dosya_adi = os.path.join(home, ".not_yedek_kayit.txt")
        self.masaustu_yolu = os.path.join(home, "Masaüstü") if os.path.exists(os.path.join(home, "Masaüstü")) else os.path.join(home, "Desktop")

        self.setWindowTitle("NOT ALMA PRO")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.InitWindow()
        self.notu_geri_yukle()

        # SAAT GÜNCELLEME
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.saati_guncelle)
        self.timer.start(1000)

        # OTOMATİK KAYIT
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.otomatik_kaydet)

        if hasattr(self, 'textEdit'):
            self.textEdit.textChanged.connect(self.yazi_degisti)

    def InitWindow(self):
        try:
            # Menü İşlemleri
            if hasattr(self, 'TXTBUTON'): self.TXTBUTON.triggered.connect(self.txt_disa_aktar)
            if hasattr(self, 'pdf'): self.pdf.triggered.connect(self.pdf_disa_aktar)
            if hasattr(self, 'CIK2'): self.CIK2.triggered.connect(self.close)
            if hasattr(self, 'FONT'): self.FONT.triggered.connect(self.font_degistir)
            if hasattr(self, 'renk'): self.renk.triggered.connect(self.renk_degistir)

            # Tema Radio Button Bağlantıları
            if hasattr(self, 'aciktema'): self.aciktema.clicked.connect(self.tema_acik)
            if hasattr(self, 'kapali'): self.kapali.clicked.connect(self.tema_kapali)

        except Exception as e:
            print(f"Bağlantı Hatası: {e}")

    # --------------- Saat ----------------
    def saati_guncelle(self):
        if hasattr(self, 'saat'):
            simdi = QDateTime.currentDateTime().toString("dd-MM-yyyy hh:mm:ss")
            self.saat.setText(simdi)

    # --------------- Tema ----------------
    def saat_rengini_ayarla(self, koyu_arkaplan: bool):
        if hasattr(self, 'saat'):
            renk = "white" if koyu_arkaplan else "black"
            self.saat.setStyleSheet(f"color: {renk};")

    def tema_acik(self):
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
        if hasattr(self, 'textEdit'):
            self.textEdit.setStyleSheet("background-color: white; color: black;")
        self.saat_rengini_ayarla(False)

    def tema_kapali(self):
        self.setStyleSheet("QMainWindow { background-color: #2e2e2e; }")
        if hasattr(self, 'textEdit'):
            self.textEdit.setStyleSheet("background-color: #1e1e1e; color: #00ff00;") # Retro yeşil
        self.saat_rengini_ayarla(True)

    # --------------- Yedek ----------------
    def notu_geri_yukle(self):
        if os.path.exists(self.yedek_dosya_adi):
            try:
                with open(self.yedek_dosya_adi, "r", encoding="utf-8") as f:
                    self.textEdit.setPlainText(f.read())
            except: pass

    def yazi_degisti(self):
        self.autosave_timer.start(1000)

    def otomatik_kaydet(self):
        try:
            icerik = self.textEdit.toPlainText()
            with open(self.yedek_dosya_adi, "w", encoding="utf-8") as f:
                f.write(icerik)
        except: pass

    # --------------- Font / Renk ----------------
    def font_degistir(self):
        font, ok = QFontDialog.getFont()
        if ok: self.textEdit.setFont(font)

    def renk_degistir(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.textEdit.setTextColor(color)

    # --------------- Dışa Aktar ----------------
    def txt_disa_aktar(self):
        yol, _ = QFileDialog.getSaveFileName(self, "TXT Kaydet", self.masaustu_yolu, "Metin (*.txt)")
        if yol:
            with open(yol, "w", encoding="utf-8") as f:
                f.write(self.textEdit.toPlainText())
            QMessageBox.information(self, "Başarılı", "Dosya kaydedildi!")

    def pdf_disa_aktar(self):
        yol, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", self.masaustu_yolu, "PDF (*.pdf)")
        if yol:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(yol)
            self.textEdit.document().print_(printer)
            QMessageBox.information(self, "Başarılı", "PDF oluşturuldu!")

# --------------- Uygulama Başlat ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())