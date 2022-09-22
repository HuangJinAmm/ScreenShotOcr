#!/usr/bin/env python3
# 创建者：黄金
# 创建时间:2022/9/18
# 版本:V1.0

from cgi import print_arguments
import io
import sys

import pyperclip
from PIL import Image
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
import cv2

from paddleocr import PaddleOCR,PPStructure

# TABLE_KEY = "姓名 性别 民族 地址 年龄 学历 联系电话 电话 电子邮件 电子邮箱 email 籍贯 工作经历 项目 ".split(" ")

det_model_dir = "./ch_PP-OCRv3_det_infer"
rec_model_dir = "./ch_PP-OCRv3_rec_infer"
# rec_char_dict_path = "C:\\Users\\黄金\\.paddleocr\\whl\\rec\\ch\\ch_PP-OCRv3_rec_infer"
cls_model_dir = "./ch_ppocr_mobile_v2.0_cls_infer"
table_model_dir = "./ch_ppstructure_mobile_v2.0_SLANet_infer"
layout_model_dir = "./picodet_lcnet_x1_0_fgd_layout_cdla_infer"
# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
# ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
ocr = PaddleOCR(det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
                # rec_char_dict_path=rec_char_dict_path,
                cls_model_dir=cls_model_dir,
                use_angle_cls=True)

table_engine = PPStructure(det_model_dir=det_model_dir,
                           rec_model_dir=rec_model_dir,
                           table_model_dir=table_model_dir,
                        #    layout_model_dir=layout_model_dir,
                            layout = False,
                           show_log=True,structure_version="PP-Structurev2")
# table_engine = PPStructure(layout=False, show_log=True)
class SystemTrayIcon(QSystemTrayIcon):
    exact_keyV = pyqtSignal(str)  # show action
    exact_data = pyqtSignal(str)  # show action
    quit = pyqtSignal()         # quit action

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        

        #菜单配置
        self.setIcon(QIcon("./res/2.png"))
        self.setToolTip("文字识别小工具")
        self.tray_menu = None
        self.setup_menu()

        # 点击信号处理
        # self.messageClicked.connect(self.on_message_clicked)
        # self.activated.connect(self.on_activated)

    def setup_menu(self):
        self.tray_menu = QMenu()  # 右键菜单

        action_exact = QAction(self)
        action_exact_table = QAction(self)
        action_exact_kv = QAction(self)
        action_quit = QAction(self)
        # action_setting = QAction(self)
        # action_about = QAction(self)

        # 设置右键菜单图标
        action_exact.setIcon(QIcon("./res/2.png"))
        action_quit.setIcon(QIcon("./res/1.gif"))
        action_exact_kv.setIcon(QIcon("./res/3.png"))
        action_exact_table.setIcon(QIcon("./res/3.png"))
        # action_setting.setIcon(QIcon("./res/glyphicons-281-settings.png"))
        # action_about.setIcon(QIcon("./res/glyphicons-195-question-sign.png"))

        # -- 二级菜单
        # self.sub_menu = QMenu()
        # action_setting_setting1 = QAction(self)
        # action_setting_setting1.setText("打开配置")
        # action_setting_setting1.setIcon(QIcon("../res/glyphicons-281-settings.png"))
        # action_setting_setting1.setIcon(QIcon(":/img/about"))

        # self.sub_menu.addAction(action_setting_setting1)
        # action_setting.setMenu(self.sub_menu)

        # 设置菜单文本
        action_exact.setText("截图识别文字")
        action_quit.setText("退出")
        action_exact_kv.setText("识别关键信息")
        action_exact_table.setText("识别表格")
        # action_setting.setText("设置")
        # action_about.setText("关于")

        self.tray_menu.addAction(action_exact)
        self.tray_menu.addAction(action_exact_kv)
        self.tray_menu.addAction(action_exact_table)
        self.tray_menu.addAction(action_quit)
        # self.tray_menu.addAction(action_setting)
        # self.tray_menu.addAction(action_about)

        self.setContextMenu(self.tray_menu)
        action_exact.triggered.connect(self.do_exact_data)
        action_exact_kv.triggered.connect(self.do_exact_keyValue)
        action_exact_table.triggered.connect(self.do_exact_table)
        action_quit.triggered.connect(self.quit)
        # action_about.triggered.connect(self.welcome)
        # action_setting.triggered.connect(self.openConfig)

        self.quit.connect(self.quit)

    # def openConfig(self):
    #     '''打开配置文件,约定为与当前执行文件通路径下的config.ini文件'''
    #     os.startfile(CONFIG_NAME) 
    

    def on_activated(self, reason):
        """托盘图标被点击
            有三种情况：左单击，左双击，右单击
        """

        print("on_activated {}".format(reason))
        if reason == QSystemTrayIcon.DoubleClick:
            self.do_exact_data()
        elif reason == QSystemTrayIcon.Trigger:
            self.do_exact_data()


    # def on_message_clicked(self):
    #     """弹出消息被点击"""
    #     print("on messaged clicked")

    def welcome(self):
        self.showMessage("截图识别文字小工具", "打开成功！", msecs=1000)
        # self.exact_data.emit()

    def show(self):
        super(SystemTrayIcon, self).show()
        QTimer.singleShot(1000, self.welcome)
    
    def do_exact_keyValue(self):
        self.exact_keyV.emit('todo')

    def do_exact_table(self):
        self.exact_data.emit('table')

    def do_exact_data(self):
        self.exact_data.emit('data')


