#７並べ

#ライブラリのインポート
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import random

#人数の入力
n=int(input("人数を入力してください:"))

#変数の設定
card_list_0=[]
field_card_list=[7,107,207,307]
pass_list=[0]*n
xy_list=[]
ax_list=[]
btn_list=[]
txt_list=[]
pause_list=[False]*n
pause_list[0]=True

#randomを用いたカードのシャッフル
for i in range(4):
    card_list_0.extend([j+100*i for j in range(1,14) if j!=7])
random.shuffle(card_list_0)

#リストを人数分で等分割して手札の用意
card_list=[card_list_0[i:i+48//n] for i in range(0,48,48//n)]

#表示画面の準備
fig=plt.figure(facecolor='brown')
ax=fig.add_axes([0.1,0.3,0.8,0.69])

#ボタンを配置するためのaxesを追加
if (n==3)or(n==4):      #人数でボタン配置を変更
    w=0.99/(48//n)
    for t in range(n):
        for i in range(48//n):
            card_ax=fig.add_axes([0.01+w*i,0.08*(n-1-t),w*0.9,0.07])
            ax_list.append(card_ax)
    pass_ax=fig.add_axes([0.91,0.40,0.08,0.1])
if (n==6)or(n==8):
    w=0.99/(48//n)/2.2
    for t in range(n//2):
        for i in range(48//n):
            card_ax=fig.add_axes([0.01+w*i,0.08*(n//2-1-t),w*0.9,0.07])
            ax_list.append(card_ax)
    for t in range(n//2):
        for i in range(48//n):
            card_ax=fig.add_axes([0.55+w*i,0.08*(n//2-1-t),w*0.9,0.07])
            ax_list.append(card_ax)
    pass_ax=fig.add_axes([0.46,0.01,0.08,0.1])

#axesの調整と７のトランプを並べる関数
def show_board():
    ax.set_facecolor('lightgreen')
    ax.set_xlim(0,13)
    ax.set_ylim(0,4)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    for i in range(4):
        show_card(6,i)    

#画面上にトランプをプロットする関数
def show_card(x,y):
    card=patches.Rectangle(xy=(x+0.1,y+0.1),width=0.8,height=0.8,fc='w',ec='k') #カードはpatch
    ax.add_patch(card)
    if y==0:                                                #模様はmarker
        ax.plot(x+0.50,y+0.20,marker='^',ms=5,color='k')
        ax.plot(x+0.50,y+0.35,marker='o',ms=7,color='k')
        ax.plot(x+0.65,y+0.25,marker='o',ms=7,color='k')
        ax.plot(x+0.35,y+0.25,marker='o',ms=7,color='k')
    elif y==1:
        ax.plot(x+0.50,y+0.20,marker='v',ms=10,color='r')
        ax.plot(x+0.59,y+0.30,marker='o',ms=4.9,color='r')
        ax.plot(x+0.41,y+0.30,marker='o',ms=4.9,color='r')
    elif y==2:
        ax.plot(x+0.50,y+0.25,marker='d',ms=10,color='r')
    else:
        ax.plot(x+0.50,y+0.30,marker='^',ms=10,color='k')
        ax.plot(x+0.50,y+0.20,marker='^',ms=5,color='k')
    ax.text(x+0.50,y+0.75,str(x+1),color='k')               #数字はtext
    plt.draw()

#リストの数値からトランプのデータを読み出す関数
def return_xy(d):
    xy=[]
    for p in range(48//n):
        if 1<=d[p]<=13:
            x,y=d[p]-1,3
            card_type='S'
        elif 101<=d[p]<=113:
            x,y=d[p]-101,2
            card_type='D'
        elif 201<=d[p]<=213:
            x,y=d[p]-201,1
            card_type='H'
        else:
            x,y=d[p]-301,0
            card_type='C'
        xy.append([x,y,card_type])
    return xy

#トランプのデータを読み出してリスト化
for k in range(n):
    d=card_list[k]
    xy=return_xy(d)
    xy_list.append(xy)

#コールバック関数を作成するクラス
class Func_list:
    def __init__(self,x,y,card_type,i,q,txt_list,btn_list):
        self.x,self.y,self.card_type,self.i,self.q=x,y,card_type,i,q
        self.txt_list,self.btn_list=txt_list,btn_list
        self.data=self.x+1+(3-self.y)*100
        
    #コールバック関数はメソッドとして定義
    def click_button(self,event):
        if self.i==pause_list.index(True):      #押したボタンが自分のものかどうか
            if self.x+1<7:                      #7を境にして条件分岐
                d=self.data+1
                self.onclick(d)    
            if self.x+1>7:
                d=self.data-1
                self.onclick(d)
            self.win()
        else:                                   #他人の手札は出せない
            print("This isn't yours")

    def onclick(self,d):
        global pause_list
        if d in field_card_list:                #場札と隣り合っているか
                show_card(self.x,self.y)
                xy_list[self.i].remove([self.x,self.y,self.card_type])  #手札の情報を更新
                field_card_list.append(self.data)                       #場札の情報を更新
                pause_list[self.i%n]^=True
                pause_list[(self.i+1)%n]^=True
                for r in range(48//n):          #自分の手札を非表示にして次のプレーヤーの手札を表示する
                    self.txt_list[r+(self.i%n)*(48//n)].set_visible(pause_list[self.i%n])
                    self.txt_list[r+((self.i+1)%n)*(48//n)].set_visible(pause_list[(self.i+1)%n])
                self.btn_list[self.q+self.i*(48//n)].disconnect_events()    #一度押したボタンは紐付けが解除
        else:
            print('You cannot select')
    
    def win(self):
        if not xy_list[self.i]:         #手札がなくなったら勝利
            print("player"+str(self.i+1)+""+"win!")
        if xy_list.count([])==n-1:      #手札の残っている人が残り一人になったら終了
            print("Game set")

#手札のボタンを生成する関数        
def card_button(xy_list,n,ax_list,btn_list,txt_list):
    for e in range(n):
        for i in range(48//n):
            xy=xy_list[e]
            x,card_type=xy[i][0],xy[i][2]
            card_name=card_type+'\n'+str(x+1)
            txt=ax_list[i+e*(48//n)].text(0.5,0.5,card_name,horizontalalignment='center',verticalalignment='center')
            txt_list.append(txt)
            btn_list.append(Button(ax_list[i+e*(48//n)],""))

#パスのためのボタンのコールバック関数
def click_pass(event):
    idx=pause_list.index(True)  #リストのインデックスからターンを参照
    pass_list[idx]+=1           #各プレーヤーのパス回数を記録
    pause_list[idx%n]^=True
    pause_list[(idx+1)%n]^=True
    for r in range(48//n):      
        txt_list[r+(idx%n)*(48//n)].set_visible(pause_list[idx%n])
        txt_list[r+((idx+1)%n)*(48//n)].set_visible(pause_list[(idx+1)%n])
    if pass_list[idx]>3:        #パスは3回まで
        print("player"+str(idx+1)+""+'lose')
    if xy_list.count([])==n-1:
        print("Game set")

#本編
show_board()                                        
card_button(xy_list,n,ax_list,btn_list,txt_list)    #ボタンを生成
for s in range(n):                                  #最初のプレーヤー以外の場札を非表示
    for h in range(48//n):
        txt_list[h+s*(48//n)].set_visible(pause_list[s])
fc_list=[]
for i in range(n):
    for q in range(48//n):
        xy=xy_list[i]
        x,y,card_type=xy[q][0],xy[q][1],xy[q][2]
        fc_list.append(Func_list(x,y,card_type,i,q,txt_list,btn_list))  #インスタンスのリストを作成
for e in range(48): 
    btn_list[e].on_clicked(fc_list[e].click_button) #各インスタンスから関数を呼び出しボタンに紐付ける
pass_btn=Button(pass_ax,'Pass')                                             #パスボタンを追加
pass_btn.on_clicked(click_pass)
plt.show()                                                                  #画面を表示