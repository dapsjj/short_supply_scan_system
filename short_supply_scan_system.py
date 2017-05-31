# -*- coding: UTF-8 -*-
import os
import time
import datetime
import threading
import Tkinter
import shutil
import schedule
# import tkMessageBox
import mp3play
import cv2

'''
功能：开启摄像头监控空货架，启动后点击"打开摄像头"，自动开启摄像头，点击"关闭摄像头"则关闭摄像头
      点击"开始监测"，每5秒检测一次当天是否有缺货的货架，有就播放提示音，没有则不提示，点击"停止监测"则终止检测。
'''


class mythread_check(threading.Thread):
    global vc
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        root.flag = True#启动标志,点击"开始"时变为True，点击"停止"时变为False
        root.stop = False#终止标志,点击"开始"时为False，点击"停止"时变为True
        while root.flag:
            # vedio_capture()
            check_null_dir(short_work_path)
            schedule.run_pending()

class mythread_vedio(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        vedio_capture()

root = Tkinter.Tk()
root.title('实时监测空货架系统')
root.geometry('400x150+500+300')
root.resizable(False, False)

# today_path =time.strftime('%Y-%m-%d')
disk_short_supply_path = 'C:\\short_supply_pictures'
disk_normal_supply_path = 'C:\\normal_supply_pictures'
short_work_path = 'C:\\short_supply_pictures\\' + time.strftime('%Y-%m-%d')
normal_work_path = 'C:\\normal_supply_pictures\\' + time.strftime('%Y-%m-%d')


#开启摄像头捕捉关键帧
def vedio_capture():
    btn_openVideo['state'] = 'disabled'
    btn_closeVideo['state'] = 'normal'
    lbl['text'] = '摄像头已开启!'
    create_dirs()
    # vc = cv2.VideoCapture(0)  # 读入摄像头
    vc = cv2.VideoCapture('short_supply1.avi')  # 读入视频文件
    pic = 1
    c = 1
    timeF = 10  # 视频帧计数间隔频率
    rval, frame = vc.read()
    # while True:  # 循环读取摄像头
    while rval:  # 循环读取视频帧
        rval, frame = vc.read()
        if (pic % timeF == 5):
            body_cascade = cv2.CascadeClassifier(
                'C:\\OpenCV2.4.9\\opencv\\sources\\data\\haarcascades\\test_short_supply.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            bodys = body_cascade.detectMultiScale(gray, 1.1, 20, cv2.CASCADE_SCALE_IMAGE, (55, 55))
            flag = False
            for (x, y, w, h) in bodys:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                flag = True
            if flag == True:
                cv2.imwrite(short_work_path + '\\' + datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')+'_'+str(c) + '.jpg', frame)  # 保存
            else:
                cv2.imwrite(normal_work_path + '\\' +datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')+'_'+ str(c) + '.jpg',frame)  # 保存
            c += 1
        pic = pic + 1
        # time.sleep(0.5)
        # cv2.imshow('Video', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'): #按q键关闭摄像头
            # break
        # vc.release()

def close_video():#关闭摄像头
    btn_closeVideo['state'] = 'disabled'
    btn_openVideo['state'] = 'normal'
    lbl['text'] = '摄像头已关闭!'
    # cv2.VideoCapture(0).release()  # 读入摄像头
    cv2.VideoCapture('short_supply1.avi').release()# 读入视频文件

def create_dirs(): #创建文件夹
    if not os.path.exists(short_work_path):
        os.makedirs(short_work_path)
    if not os.path.exists(normal_work_path):
        os.makedirs(normal_work_path)

def check_null_dir(dirr): #扫描文件夹
    # root.flag = True
    if root.stop == True:
        return

    global pic_path
    pic_path=''
    if not os.path.exists(dirr):
        # pass
        lbl['text'] = '路径' + dirr + '不存在!'
        btn_startCheck['state'] = 'normal'
        btn_stopCheck['state'] = 'disabled'
        root.flag = False
    else:
        if os.path.isdir(dirr):
            for p in os.listdir(dirr):
                d  = os.path.join(dirr,p)
                if (os.path.isdir(d) == True):
                    check_null_dir(d)
        if  os.listdir(dirr):
            if dirr.count('\\')==2:
                filename = 'C:\\message.mp3'
                mp3 = mp3play.load(filename)
                mp3.play()
                len = mp3.seconds()
                time.sleep(len)
                mp3.stop()
                pic_path = dirr
                if root.stop == False:
                    lbl['text'] = '路径' + pic_path + '\n货架缺货,请及时确认!'
                else:
                    lbl['text'] = '监测已停止!'

                time.sleep(5)

def remove_threedaysago_files():
    today = datetime.date.today()
    threedaysago = today - datetime.timedelta(days=3)
    for file in os.listdir(disk_short_supply_path):
        if os.path.isdir(os.path.join(disk_short_supply_path, file)):
            if file <= str(threedaysago):
                shutil.rmtree(os.path.join(disk_short_supply_path, file))
    for file in os.listdir(disk_normal_supply_path):
        if os.path.isdir(os.path.join(disk_normal_supply_path, file)):
            if file <= str(threedaysago):
                shutil.rmtree(os.path.join(disk_normal_supply_path, file))

schedule.every().day.at("12:00").do(remove_threedaysago_files)

# 关闭程序时执行的函数代码
def closeWindow():
    root.flag = False
    root.destroy()

# root.protocol('关闭窗口', closeWindow)

def openVideo():
    t = mythread_vedio()
    t.start()

btn_openVideo = Tkinter.Button(root, text='打开摄像头',command=openVideo)
btn_openVideo.place(x=10, y=10, width=80, height=20)



btn_closeVideo = Tkinter.Button(root, text='关闭摄像头',command=close_video)
btn_closeVideo.place(x=110, y=10, width=80, height=20)

def btn_startCheck_Click():
    # 每次单击“开始”按钮启动新线程
    lbl['text'] = '监测已开始!'
    create_dirs()
    t = mythread_check()
    t.start()
    btn_startCheck['state'] = 'disabled'
    btn_stopCheck['state'] = 'normal'


btn_startCheck = Tkinter.Button(root, text='开始监测',command=btn_startCheck_Click)
btn_startCheck.place(x=210, y=10, width=80, height=20)


def btn_stopCkeck_Click():
    # 单击“停止”按钮结束
    # lbl['text'] = ''
    btn_startCheck['state'] = 'normal'
    btn_stopCheck['state'] = 'disabled'
    # root.update()
    root.flag = False
    root.stop = True
    lbl['text'] = '监测已停止!'

btn_stopCheck = Tkinter.Button(root,text='停止监测',command=btn_stopCkeck_Click)
btn_stopCheck['state'] = 'disabled'
btn_stopCheck.place(x=310, y=10, width=80, height=20)

lbl = Tkinter.Label(root, text='')
lbl.place(x=20, y=60, width=350, height=50)

# 启动Tkinter主程序
root.mainloop()