class Snipper(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.setWindowTitle("TextShot")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog
        )
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)

        self.system_tray = SystemTrayIcon(self)
        self.system_tray.show()

        # signal & slot
        self.system_tray.exact_data.connect(self.exactData)
        self.system_tray.exact_keyV.connect(self.exactData)
        self.system_tray.quit.connect(self.close)

    def exactData(self,action_type):
        print("动作类型：",action_type)
        self.action_type = action_type
        self.screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).grabWindow(0)
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(self.screen))
        self.setPalette(palette)

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.start, self.end = QtCore.QPoint(), QtCore.QPoint()
        self.show() 

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # QtWidgets.QApplication.quit()
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.hide()

        return super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRect(0, 0, self.width(), self.height())

        if self.start == self.end:
            return super().paintEvent(event)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.setBrush(painter.background())
        painter.drawRect(QtCore.QRect(self.start, self.end))
        return super().paintEvent(event)

    def mousePressEvent(self, event):
        self.start = self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start == self.end:
            return super().mouseReleaseEvent(event)

        self.hide()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        QtWidgets.QApplication.processEvents()
        shot = self.screen.copy(
            min(self.start.x(), self.end.x()),
            min(self.start.y(), self.end.y()),
            abs(self.start.x() - self.end.x()),
            abs(self.start.y() - self.end.y()),
        )
        processImage(shot,self.action_type)
        # QtWidgets.QApplication.quit()


def processImage(img,action_type):
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QBuffer.ReadWrite)
    img.save(buffer, "PNG")
    pil_img = Image.open(io.BytesIO(buffer.data()))
    buffer.close()

    w = pil_img.width
    h = pil_img.height

    image_mat = np.asarray(pil_img)

    angle = get_minAreaRect(image_mat)
    print("角度",angle)
    pix =rotate_bound(image_mat,angle)
    
    # cv2.putText(pix, "angle: {:.2f} ".format(angle),(10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # print("[INFo] angle: {:.3f}".format(angle))	
    # cv2.imshow("imput", image_mat)	
    # cv2.imshow("output", pix)	
    # cv2.waitKey(0)	
     
    result=""
    try:
        if action_type == "data":
            resultList = ocr.ocr(pix, cls=True)
            result = resultCompose(w,h,resultList)
        elif action_type == "table":
            res = table_engine(pix)
            print("{}",res)
            result = res[0]['res']['html']
        else:
            resultList = ocr.ocr(pix, cls=True)
            result = getResultKeyValue(w,h,resultList)
        print(result)
        # for line in resultList:
        #     print(line)
        #     result += line[1][0]+"\r\n"
        # boxes = [line[0] for line in resultList]
        # txts = [line[1][0] for line in resultList]
        # scores = [line[1][1] for line in resultList]
        # im_show = draw_ocr(pil_img, boxes, txts, scores, font_path='./fonts/simfang.ttf')
        # im_show = Image.fromarray(im_show)
        # im_show.save('result_1.jpg')
    except RuntimeError as error:
        # print(f"ERROR: An error occurred when trying to process the image: {error}")
        notify(f"发生错误: {error}")
        return

    if result:
        pyperclip.copy(result)
        # print(f'INFO: Copied "{result}" to the clipboard')
        notify(f'已复制到剪切板:{result}')
    else:
        # print(f"INFO: Unable to read text from image, did not copy")
        notify(f"未识别到文字")


def notify(msg):
    trayicon = QtWidgets.QSystemTrayIcon(
        QtGui.QIcon(
            QtGui.QPixmap.fromImage(QtGui.QImage(1, 1, QtGui.QImage.Format_Mono))
        )
    )
    trayicon.show()
    trayicon.showMessage("识别完成", msg, QtWidgets.QSystemTrayIcon.NoIcon)
    trayicon.hide()

