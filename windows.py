import sys
import os
import win32ui
import pickle
from collections import OrderedDict
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QApplication
from PyQt5.QtGui import QFont   
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QAction, qApp
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets import QFileDialog

class Book(object):
    def __init__(self,title,author,idx):
        self.title = title
        self.nation, self.author = author
        self.readtime = []
        self.highcells = []
        self.notecells = []
        self.othercells = []
        self.cellnum = 0
        self.idx = idx
        self.tag = []

    def add_cell(self,cell):
        if cell.booktitle == self.title:
            if cell.celltype == 0:
                self.highcells.append(cell)
                cell.idx_cell = len(self.highcells)
            elif cell.celltype == 1:
                self.notecells.append(cell)
                cell.idx_cell = len(self.notecells)
            else:
                self.othercells.append(cell)
                cell.idx_cell = len(self.othercells)
             # 1,2,...
            self.cellnum += 1
            cell.idx_book = self.idx
            return True
        else:
            return False

    def ini_time(self):
        if self.highcells is not None:
            self.readtime = self.highcells[0].time[0:2]
        elif self.notecells is not None:
            self.readtime = self.notecells[0].time[0:2]
        elif self.othercells is not None:
            self.readtime = self.othercells[0].time[0:2]
        else:
            self.readtime = None
        
    def add_tag(self,tag):
        if isinstance(list,tag):
            self.tag.extend(tag)
        elif isinstance(str,tag):
            self.tag.append(tag)
        else:
            self.tag.append('Unknown tag error')
    
    def info(self):
        tag = ','.join(self.tag)
        print("Book %3d:《%15s》- %6s - Tag:%s - Has %d Notes and Highlights"%(self.idx, self.title,self.author, tag , self.cellnum))

    def output_md(self,mode='book',path = None):
        self.ini_time()
        t = self.readtime
        if mode == 'book':
            filename = str(t[0])+'-'+str(t[1])+'-'+self.title + '-' + self.author + '.md'
            folder = self.mk_time_folder(t[0],t[1],path)
        elif mode == 'author':
            filename = self.author + '.md'
            folder = self.mk_nation_folder(self.nation,path)
        elif mode == 'all':
            filename = 'AllBooks.md'
            folder = path
        else:
            print('mode error')
        filename = os.path.join(folder,filename)
        with open(filename,'w',encoding='utf-8') as f:
            f.write('## '+self.title+'\n')
            f.write('[TOC]\n')
            readtime_f = str(t[0])+'-'+str(t[1])+'\n'
            f.write('Author : '+'['+self.nation+']'+self.author+'\n')
            f.write('Time : '+readtime_f+'\n') 
            f.write('Tags : '+str(self.tag)[1:-2]+'\n')
            f.write('Notes: Has %d Notes and Highlights'% self.cellnum+'\n')
            f.write('### HighLight \n')    
            for cell in self.highcells:
                cell.output_md(f)
            f.write('### Notes \n')
            for cell in self.notecells:
                cell.output_md(f)
            f.write('### Other \n')
            for cell in self.othercells:
                cell.output_md(f)
        f.close()

    def mk_time_folder(self,year,month,path=None):
        folder = str(year) + '-' + str(month)
        if path is None:
            path = os.getcwd()
        if folder not in os.listdir(path):
            os.mkdir(folder)
        folder_path = os.path.join(path,folder)
        return folder_path
    
    def mk_nation_folder(self,nation,path=None):
        search_dict = {
            "美国【美】[美](美)":'America',
            "[夏][商][周][秦][汉][唐][宋][元][明][清][当代][南唐]":'China',
            "[法]【法】法国":'French',
            "[德][奥]德国【德】":'Germany',
            "【英】[英]英国":'English',
            "[阿][阿根廷][西]":'Latin'
        }
        for i in search_dict.keys():
            if i.find(nation) != -1:
                folder = search_dict[i]
        if path is None:
            path = os.getcwd()
        if folder not in os.listdir(path):
            os.mkdir(folder)
        folder_path = os.path.join(path,folder)
        return folder_path
        
    
    def modify(self,info):
        for name in info.keys():
            setattr(self,name,info[name])
        print('Modify successfully!')

class Author(object):
    def __init__(self,author,nation):
        self.name = author
        self.nation = nation
        self.content = ""
        self.books = []

    def add_books(self,book):
        if self.name in book.author:
            info = {
                'author':self.name
            }
            book.modify(info)
            self.books.append(book.title)

