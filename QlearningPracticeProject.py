from tkinter import *
from tkinter.ttk import *
import random
import math
import os
import pickle
import time
import sys

class baseGame:
    def __init__(self,lowangle=False):
        self.author = "Aikko"
        self.width = 500
        self.height = 400
        self.boardwidth = 60
        self.rodheight = 60
        self.angle = -1
        self.pos= self.width/2
        self.lowangle = lowangle
        self.initAngle()
        self.save_Flag = False
        self.failedTime = 0
        self.successTime = 0
        self.maxSuccessTime = 50
        self.maxFailedTime = 50
        #=====
        self._keyDown=False
        self._keyCode=0
    def initAngle(self):
        if self.lowangle:
            _randA=random.randint(1,45)
            _randB=random.randint(135,179)
            self.angle = random.choice([_randA,_randB])
        else:
            self.angle = random.randint(1,179)
    
    def start(self):
        self.createCanvas()
    
    def createCanvas(self):
        self.root = Tk()
        self.root.title("QLearning Practice Project")
        self.root.geometry(str(self.width+1)+ "x" + str(self.height+1))
        self.root.resizable(False, False)
        
        self.canvas = Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()
        
        self.root.bind("<KeyPress>", self.keyPress)
        self.root.bind("<KeyRelease>", self.keyRelease)
        self.root.bind('<Destroy>', self._on_destroy)
        self.visionUpdate()
        self.root.after(10,self.actionMove)
        self.root.mainloop()
        
    def actionMove(self):
        if self._keyCode == 37 and self.pos > self.boardwidth*0.5:
            self.pos -= 1
            self.angleCompensate(-1,0.25)
        elif self._keyCode == 39 and self.pos < self.width-self.boardwidth*0.5:
            self.pos += 1
            self.angleCompensate(1,0.25)
        self.angleChange()
        if self.angle==0 or self.angle==180:
            self.failedTime+=1
        elif int(round(self.angle,1))==90:
            self.successTime+=1
        if self.failedTime>self.maxFailedTime:
            self.failedTime=0
            print('failed')
            self.restartGame()
        elif self.successTime>self.maxSuccessTime:
            self.successTime=0
            print('success')
            self.restartGame()
        self.visionUpdate()
        
        self.root.after(10,self.actionMove)
    
    def loseCheck(self):
        if self.angle==0 or self.angle==180:
            return True
    
    def winCheck(self):
        if self.angle==90:
            return True
        else:
            return False
        
    def checkwall(self,forwards):
        if forwards<0:
            if self.pos <= self.boardwidth*0.5:
                return False
            else:
                return True
        elif forwards>0:
            if self.pos >= self.width-self.boardwidth*0.5:
                return False
            else:
                return True
        else:
            return True
    
    def angleChange(self,weight=0.01):
        self.angle += (self.angle - 90) * weight
        if self.angle>180:
            self.angle=180
        if self.angle<0:
            self.angle=0
            
    def angleCompensate(self,forwards,rate):
        if forwards>0:
            _angleDifference=int(abs(self.angle-90)) if int(abs(self.angle-90))>1 else 1
            _attenuation=math.pow(1/_angleDifference,rate)
            self.angle += 3*_attenuation
        else:
            _angleDifference=int(abs(self.angle-90)) if int(abs(self.angle-90))>1 else 1
            _attenuation=math.pow(1/_angleDifference,rate)
            self.angle -= 3*_attenuation
        if self.angle>180:
            self.angle=180
        if self.angle<0:
            self.angle=0
    
    def visionUpdate(self):
        _board_y = self.height - 50
        self.canvas.delete("all")
        self.canvas.create_line(self.pos-self.boardwidth/2, _board_y, self.pos+self.boardwidth/2, _board_y, fill="white")
        self.rod_x = self.pos + self.boardwidth/2 * math.cos(math.radians(self.angle))
        self.rod_y = _board_y - self.boardwidth/2 * math.sin(math.radians(self.angle))
        self.canvas.create_line(self.pos, _board_y, self.rod_x, self.rod_y, fill="gold")
        self.root.update()
        
    def keyPress(self,event):
        self._keyDown=True
        self._keyCode=event.keycode
        
    def keyRelease(self,event):
        self._keyDown=False
        self._keyCode=0
        
    
    def restartGame(self):
        self.pos= self.width/2
        self.initAngle()
        self.visionUpdate()
        self.root.update()
    
    def saveDat(self):
        pass
    
    def _on_destroy(self, event):
        if self.save_Flag:
            self.saveDat()
        self.root.quit()
    
    def _Bot_keyPress(self,key):
        if key==-1:
            self._keyDown=True
            self._keyCode=37
        elif key==1:
            self._keyDown=True
            self._keyCode=39
        elif key==0:
            self._keyDown=False
            self._keyCode=0
    
    def _Bot_See(self):
        return int(round(self.angle,1))
    