def resultCompose(width,height,resultList):
    tc = TextCompose(width,height,resultList)
    table = tc.getTableText()
    res = ""
    for row in table:
       res = res +"\r\n"+"\t".join(row) 
    return res

def getResultKeyValue(width,height,resultList):
    tc = TextCompose(width,height,resultList)
    table = tc.getTableText()
    

class TextCompose:
    
    def __init__(self,width,height,resultList) :
        self.width = width
        self.height = height
        self.textBlocks = []
        self.textComposed = {}
        for res in resultList:
            self.textBlocks.append(TextBolck(res[0],res[1][0]))
        row = 0
        preBlock = None
        #处理行
        for block in self.textBlocks:
            if block.eqY(preBlock) :
                self.textComposed[block] = [row]
            else:
                row = row + 1
                self.textComposed[block] = [row]
            preBlock = block
        self.textBlocks.sort(key=lambda x:x.xLeft)
        self.row = row + 1
        col = 0
        preBlock = None
        for block in self.textBlocks:
            if block.eqX(preBlock) :
                self.textComposed[block].append(col)
            else:
                col = col + 1
                self.textComposed[block].append(col)
            preBlock = block
        self.col = col + 1       

    def getTableText(self):
        tableText = [ [ "" for y in range(self.col)] for x in range(self.row)]
        for (tb,pos) in self.textComposed.items():
            tableText[pos[0]][pos[1]] = tb.text
        return tableText
    
class TextBolck:

    precision = 10

    def __init__(self,box,text) :
        self.yTop = int(box[0][1])
        self.yBottom = int(box[2][1])
        self.xLeft = int(box[0][0])
        self.xRigth = int(box[1][0])
        self.text = text
    
    @property
    def middleX(self):
        return int((self.xLeft + self.xRigth)/2)
    
    @property
    def middleY(self):
        return int((self.yBottom + self.yTop)/2)

    def eqX(self,other):
        if not other and not self:
            return True
        elif other and self:
            if abs(self.xLeft - other.xLeft) < TextBolck.precision or abs(self.xRigth-other.xRigth) < TextBolck.precision or abs(self.middleX - other.middleX) < TextBolck.precision:
                return True
            else:
                return False
        else:
            return False

    def eqY(self,other):
        if not other and not self:
            return True
        elif other and self:
            if abs(self.yTop - other.yTop ) < TextBolck.precision or abs(self.yBottom-other.yBottom) < TextBolck.precision or abs(self.middleY - other.middleY) < TextBolck.precision:
                return True
            else:
                return False
        else:
            return False

    # def cmpX(self,other):
    #     if not other:
    #         return 1
    #     # if  self.xRigth - other.xLeft < TextBolck.precision :
    #     if  self.xLeft - other.xLeft < TextBolck.precision :
    #         return 1
    #     elif self.xLeft - other.xLeft > TextBolck.precision:
    #         return -1
    #     else :
    #         return 0
    
    # def cmpY(self,other):
    #     if not other :
    #         return 1
    #     if  self.yTop - other.yTop < TextBolck.precision:
    #         return -1
    #     elif self.yTop - other.yTop > TextBolck.precision:
    #         return 1
    #     else :
    #         return 0
        
    def __hash__(self) -> int:
        return hash(self.text+str(self.xLeft)+str(self.xRigth)+str(self.yBottom)+str(self.yBottom))
    
    def __eq__(self,other) -> bool:
        return self.xLeft == other.xLeft and self.xRigth == other.xRigth and self.yBottom == other.yBottom and self.yTop == other.yTop and self.text == other.text
    
def rotate_bound(image,angle):
    (h,w)=image.shape[:2]
    (cX,cY) = (w//2,h//2)

    M = cv2.getRotationMatrix2D((cX,cY),angle,1.0)

    cos = np.abs(M[0,0])    
    sin = np.abs(M[0,1])    

    nW = int((h*sin)+(w*cos))
    # nH = int((h*cos)+(w*sin))

    nH = h
    return cv2.warpAffine(image,M,(nW,nH),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE) 


			
#获取图片旋转角度		
def get_minAreaRect(image):		
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)	
    gray = cv2.bitwise_not(gray)	
    thresh = cv2.threshold(gray, 0, 255,	
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))	
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        return -(90+angle)
    else:
        return -angle

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    snipper = Snipper(window)
    # snipper.show()
    sys.exit(app.exec_())