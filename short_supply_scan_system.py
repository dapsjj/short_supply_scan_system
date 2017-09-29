# -*- coding: UTF-8 -*-
import os
import time
import datetime
import threading
# import tkinter #python3.5时
import Tkinter #python2.7时
import shutil
import schedule
# import tkinter.messagebox #python3.5时
import tkMessageBox #python2.7时
import cv2
import re
# import tkinter.filedialog #python3.5时
import tkFileDialog #python2.7时
# from pygame import mixer #python3.5时
import mp3play #python2.7版本使用mp3play好用,但是python3.5时,使用mp3play时出错,为了保证python3.5能正常播放mp3,则python3.5时使用pygame模块的mixer

# import win32com

'''
功能：开启摄像头监控空货架，启动后点击"打开摄像头"，自动开启摄像头，点击"关闭摄像头"则关闭摄像头.
      点击"上传视频"可以监测视频.
      摄像头每1秒截图一次,视频每10帧截图一次.
      点击"开始监测"，每3秒检测一次当天是否有缺货的货架，有就播放提示音，没有则不提示，点击"停止监测"则终止监测。
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
            check_all_null_dir(short_work_path)
            schedule.run_pending()

class mythread_vedio(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        vedio_capture()

root = Tkinter.Tk()
root.title('監視空棚システム')
root.geometry('420x250+400+200')
root.resizable(False, False)

# today_path =time.strftime('%Y-%m-%d')
disk_short_supply_path = 'C:\\short_supply_pictures'
disk_normal_supply_path = 'C:\\normal_supply_pictures'
short_work_path = 'C:\\short_supply_pictures\\' + time.strftime('%Y-%m-%d')
normal_work_path = 'C:\\normal_supply_pictures\\' + time.strftime('%Y-%m-%d')
short_monitor_path = short_work_path+'\\'+'monitor'
normal_monitor_path = normal_work_path+'\\'+'monitor'

#检测空目录
def check_all_null_dir(dir):
    i=0
    num=0
    if os.path.isdir(dir):
        for p in os.listdir(dir):
            d = os.path.join(dir, p)
            if (os.path.isdir(d) == True):
                i+=1
                if not os.listdir(d):
                    num+=1
        if i ==num and root.stop == False:
            lbl['text'] = '監視が始まった!'


#开启摄像头捕捉关键帧
def vedio_capture():
    btn_openVideo['state'] = 'disabled'
    btn_closeVideo['state'] = 'normal'
    lbl['text'] = 'カメラが開いている!'
    create_dirs()
    vc = cv2.VideoCapture(0)  # 读入摄像头
    # vc = cv2.VideoCapture('short_supply1.avi')  # 读入视频文件
    pic = 1
    c = 1
    timeF = 10  # 视频帧计数间隔频率
    openFlag=False #摄像头正常打开时，此标志变为True
    if vc.isOpened():#判断是否正常打开
        rval, frame = vc.read()
        openFlag = True
    else:
        rval = False
        lbl['text'] = 'カメラは開くできません!'
    while openFlag:  # 循环读取摄像头
    # while rval:  # 循环读取视频帧
        rval, frame = vc.read()
        if (pic % timeF == 5):
            body_cascade = cv2.CascadeClassifier(
                'C:\\OpenCV2.4.9\\opencv\\sources\\data\\haarcascades\\test_short_supply.xml')
            if len(frame.shape) == 3 or len(frame.shape) == 4:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            bodys = body_cascade.detectMultiScale(gray, 1.1, 20, cv2.CASCADE_SCALE_IMAGE, (55, 55))
            flag = False
            for (x, y, w, h) in bodys:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                flag = True
            if flag == True:
                if not os.path.exists(short_monitor_path):
                    os.makedirs(short_monitor_path)
                cv2.imwrite(short_monitor_path + '\\' + datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')+'_'+str(c) + '.jpg', frame)  # 保存
            else:
                if not os.path.exists(normal_monitor_path):
                    os.makedirs(normal_monitor_path)
                cv2.imwrite(normal_monitor_path + '\\' +datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')+'_'+ str(c) + '.jpg',frame)  # 保存
            c += 1
        pic = pic + 1
        time.sleep(1)
        # cv2.imshow('Video', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'): #按q键关闭摄像头
            # break
        # vc.release()

def close_video():#关闭摄像头
    btn_closeVideo['state'] = 'disabled'
    btn_openVideo['state'] = 'normal'
    lbl['text'] = 'カメラが閉鎖されている!'
    cv2.VideoCapture(0).release()  # 读入摄像头
    # cv2.VideoCapture('short_supply1.avi').release()# 读入视频文件

def create_dirs(): #创建文件夹
    if not os.path.exists(short_monitor_path):
        os.makedirs(short_monitor_path)
    if not os.path.exists(normal_monitor_path):
        os.makedirs(normal_monitor_path)

def check_null_dir(dirr): #扫描文件夹
    # root.flag = True
    if root.stop == True:
        return

    global pic_path
    pic_path=''

    if not os.path.exists(dirr):
        # pass
        lbl['text'] = '経路' + dirr + '存在しない!'
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
            if dirr.count('\\')==3:
                filename = 'C:\\message.mp3'
                mp3 = mp3play.load(filename) #python2.7时使用mp3play
                mp3.play()
                len = mp3.seconds()
                time.sleep(len)
                mp3.stop()
                # mixer.init()  # python3.5时使用mixer
                # mixer.music.load(filename)
                # mixer.music.play()
                pic_path = dirr
                if root.stop == False:
                    lbl['text'] = '経路' + pic_path + '\n棚欠品、確認して!'
                else:
                    lbl['text'] = '監視が止まっている!'
        time.sleep(3) #3秒检查一次

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

# btn_openVideo = Tkinter.Button(root, text='打开摄像头',command=openVideo)
# btn_openVideo.place(x=10, y=10, width=80, height=20)



# btn_closeVideo = Tkinter.Button(root, text='关闭摄像头',command=close_video)
# btn_closeVideo.place(x=110, y=10, width=80, height=20)

def btn_startCheck_Click():
    # 每次单击“开始”按钮启动新线程
    lbl['text'] = '監視が始まった!'
    create_dirs()
    t = mythread_check()
    t.start()
    btn_startCheck['state'] = 'disabled'
    btn_stopCheck['state'] = 'normal'

# btn_startCheck = Tkinter.Button(root, text='开始监测',command=btn_startCheck_Click)
# btn_startCheck.place(x=210, y=10, width=80, height=20)

def btn_stopCkeck_Click():
    # 单击“停止”按钮结束
    # lbl['text'] = ''
    btn_startCheck['state'] = 'normal'
    btn_stopCheck['state'] = 'disabled'
    # root.update()
    root.flag = False
    root.stop = True
    lbl['text'] = '監視が止まっている!'

def get_file():
    today_path = time.strftime('%Y-%m-%d')
    filename = tkFileDialog.askopenfilename(title="ビデオを選択",filetypes = [('ビデオ', 'MPEG'),('ビデオ', 'AVI'),('ビデオ', 'FLV'),('ビデオ', 'RMVB'),('ビデオ', 'MP4')])
    CN_Pattern = re.compile(u'[\u4E00-\u9FBF]+')
    JP_Pattern = re.compile(u'[\u3040-\u31fe]+')
    if filename:
        newFile = filename.split('/')[-1].split('.')[0]
        if not os.path.exists(short_work_path+'\\'+ newFile):
            os.makedirs(short_work_path+'\\'+ newFile)
        if not os.path.exists(normal_work_path+'\\'+ newFile):
            os.makedirs(normal_work_path+'\\'+ newFile)
        CN_Match = CN_Pattern.search(filename)
        JP_Match = JP_Pattern.search(filename)
        if CN_Match:
            # print u'有中文：%s' % (CN_Match.group(0),)
            lbl['text'] = 'ファイルの経路とファイル名は中国語ができません,修正してくだせい!'
            return
        elif JP_Match:
            # print u'有日文：%s' % (JP_Match.group(0),)
            lbl['text'] = 'ファイルの経路とファイル名は日本語ができません,修正してくだせい!'
            return

        vc = cv2.VideoCapture(filename)  # 读入视频文件
        pic = 1
        c = 1
        timeF = 10  # 视频帧计数间隔频率
        openFlag = False  # 视频正常打开时，此标志变为True
        if vc.isOpened():  # 判断视频是否正常打开
            rval, frame = vc.read()
            openFlag = True
        else:
            rval = False
            lbl['text'] = 'ビデオは失敗を開く!'
        while rval:  # 循环读取视频帧
            rval, frame = vc.read()
            if (pic % timeF == 5):
                body_cascade = cv2.CascadeClassifier('C:\\OpenCV2.4.9\\opencv\\sources\\data\\haarcascades\\test_short_supply.xml')
                if len(frame.shape) == 3 or len(frame.shape) == 4:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                else:
                    gray = frame
                bodys = body_cascade.detectMultiScale(gray,1.1,20,cv2.CASCADE_SCALE_IMAGE, (55, 55))
                flag = False
                for (x, y, w, h) in bodys:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    flag = True
                if flag == True:
                    cv2.imwrite(short_work_path  + '\\' + newFile + '\\' + datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S') + '_' + str(c) + '.jpg', frame)  # 保存
                else:
                    cv2.imwrite(normal_work_path + '\\' + newFile + '\\' + datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S') + '_' + str(c) + '.jpg', frame)  # 保存
                c += 1
            pic = pic + 1
        lbl['text'] = 'ビデオがアップロードされている!'
    else:
        return

# btn_stopCheck = Tkinter.Button(root,text='停止监测',command=btn_stopCkeck_Click)
# btn_stopCheck['state'] = 'disabled'
# btn_stopCheck.place(x=310, y=10, width=80, height=20)

lbl = Tkinter.Label(root, text='',font = ("Arial, 10"))
lbl.place(x=40, y=120, width=350, height=50)

#
realTimeSet = Tkinter.LabelFrame(root, text='リアル監視')
btn_openVideo=Tkinter.Button(realTimeSet, text='カメラ開ける',command=openVideo)
btn_openVideo.grid(row=0, column=0, padx=2, pady=2)
btn_closeVideo = Tkinter.Button(realTimeSet, text='カメラ消す',command=close_video)
btn_closeVideo.grid(row=0, column=1, padx=2, pady=2)
realTimeSet.grid(row=0, column=0, padx=(10), pady=(5),ipadx=(5), ipady=(5))

uploadVedioSet = Tkinter.LabelFrame(root,text='ビデオ監視')
btn_uploadVedio=Tkinter.Button(uploadVedioSet, text='ビデオアップロード',command=get_file)
btn_uploadVedio.grid(row=0, column=0, padx=2, pady=2)
uploadVedioSet.grid(row=0, column=1, padx=(10), pady=(5),ipadx=(3), ipady=(5))

monitorSet = Tkinter.LabelFrame(root, text='モニタリング')
btn_startCheck = Tkinter.Button(monitorSet, text='スタート',command=btn_startCheck_Click)
btn_startCheck.grid(row=0, column=0, padx=2, pady=2)
btn_stopCheck = Tkinter.Button(monitorSet,text='ストップ',command=btn_stopCkeck_Click)
btn_stopCheck['state'] = 'disabled'
btn_stopCheck.grid(row=0, column=1, padx=2, pady=2)
monitorSet.grid(row=0, column=2, padx=(10), pady=(5),ipadx=(5), ipady=(5))
#


# 启动Tkinter主程序
root.mainloop()