class botGame(baseGame):
    def __init__(self,lowangle):
        super().__init__(lowangle)
        self.ACTIONS = ['left','stop','right'] #可用的动作
        self.action_code = {"left":-1,"stop":0,"right":1}
        self.EPSILON = 0.9 #贪婪度
        self.ALPHA = 0.1 #学习率
        self.GAMMA = 0.9 #奖励递减值
        self.save_Flag = True
        self.operatTime = 0
        self.buildingQtable()

    def createCanvas(self):
        self.root = Tk()
        self.root.title("QLearning Practice Project")
        self.root.geometry(str(self.width+301)+ "x" + str(self.height+1))
        self.root.resizable(False, False)

        self._Frame_Canvas = Frame(self.root, width=self.width, height=self.height)
        self._Frame_Canvas.place(anchor=CENTER,relx=0.5,rely=0.5,x=-151,y=0)
        
        self.canvas = Canvas(self._Frame_Canvas, width=self.width, height=self.height, bg="black")
        self.canvas.pack()
        
        self._Frame_Control = LabelFrame(self.root, width=290, height=self.height-5,text="Control")
        self._Frame_Control.place(anchor=E,relx=0.99,rely=0.5,x=2,y=0)
        
        self._Label_EPSILON = Label(self._Frame_Control, text="EPSILON: "+str(self.EPSILON))
        self._Label_EPSILON.place(anchor=CENTER,relx=0.5,rely=0.1,x=0,y=0)
    
        self._Label_ALPHA = Label(self._Frame_Control, text="ALPHA: "+str(self.ALPHA))
        self._Label_ALPHA.place(anchor=CENTER,relx=0.5,rely=0.3,x=0,y=0)
    
        self._Label_GAMMA = Label(self._Frame_Control, text="GAMMA: "+str(self.GAMMA))
        self._Label_GAMMA.place(anchor=CENTER,relx=0.5,rely=0.5,x=0,y=0)
        
        self._Scale_EPSILON = Scale(self._Frame_Control, from_=0, to=1, orient=HORIZONTAL,length=250,command=self.EPSILON_Change)
        self._Scale_EPSILON.set(self.EPSILON)
        self._Scale_EPSILON.place(anchor=CENTER,relx=0.5,rely=0.2,x=0,y=0)
        
        self._Scale_ALPHA = Scale(self._Frame_Control, from_=0, to=1, orient=HORIZONTAL,length=250,command=self.ALPHA_Change)
        self._Scale_ALPHA.set(self.ALPHA)
        self._Scale_ALPHA.place(anchor=CENTER,relx=0.5,rely=0.4,x=0,y=0)
        
        self._Scale_GAMMA = Scale(self._Frame_Control, from_=0, to=1, orient=HORIZONTAL,length=250,command=self.GAMMA_Change)
        self._Scale_GAMMA.set(self.GAMMA)
        self._Scale_GAMMA.place(anchor=CENTER,relx=0.5,rely=0.6,x=0,y=0)
        
        self._Button_Save = Button(self._Frame_Control, text="Save",width=25, command=self.saveDat)
        self._Button_Save.place(anchor=CENTER,relx=0.5,rely=0.8,x=0,y=0)
        
        self.root.bind("<KeyPress>", self.keyPress)
        self.root.bind("<KeyRelease>", self.keyRelease)
        self.root.bind('<Destroy>', self._on_destroy)
        self.visionUpdate()
        self.root.after(10,self.actionMove)
        self.root.mainloop()
        
    def EPSILON_Change(self,event):
        self.EPSILON = round(self._Scale_EPSILON.get(),3)
        self._Label_EPSILON.config(text="EPSILON: "+str(self.EPSILON))
        
    def ALPHA_Change(self,event):
        self.ALPHA = round(self._Scale_ALPHA.get(),3)
        self._Label_ALPHA.config(text="ALPHA: "+str(self.ALPHA))
        
    def GAMMA_Change(self,event):
        self.GAMMA = round(self._Scale_GAMMA.get(),3)
        self._Label_GAMMA.config(text="GAMMA: "+str(self.GAMMA))
        
        
    def buildingQtable(self):
        self.QTable={}
        if os.path.exists('learning_data.dat'):
            with open('learning_data.dat','rb') as f:
                _dat = pickle.loads(f.read())
                self.EPSILON,self.ALPHA,self.GAMMA,self.QTable=_dat
    def saveDat(self,*event):
        with open('learning_data.dat','wb') as f:
            _dat = pickle.dumps([self.EPSILON,self.ALPHA,self.GAMMA,self.QTable])
            f.write(_dat)
    def GetRandom(self):
        random.seed()
        return random.random()
    def GetRandomChoice(self,_act):
        random.seed()
        return random.choice(_act)
    def stateExist(self,state):
        if state in self.QTable.keys():
            return True
        else:
            return False
    def createState(self,state):
        self.QTable[state]={'left':0,'stop':0,'right':0}
    
    def getValue(self,state,action):
        return self.QTable[state][action]
    
    def getMaxAction(self,state):
        if self.stateExist(state):
            _maxAction = max(self.QTable[state],key=self.QTable[state].get)
            return _maxAction
        else:
            raise Exception('state not exist')
        
        
    def getMaxValue(self,state):
        if self.stateExist(state):
            _maxValue = self.QTable[state][self.getMaxAction(state)]
            return _maxValue
        else:
            raise Exception('state not exist')
    
    def action(self,_act):
        if _act=='left':
            self._Bot_keyPress(1)
        elif _act=='right':
            self._Bot_keyPress(-1)
        elif _act=='stop':
            self._Bot_keyPress(0)
    def choiceAction(self,state):
        usefulActions = []
        for action in range(len(self.ACTIONS)-1):
            if self.checkwall(action):
                usefulActions.append(self.ACTIONS[action])
        if (self.GetRandom() > self.EPSILON) or (not self.stateExist(state)):  #非贪婪 or 或者这个 state 还没有探索过
            if not self.stateExist(state):
                self.createState(state)
            action_name = self.GetRandomChoice(usefulActions)
        else:
            if not self.stateExist(state):
                self.createState(state)
            action_name = self.getMaxAction(state)    # 贪婪模式
        return action_name
    def doAction(self,action):
        self._Bot_keyPress(self.action_code[action])
    
    def timeReward(self):
        _div=self.operatTime
        if _div==0:
            _div=1
        return 500/_div
    
    def feedback(self):
        _angle=self._Bot_See()
        _timePunish = self.timeReward()
        if _angle==90:
            return 50 + _timePunish
        elif _angle==180 or _angle==0:
            return -20
        
        return round((math.pow(1/abs(_angle-90),0.25)-1.1)*10/3,2)
        
    def actionMove(self):
        S=self._Bot_See()               # 观察状态
        A=self.choiceAction(S)           # 选择行为
        q_predict = self.getValue(S,A)  # 预期值,当前选择的动作对应的分值
        self.doAction(A)                 # 执行动作
        S_=self._Bot_See()              # 观察执行动作后的状态
        q_actual = self.getMaxValue(S_)   #实际值,执行动作后的最大分值
        if self._keyCode == 37 and self.pos > self.boardwidth*0.5:
            self.pos -= 1
            self.angleCompensate(-1,0.25)   #位移时角度补偿
        elif self._keyCode == 39 and self.pos < self.width-self.boardwidth*0.5:
            self.pos += 1
            self.angleCompensate(1,0.25)    #位移时角度补偿
        self.angleChange()              #角度变化
        
        if S_!=90:
            self.operatTime+=1
        
        R = self.feedback()             # 获取奖励
        self.visionUpdate()             # 更新视觉
        
        if S_==0 or S_==180:
            self.failedTime+=1
        elif S_==90:
            self.successTime+=1
            self.operatTime-=1
        if self.failedTime>self.maxFailedTime:
            self.failedTime=0
            self.operatTime=0
            print('failed')
            self.restartGame()
        elif self.successTime>self.maxSuccessTime:
            self.successTime=0
            self.operatTime=0
            print('success')
            self.restartGame()
        q_target = R + self.GAMMA * q_actual
        # 更新QTable
        self.QTable[S][A] += self.ALPHA * (q_target - q_predict)  # 更新
        self.root.after(10,self.actionMove)
                


