# coding:utf-8
from PyQt5.QtWidgets import QGridLayout, QStackedWidget, QWidget, QFileDialog
from qfluentwidgets import (TextEdit, PushButton, Dialog, SpinBox, BodyLabel, VBoxLayout, SegmentedWidget)
from ..common.translator import Translator
from .gallery_interface import GalleryInterface
from ..ProgramVerifier.hoare_prover import HoareProver
from ..ProgramVerifier.bitvec_hoare_prover import BitvecHoareProver

class UnboundedVerifier(QWidget):
    def __init__(self):
        super().__init__()
        self.filename = None
        self.layout = QGridLayout(self)

        detail_button = PushButton("功能介绍")
        detail_button.clicked.connect(self.FuncIntro)
        self.layout.addWidget(detail_button, 1,0,1,1)

        detail_button = PushButton("语法")
        detail_button.clicked.connect(self.show_gramma)
        self.layout.addWidget(detail_button, 3,0,1,1)

        verify_button = PushButton('验证')
        verify_button.clicked.connect(self.verify)
        self.layout.addWidget(verify_button, 5,0,1,1)

        self.layout.addWidget(BodyLabel("输出:"),7,0,1,1)
        self.output = TextEdit(self)
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output,9,0,10,6)

        self.clear_button = PushButton("清空输出")
        self.clear_button.clicked.connect(self.clear_output)
        self.layout.addWidget(self.clear_button, 19,0,1,1)

        self.segement = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.file_button = PushButton("上传文件")
        self.file_button.clicked.connect(self.upload_file)
        self.code_input = TextEdit(self)

        self.addSubInterface(self.file_button, 'file', '上传文件')
        self.addSubInterface(self.code_input, 'code', '输入代码')

        # 连接信号并初始化当前标签页
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.code_input)
        self.segement.setCurrentItem(self.code_input.objectName())

        self.layout.addWidget(self.segement, 0,2,1,4)
        self.layout.addWidget(self.stackedWidget,1,2,8,4)

    def addSubInterface(self, widget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        # 使用全局唯一的 objectName 作为路由键
        self.segement.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.segement.setCurrentItem(widget.objectName())

    def upload_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择文件')
        if filename:
            self.filename = filename
            self.file_button.setText(filename)

    def verify(self):
        prover=HoareProver(self.output)
        if self.segement._currentRouteKey == "code":
            code = self.code_input.toPlainText()
        else:
            if self.filename==None:
                w = Dialog("Warning", "请先选择文件！", self.window())
                w.setContentCopyable(True)
                w.cancelButton.hide()
                w.buttonLayout.insertStretch(1)
                w.exec()
                return
            with open(self.filename) as f:
                code=f.read()
        try:
            prover.run(code)
        except:
            w = Dialog("Warning", "程序不符合语法！", self.window())
            w.setContentCopyable(True)
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec()

    def clear_output(self):
        self.output.clear()

    def FuncIntro(self):
        title = "功能介绍"
        content = '''我们设计了两类程序验证器来满足您的需求。 \n 
            无界整数与实数验证器：支持无界整数与任意精度实数，偏向于数学语境；\n 
            有界整数与浮点数验证器：支持有符号整数，无符号整数，浮点数三种数据类型，考虑溢出与精度等问题，适用于计算机语境。'''
        w = Dialog(title, content, self.window())
        w.setContentCopyable(True)
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec()

    def show_gramma(self):
        title = "语法"
        content = """program := var_dec_list "{" z3_exp "}" stmt_list "{" z3_exp "}"      
    var_dec_list :=  (var_dec)*                        
    var_dec := specifier var_decl ("," var_decl)* ";" 
    var_decl := CNAME ("[" INT "]")?
    specifier := "int" | "float" 
    var_use := CNAME ("[" exp "]")? 
    stmt_list := (stmt)* 
    stmt := "skip" ";" | var_use "=" exp ";" | ";" | "if" "(" bool_exp ")" "{" stmt_list "}" "else" "{" stmt_list "}" | "if" "(" bool_exp ")" "{" stmt_list "}" | "{" "inv" ":" bool_exp "}" "while" "(" bool_exp ")" "{" stmt_list "}" 
    z3_exp := z3_imply | z3_exp "<=>" z3_imply
    z3_imply := z3_or | z3_imply "->" z3_or 
    z3_or := z3_and | z3_or "or" z3_and                             
    z3_and := z3_not | z3_and "and" z3_not | z3_and ";" z3_not                           
    z3_not := z3_atom | "not" z3_atom    
    z3_atom := "(" z3_exp ")" | bool_exp | "forall"  CNAME ("," CNAME)*  "(" z3_exp ")" | "exists"  CNAME ("," CNAME)*  "(" z3_exp ")"                       
    bool_exp := and_term | bool_exp "||" and_term  
    and_term := not_term | and_term "&&" not_term  
    not_term := bool_atom |"!" bool_atom     
    bool_atom := "(" bool_exp ")" | "true" | "false" | exp "<=" exp | exp ">=" exp | exp "==" exp | exp "!=" exp | exp "<" exp | exp ">" exp  
    exp := product | exp "+" product | exp "-" product  
    product := atom | product "*" atom | product "/" atom | product "%" atom              
    atom := INT | FLOAT | "-" atom | var_use | "(" exp ")"  
    COMMENT := "/*" /(.|\\n|\\r)+/ "*/" |  "//" /(.)+/ NEWLINE"""
        w = Dialog(title, content, self.window())
        w.setContentCopyable(True)
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec()

class BoundedVerifier(QWidget):
    def __init__(self):
        super().__init__()
        self.filename = None
        self.layout = QGridLayout(self)

        self.int_size = SpinBox(self)
        self.int_size.setMinimum(1)
        self.int_size.setValue(16)
        self.exponent_size = SpinBox(self)
        self.exponent_size.setMinimum(2)
        self.exponent_size.setValue(8)
        self.significand_size = SpinBox(self)
        self.significand_size.setMinimum(3)
        self.significand_size.setValue(23)

        detail_button = PushButton("语法")
        detail_button.clicked.connect(self.show_gramma)
        self.layout.addWidget(detail_button, 0,0,1,1)

        self.layout.addWidget(BodyLabel("Int类型的长度"), 2,0,1,1)
        self.layout.addWidget(self.int_size,2,1,1,1)
        self.layout.addWidget(BodyLabel("Float类型的指数长度"),3,0,1,1)
        self.layout.addWidget(self.exponent_size,3,1,1,1)
        self.layout.addWidget(BodyLabel("Float类型的底数长度"),4,0,1,1)
        self.layout.addWidget(self.significand_size,4,1,1,1)

        verify_button = PushButton('验证')
        verify_button.clicked.connect(self.verify)
        self.layout.addWidget(verify_button,5,0,1,1)

        self.layout.addWidget(BodyLabel("输出:"),7,0,1,1)
        self.output = TextEdit(self)
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output,9,0,10,6)

        self.clear_button = PushButton("清空输出")
        self.clear_button.clicked.connect(self.clear_output)
        self.layout.addWidget(self.clear_button, 19,0,1,1)

        self.segement = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.file_button = PushButton("上传文件")
        self.file_button.clicked.connect(self.upload_file)
        self.code_input = TextEdit(self)

        self.addSubInterface(self.file_button, 'file', '上传文件')
        self.addSubInterface(self.code_input, 'code', '输入代码')

        # 连接信号并初始化当前标签页
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.code_input)
        self.segement.setCurrentItem(self.code_input.objectName())

        self.layout.addWidget(self.segement, 0,2,1,4)
        self.layout.addWidget(self.stackedWidget,1,2,8,4)

    def addSubInterface(self, widget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        # 使用全局唯一的 objectName 作为路由键
        self.segement.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.segement.setCurrentItem(widget.objectName())

    def upload_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择文件')
        if filename:
            self.filename = filename
            self.file_button.setText(filename)

    def verify(self):
        int_bit_num = self.int_size.value()
        exponent_length = self.exponent_size.value()
        significand_length = self.significand_size.value()
        prover = BitvecHoareProver(int_bit_num, exponent_length, significand_length, self.output)
        if self.segement._currentRouteKey == "code":
            code = self.code_input.toPlainText()
        else:
            if self.filename==None:
                w = Dialog("Warning", "请先选择文件！", self.window())
                w.setContentCopyable(True)
                w.cancelButton.hide()
                w.buttonLayout.insertStretch(1)
                w.exec()
                return
            with open(self.filename) as f:
                code=f.read()
        try:
            prover.run(code)
        except:
            w = Dialog("Warning", "程序不符合语法！", self.window())
            w.setContentCopyable(True)
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec()

    def clear_output(self):
        self.output.clear()

    def show_gramma(self):
        title = "语法"
        content = """program := var_dec_list "{" z3_exp "}" stmt_list "{" z3_exp "}"  
    var_dec_list :=  (var_dec)* 
    var_dec := specifier var_decl ("," var_decl)* ";" 
    var_decl := CNAME ("[" INT "]")? 
    specifier := "int" | "float" | "unsigned" "int"
    var_use := CNAME ("[" exp "]")? 
    stmt_list := (stmt)*
    stmt := "skip" ";" | var_use "=" exp ";"  | ";" | "if" "(" bool_exp ")" "{" stmt_list "}" "else" "{" stmt_list "}" | "if" "(" bool_exp ")" "{" stmt_list "}" | "{" "inv" ":" bool_exp "}" "while" "(" bool_exp ")" "{" stmt_list "}"  
    z3_exp := z3_imply | z3_exp "<=>" z3_imply
    z3_imply := z3_or | z3_imply "->" z3_or
    z3_or := z3_and | z3_or "or" z3_and   
    z3_and := z3_not | z3_and "and" z3_not | z3_and ";" z3_not
    z3_not := z3_atom | "not" z3_atom
    z3_atom := "(" z3_exp ")" | bool_exp | "forall"  CNAME ("," CNAME)*  "(" z3_exp ")"  | "exists"  CNAME ("," CNAME)*  "(" z3_exp ")"                  
    bool_exp := and_term | bool_exp "||" and_term
    and_term := not_term | and_term "&&" not_term 
    not_term := bool_atom |"!" bool_atom 
    bool_atom := "(" bool_exp ")" | "true" | "false" | exp "<=" exp | exp ">=" exp | exp "==" exp | exp "!=" exp | exp "<" exp | exp ">" exp 
    exp := bit_xor_term | exp "|" bit_xor_term 
    bit_xor_term := bit_and_term | bit_xor_term "^" bit_and_term  
    bit_and_term := shift_term | bit_and_term "&" shift_term 
    shift_term := add_term | shift_term "<<" exp  | shift_term ">>" exp  
    add_term := product | exp "+" product | exp "-" product  
    product := atom | product "*" atom | product "/" atom | product "%" atom 
    atom := INT | FLOAT | "-" atom | var_use | "(" exp ")" | "~" atom | specifier "(" exp ")" 
    COMMENT := "/*" /(.|\\n|\\r)+/ "*/"   |   "//" /(.)+/ NEWLINE"""
        w = Dialog(title, content, self.window())
        w.setContentCopyable(True)
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec()

class ChooseVerifier(QWidget):
    def __init__(self):
        super().__init__()
        self.segement = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = VBoxLayout(self)

        self.verifier1 = UnboundedVerifier()
        self.verifier2 = BoundedVerifier()

        # 添加标签页
        self.addSubInterface(self.verifier1, 'verifier1', '无界整数与实数')
        self.addSubInterface(self.verifier2, 'verifier2', '有界整数与浮点数')

        # 连接信号并初始化当前标签页
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.verifier1)
        self.segement.setCurrentItem(self.verifier1.objectName())

        self.vBoxLayout.addWidget(self.segement)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def addSubInterface(self, widget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        # 使用全局唯一的 objectName 作为路由键
        self.segement.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.segement.setCurrentItem(widget.objectName())

class VerifierInterface(GalleryInterface):
    """ Verifier interface """

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.verifier,
            subtitle='上传或输入符合语法规则的程序，我们将验证程序的正确性',
            parent=parent
        )
        self.setObjectName('verifierInterface')

        choose_verifier = ChooseVerifier()
        self.vBoxLayout.addWidget(choose_verifier)