class Cell(object):
    """A cell data structure"""
    def __init__(self,title,author,time,content,ctp,loc):
        self.booktitle = title
        self.nation, self.author = author
        self.time = time # year month day hour min sec
        self.content = content
        self.celltype = ctp # 0 is highlight 1 is notes 2 is bookmark 3 is clip
        self.loc = loc # [start,end,mode]
        self.idx_cell = 0 # index of cell in this book
        self.tag = []
    
    @classmethod
    def check_time(self,t):
        t_ = []
        for i in range(len(t)):
            if t[i]<10:
                t_.append('0'+str(t[i]))
            else:
                t_.append(str(t[i]))
        return t_

    def output_md(self,f):
        t = self.time
        t_ = self.check_time(t)
        f.write('%d. %d 年 %d 月 %d 日 %s:%s:%s \n'
                    % (self.idx_cell, t[0],t[1],t[2],
                    t_[3],t_[4],t_[5]))
        s = ['> ','- ',' ',' ']
        f.write(s[self.celltype]+self.content+'\n')
        f.write('&nbsp; \n')



class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.datapath = None
        self.booklist = None
        self.ignorelist = None

        # setting
        self.cell_lb = 20 # 最低显示条目
        self.model = 'author' # 输出md分类模式
        self.outputpath = os.getcwd() # 输出md位置
        
        
    def initUI(self):

        self.statusBar()
        
        # menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.impAct())
        fileMenu.addAction(self.exitAct())
        fileMenu = menubar.addMenu('&Perference')
        fileMenu.addAction(self.setAct())
        fileMenu = menubar.addMenu('&Help')
        fileMenu.addAction(self.helpAct())


        QToolTip.setFont(QFont('SansSerif', 14))
        self.setToolTip('This is a <b>QWidget</b> widget')

        #--------- items -----------------
        title = QLabel('Title')
        author = QLabel('Author')
        review = QLabel('Review')

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        #--------- Layout ----------------
        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid) 
        #--------- Button ----------------
        okButton = QPushButton('Confirm', self)
        okButton.setToolTip('This is a button')
        okButton.resize(okButton.sizeHint())
        okButton.move(50, 100)  

        cancelButton = QPushButton('Quit', self)
        # bind event
        cancelButton.clicked.connect(QCoreApplication.instance().quit)
        cancelButton.resize(cancelButton.sizeHint())
        cancelButton.move(50, 50)  

        importButton = QPushButton('Import', self)
        importButton.clicked.connect(self.importFile)
        importButton.resize(importButton.sizeHint())
        importButton.move(50, 100)  

        # --------- Layout -------------
        # hbox = QHBoxLayout()
        # hbox.addStretch(1)
        # hbox.addWidget(okButton)
        # hbox.addWidget(cancelButton)

        # vbox = QVBoxLayout()
        # vbox.addStretch(1)
        # vbox.addLayout(hbox)
        # self.setLayout(vbox)  

        self.setGeometry(1600, 960, 300, 220)
        self.resize(1600,960)
        self.center()
        self.setWindowTitle('Kindle Notes Tool')
        self.setWindowIcon(QIcon('web.png'))        
    
        self.show()

    # ----------- menu -------------
    def exitAct(self):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        return exitAct

    def setAct(self):
        setAct = QAction(QIcon('exit.png'), '&Set', self)        
        setAct.setShortcut('Ctrl+P')
        setAct.setStatusTip('Set perference')
        setAct.triggered.connect(self.setting)
        return setAct

    def setting(self):
        """设置对话框"""
        self.cell_lb = 20 # 最低显示条目
        self.model = 'author' # 输出md分类模式
        self.outputpath = os.getcwd() # 输出md位置
        pass

    def impAct(self):
        impAct = QAction(QIcon('exit.png'), '&Import', self)        
        impAct.setShortcut('Ctrl+I')
        impAct.setStatusTip('Import File')
        impAct.triggered.connect(self.importFile)
        return impAct

    def helpAct(self):
        helpAct = QAction(QIcon('exit.png'), '&Help Info', self)        
        helpAct.setShortcut('Ctrl+H')
        helpAct.setStatusTip('Get Help')
        helpAct.triggered.connect(self.displayhelp)
        return helpAct
    
    def displayhelp(self):
        text, ok = QInputDialog()
        
        if ok:
            self.le.setText(str(text))

    # ----------- parse txt ---------------
    def importFile(self):
        """导入cliptxt"""
        path = os.getcwd()
        # open path os.startfile(path)
        # open file selector
        # dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
        # dlg.SetOFNInitialDir(os.getcwd())  # 设置打开文件对话框中的初始显示目录
        # dlg.DoModal()

        # filename = dlg.GetPathName()  # 获取选择的文件名称
        filename = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        Bookdict, Booklist = self.parse(filename)
        self.display(Bookdict,Booklist)
    
    def parse(self,file):
        """解析"""
        
        celllist = []
        Bookdict = OrderedDict() # {title:idx}
        Booklist = []

        # get dir
        path = os.path.dirname(os.path.realpath(file))
        # get filename
        # os.path.basename(os.path.realpath(file))
        # file = os.path.join(path,'My Clippings.txt')
        def get_content(index,data):
            content = ""
            line = data[index]
            while "==========" not in line:
                content = content + line
                index += 1
                line = data[index]
            return content

        def get_loc(txt,a,mode):
            if 'Added' in txt:
                b = txt.find('|',a,len(txt)) - 1
            else:
                b = txt.find('|',a,len(txt)) - 4
                if '页' in txt:
                    b = b - 1 
                if '剪切' in txt:
                    b = b - 2
                if mode == 'page':
                    b = txt.find('页') - 1
            if '-' in txt[a:b]:
                loc_str = txt[a:b].split('-')
                loc = [int(i) for i in loc_str]
            else:
                loc = [int(txt[a:b])] * 2
            if mode == 'page':
                loc.append(1)
            elif mode == 'loc':
                loc.append(0)
            return loc
        
        def get_time(txt):
            if '年' in txt:
                year = int(txt[0:4])
                month = int(txt[txt.find('年')+1:txt.find('月')])
                day = int(txt[txt.find('月')+1:txt.find('日')])
                time = [year,month,day]
                time_ = txt[txt.find('午')+1:-1].split(':')
                time.extend([int(i) for i in time_])
            elif ',' in txt:
                tmp = txt[txt.find(',')+2:-2].split(" ")
                mlist = ['January','February','March','April','May','June','July','August','September','October','November','December']
                day, month, year = int(tmp[0]),mlist.index(tmp[1])+1,int(tmp[2])
                time = [year,month,day]
                time_ = tmp[3].split(':')
                time.extend([int(i) for i in time_])
            else:
                print(txt)
            return time

        def get_info(txt):
            if 'Highlight' in txt or '标注' in txt:
                celltype = 0
            elif 'Note' in txt or '笔记' in txt:
                celltype = 1
            elif 'Bookmark' in txt or '书签' in txt:
                celltype = 2
            elif 'Clip' in txt or '剪切' in txt:
                celltype = 3
            else:
                print(txt)
                print('cell type error')
            
            if 'Added' in txt: # english
                time = get_time(txt.split('|')[-1][10:])
                if 'Article' in txt:
                    a =  txt.find('Location') + 9
                    loc = get_loc(txt,a,'loc')
                elif 'location' in txt: # if exist loc, it priorize
                    a =  txt.find('location') + 9
                    loc = get_loc(txt,a,'loc')
                elif 'page' in txt: # if don't exist loc , use page
                    a = txt.find('page') + 5  
                    loc = get_loc(txt,a,'page')
            elif '添加于' in txt:
                time = get_time(txt.split('|')[1][5:])
                if '位置' in txt:
                    a = txt.find('#') + 1
                    loc = get_loc(txt,a,'loc')
                elif '页' in txt:
                    a = txt.find('第') + 1
                    loc = get_loc(txt,a,'page')
                else:
                    print(txt)
            else:
                print(txt)
            return celltype,loc,time
        
        def get_title(txt):
            a = txt.rfind('(')
            if a == -1:
                title, author = "Unknown","Unknown"
            else:
                title = txt[:a-1]
                author = txt[a+1:-2]
            if '[' in author:
                i = author.find(']')
                nation = author[1:i]
                author = author[i+1:]
            elif '【' in author:
                i = author.find('】')
                nation = author[1:i]
                author = author[i+1:]
            else:
                nation = "Unknown"
            return title, (nation,author) 
        
        with open(file,'r',encoding='UTF-8') as f:
            data = f.readlines()
            for index, line in enumerate(data):
                if "==========" in line:
                    if index+4 <= len(data):
                        title,author= get_title(data[index+1])
                        celltype, loc,time = get_info(data[index+2])
                        content = get_content(index+4,data)
                        newcell = Cell(title,author,time,content,celltype,loc)
                        if title not in Bookdict.keys():
                            newbook = Book(title,author,len(Bookdict))
                            Bookdict[newbook.title] = newbook.idx
                            Booklist.append(newbook)
                        ind = Bookdict[title]
                        Booklist[ind].add_cell(newcell)
        
        self.datapath = os.path.join(path,'data')
        with open(os.path.join(self.datapath,'Book.pickle'),'wb') as f:
            pickle.dump(Booklist,f)
        with open(os.path.join(self.datapath,'Book_index.pickle'),'wb') as f:
            pickle.dump(Bookdict,f)

        return  Bookdict, Booklist

    def load(self):
        """加载到self.booklist"""
        with open(os.path.join(self.datapath,'Book.pickle'),'rb') as f:
            self.booklist = pickle.load(f)
            self.ignore()

    def ignore(self):
        for book in self.booklist:
            if book.title in self.ignorelist:
                self.booklist.remove(book)
            if book.author in self.ignorelist:
                self.booklist.remove(book)

    def output_md(self):
        """导出到md.  
        model: book, author and all"""
        for i in range(len(self.Booklist)):
            book = self.Booklist[i]
            if book.cellnum > self.cell_lb:
                book.output_md(self.outputpath,self.model)

    # ---------util----------------
    def center(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        """点关闭时的窗口提示"""
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()  

    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