class botGame_WithoutUI(baseGame):
    def __init__(self,lowangle=False):
        super().__init__(lowangle)
        self.ACTIONS = ['left','stop','right'] #可用的动作
        self.action_code = {"left":-1,"stop":0,"right":1}
        self.EPSILON = 0.9 #贪婪度
        self.ALPHA = 0.1 #学习率
        self.GAMMA = 0.9 #奖励递减值
        self.save_Flag = True
        self.NiceTrainTime = 0
        self.operatTime = 0
        self.buildingQtable()
        
        self.averageOperatTime = 0
        
    def buildingQtable(self):
        self.QTable={}
        if os.path.exists('learning_data.dat'):
            with open('learning_data.dat','rb') as f:
                _dat = pickle.loads(f.read())
                self.EPSILON,self.ALPHA,self.GAMMA,self.QTable=_dat
    def saveDat(self,*event):
        with open('learning_data.dat','wb') as f:
            _dat = pickle.dumps([self.EPSILON,self.ALPHA,self.GAMMA,self.QTable])
            f.write(_dat)
        return
    def GetRandom(self):
        random.seed()
        return random.random()
    def GetRandomChoice(self,_act):
        random.seed()
        return random.choice(_act)
    def stateExist(self,state):
        if state in self.QTable.keys():
            return True
        else:
            return False
    def createState(self,state):
        self.QTable[state]={'left':0,'stop':0,'right':0}
    
    def getValue(self,state,action):
        return self.QTable[state][action]
    
    def getMaxAction(self,state):
        if self.stateExist(state):
            _maxAction = max(self.QTable[state],key=self.QTable[state].get)
            return _maxAction
        else:
            raise Exception('state not exist')
        
    def getMaxValue(self,state):
        if self.stateExist(state):
            _maxValue = self.QTable[state][self.getMaxAction(state)]
            return _maxValue
        else:
            raise Exception('state not exist')
    
    def action(self,_act):
        if _act=='left':
            self._Bot_keyPress(1)
        elif _act=='right':
            self._Bot_keyPress(-1)
        elif _act=='stop':
            self._Bot_keyPress(0)
    def choiceAction(self,state):
        usefulActions = []
        for action in range(len(self.ACTIONS)-1):
            if self.checkwall(action):
                usefulActions.append(self.ACTIONS[action])
        if (self.GetRandom() > self.EPSILON) or (not self.stateExist(state)):  #非贪婪 or 或者这个 state 还没有探索过
            if not self.stateExist(state):
                self.createState(state)
            action_name = self.GetRandomChoice(usefulActions)
        else:
            if not self.stateExist(state):
                self.createState(state)
            action_name = self.getMaxAction(state)    # 贪婪模式
        return action_name
    def doAction(self,action):
        self._Bot_keyPress(self.action_code[action])   
        
    def timeReward(self):
        _div=self.operatTime
        if _div==0:
            _div=1
        return 500/_div
    
    def feedback(self):
        _angle=self._Bot_See()
        _timePunish = self.timeReward()
        if _angle==90:
            return 50 + _timePunish
        elif _angle==180 or _angle==0:
            return -20
        
        return round((math.pow(1/abs(_angle-90),0.25)-1.1)*10/3,2)
        
    def start(self):
        print('Learning start...')
        _count=0
        startTime=time.time()
        while True:
            self.actionMove()
            if _count==500000:
                _count=0
                _useTime=time.time()-startTime
                print('500000 times Learning use: %.2f s'%(_useTime))
                print('average operat time: %.2f'%(self.averageOperatTime))
                print('Saving QTable...')
                self.saveDat()
                print('Save Finished')
                startTime=time.time()
            _count+=1
            if self.NiceTrainTime>=10:
                self.saveDat()
                print('Training Finished!')
                break
        
    def restartGame(self):
        self.pos= self.width/2
        self.initAngle()
        
    def actionMove(self):
        S=self._Bot_See()               # 观察状态
        A=self.choiceAction(S)           # 选择行为
        q_predict = self.getValue(S,A)  # 预期值,当前选择的动作对应的分值
        self.doAction(A)                 # 执行动作
        S_=self._Bot_See()              # 观察执行动作后的状态
        q_actual = self.getMaxValue(S_)   #实际值,执行动作后的最大分值
        if self._keyCode == 37 and self.pos > self.boardwidth*0.5:
            self.pos -= 1
            self.angleCompensate(-1,0.25)   #位移时角度补偿
        elif self._keyCode == 39 and self.pos < self.width-self.boardwidth*0.5:
            self.pos += 1
            self.angleCompensate(1,0.25)    #位移时角度补偿
        self.angleChange()                  #角度变化
        if S_!=90:
            self.operatTime+=1
        
        R = self.feedback()                 # 获取奖励
        
        if S_==0 or S_==180:
            self.failedTime+=1
        elif S_==90:
            self.successTime+=1
        if S_!=90 and self.successTime>0:
            self.successTime=0
        if self.failedTime>self.maxFailedTime:
            self.failedTime=0
            self.NiceTrainTime=0
            self.averageOperatTime=(self.averageOperatTime + self.operatTime)/2
            self.operatTime=0
            self.restartGame()
        elif self.successTime>self.maxSuccessTime:
            self.successTime=0
            self.NiceTrainTime+=1
            print('Success!')
            self.averageOperatTime=(self.averageOperatTime + self.operatTime)/2
            self.operatTime=0
            self.restartGame()
        q_target = R + self.GAMMA * q_actual
        # 更新QTable
        self.QTable[S][A] += self.ALPHA * (q_target - q_predict)

