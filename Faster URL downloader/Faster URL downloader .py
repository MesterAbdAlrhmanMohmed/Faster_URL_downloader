from PyQt6 import QtWidgets as qt
from PyQt6 import QtGui as qt1
from PyQt6 import QtCore as qt2
import requests
class DownloaderThread(qt2.QThread):
    progress=qt2.pyqtSignal(int)
    finished=qt2.pyqtSignal(str)
    download_finished = qt2.pyqtSignal()  # إشارة جديدة للإشارة عن انتهاء التحميل
    def __init__(self, url, path):
        super().__init__()
        self.url=url
        self.path=path
    def run(self):
        # هنا نبدأ بتعريف الدالة التي سيتم تنفيذها عند بدء التحميل.
        try:
            # نقوم بتحديد اسم الملف المراد تنزيله من الرابط باستخدام آخر جزء من الرابط بعد الشرطة.
            file_name=self.url.split("/")[-1]
            # نقوم بتحديد المسار الكامل الذي سيتم حفظ الملف فيه بالاستفادة من المسار الذي اختاره المستخدم.
            save_path=f"{self.path}/{file_name}"
            # نستخدم طلب GET لجلب الملف بالرابط المعطى بالأجزاء.
            with requests.get(self.url, stream=True) as r:
                # نحصل على حجم الملف الكلي لنقوم بحساب التقدم.
                total_size=int(r.headers.get("content-length"))
                # نقوم بتعريف متغير لتتبع حجم الملف المنزل.
                downloaded=0
                # نقوم بفتح ملف للكتابة بنفس المسار الذي حددناه.
                with open(save_path, "wb") as file:
                    # نبدأ في قراءة البيانات المستقبلة وكتابتها في الملف.
                    for data in r.iter_content(chunk_size=1024):
                        file.write(data)
                        # نزيد قيمة المتغير المستخدم لتتبع حجم الملف المنزل.
                        downloaded += len(data)
                        # نقوم بحساب النسبة المئوية للتقدم.
                        progress_percentage = int((downloaded / total_size) * 100)
                        # نقوم بإرسال إشارة بالتقدم الحالي إلى واجهة المستخدم.
                        self.progress.emit(progress_percentage)
            # في حال نجاح التنزيل، نرسل إشارة بأن التنزيل اكتمل بنجاح.
            self.finished.emit("تم التنزيل بنجاح")
            # بعد ذلك، نرسل إشارة بأن التنزيل انتهى.
            self.download_finished.emit()  # إرسال إشارة بانتهاء التحميل
        # في حال حدوث أي خطأ، نقوم بإرسال إشارة بأن التنزيل فشل.
        except:
            self.finished.emit("حدث خطأ أثناء التنزيل, ربما الرابط غير صحيح, أو هناك مشكلة في الإنترنت")
class main (qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Faster URL downloader")
        self.حفظ=qt.QPushButton("تحديد مكان الحفظ أولا O")
        self.حفظ.setDefault(True)
        self.حفظ.setShortcut("o")
        self.حفظ.clicked.connect(self.opinFile)
        self.إظهار=qt.QLabel("مسار الحفظ")
        self.المسار=qt.QLineEdit()
        self.المسار.setReadOnly(True)
        self.المسار.setAccessibleName("مسار الحفظ هو")
        self.التقدم=qt.QProgressBar()
        self.التقدم.setRange(0,100)
        self.إظهار1=qt.QLabel("إدخال الرابط المباشر")
        self.رابط=qt.QLineEdit()
        self.رابط.setAccessibleName("إدخال الرابط")
        self.رابط.setAccessibleDescription("يرجى إدخال رابط مباشر")
        self.تحميل=qt.QPushButton("بدء التحميل D")
        self.تحميل.setShortcut("d")
        self.تحميل.setDefault(True)
        self.تحميل.setDisabled(False)
        self.تحميل.clicked.connect(self.start_download)
        self.إلغاء=qt.QPushButton("إلغاء التحميل C")
        self.إلغاء.setShortcut("c")
        self.إلغاء.setDefault(True)
        self.إلغاء.setDisabled(True)
        self.إلغاء.clicked.connect(self.cancel_download)
        self.حول=qt.QPushButton("حول البرنامج")
        self.حول.setDefault(True)
        self.حول.clicked.connect(self.ab)                
        l=qt.QVBoxLayout()        
        l.addWidget(self.حفظ)
        l.addWidget(self.إظهار)
        l.addWidget(self.المسار)
        l.addWidget(self.التقدم)
        l.addWidget(self.إظهار1)
        l.addWidget(self.رابط)
        l.addWidget(self.تحميل)
        l.addWidget(self.إلغاء)
        l.addWidget(self.حول)        
        w=qt.QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)                
    def start_download(self):
        url=self.رابط.text()
        if not url:
            qt.QMessageBox.warning(self, "تنبيه", "الرجاء إدخال رابط الملف")
            return
        path=self.المسار.text()
        if not path:
            qt.QMessageBox.warning(self, "تنبيه", "الرجاء تحديد مكان الحفظ")
            return        
        self.download_thread = DownloaderThread(url, path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.show_message)
        self.download_thread.start()
        self.تحميل.setDisabled(True)
        self.إلغاء.setEnabled(True)
    def cancel_download(self):
        الرد=qt.QMessageBox.question(self, "تنبيه", "هل أنت متأكد من إلغاء عملية التنزيل؟",
        qt.QMessageBox.StandardButton.Yes | qt.QMessageBox.StandardButton.No)
        if الرد==qt.QMessageBox.StandardButton.Yes:
            self.download_thread.terminate()
            self.التقدم.setValue(0)
            self.تحميل.setDisabled(False)
            self.إلغاء.setDisabled(True)            
            qt.QMessageBox.warning(self, "تنبيه", "تم إلغاء التحميل بنجاح, لكن تعذر على البرنامج أخذ الإذن لحذف الملف الذي كان يتم تحميله, إذهب الى المسار المحدد وقم بحذف الملف من هناك")
    def update_progress(self, progress):
        self.التقدم.setValue(progress)
    def show_message(self, message):
        qt.QMessageBox.information(self, "تنبيه", message)
        self.تحميل.setEnabled(True)
        self.إلغاء.setDisabled(True)
        self.التقدم.setValue(0)
    def ab(self):
        qt.QMessageBox.information(self,"تنبيه","مرحبا بكم في برنامج Faster URL downloader, هذا البرنامج يقوم بتنزيل الملفات من الروابط المباشرة بأي حجم, إختصارات الأزرار مكتوبى على الأزرار, أتمنا لكم تجربة ممتعة, مع تحياتي, مطور البرنامج, عبد الرحمن محمد")
    def opinFile(self):
        file=qt.QFileDialog()
        file.setFileMode(qt.QFileDialog.FileMode.Directory)
        if file.exec()==qt.QFileDialog.DialogCode.Accepted:
            self.المسار.setText(file.selectedFiles()[0])                                 
app=qt.QApplication([])
app.setStyle('fusion')
w=main()
w.show()
app.exec()