def buildingQtable():
    QTable={}
    if os.path.exists('learning_data.dat'):
        with open('learning_data.dat','rb') as f:
            _dat = pickle.loads(f.read())
            _,_,_,QTable=_dat
    for angle in QTable:
        print('angle=>'+str(angle)+' Left:'+str(QTable[angle]['left'])+' Stop:'+str(QTable[angle]['stop'])+' Right:'+str(QTable[angle]['right']))
            

if __name__ == "__main__":
    lowangle=False
    mode='GUI'  # GUI , Train , Manual , ShowQTable
    _help=False
    args = sys.argv[1:]
    for arg in args:
        if arg[:2]!='--':
            print('参数错误,请使用 --help 查看帮助')
            exit()
        if arg[2:]=='lowangle':
            lowangle=True
        if arg[2:7]=='mode-':
            if arg[7:].lower() in ['gui','train','manual']:
                mode=arg[7:]
            else:
                print('参数错误,请使用 --help 查看帮助')
                exit()
        if arg[2:]=='help':
            _help=True
            print('args:')
            print('--lowangle: 低角度模式,默认为False,随机角度为1-45°或者135-179°')
            print('--mode-GUI: GUI模式,默认为GUI模式')
            print('--mode-Train: 训练模式,无GUI,用于快速训练')
            print('--mode-Manual: 手动模式,不进行训练,用于手动控制游玩,左右方向键控制板子移动')
            print('--mode-ShowQTable: 显示QTable,用于查看QTable')
    
    if not _help:
        if mode.lower()=='train':
            Game=botGame_WithoutUI(lowangle).start()
        elif mode.lower()=='manual':
            Game=baseGame(lowangle).start()
        elif mode.lower()=='showqtable':
            buildingQtable()
        else:
            Game=botGame(lowangle).start()
