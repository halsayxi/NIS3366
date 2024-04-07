from lark import Visitor, Tree
import z3
from PyQt5.QtWidgets import QTextBrowser

class BitvecTypeChecker(Visitor):
    '''类型检查器，涉及int和float；Visitor为lark遍历结点的类'''
    def __init__(self, int_bit_num: int, float_type, output: QTextBrowser):
        '''int_bit_num设置int类型比特数，float_type设置浮点类型'''
        super().__init__()
        self.symbol_dict = {}
        self.error=False
        self.bit_num=int_bit_num
        self.float_type=float_type
        self.output = output

    def name_list(self, tree: Tree):
        type = tree.children[0].data
        for var in tree.children[1:]:
            name=var.children[0].value
            if name in self.symbol_dict:
                self.output.append("变量"+str(name)+"重复声明")
                self.error=True
            else:
                n = len(var.children)-1
                if n==0 and (type=="int" or type=="unsigned_int"):
                    self.symbol_dict[var.children[0].value]=[type, n, z3.BitVec(var.children[0].value, self.bit_num)]
                elif (type=="int" or type=="unsigned_int"):
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Array(var.children[0].value, z3.BitVecSort(self.bit_num), z3.BitVecSort(self.bit_num))]
                elif n==0 and type=="float":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.FP(var.children[0].value, self.float_type)]
                elif type=="float":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Array(var.children[0].value, z3.BitVecSort(self.bit_num), self.float_type)]

    def number_int(self, tree: Tree):
        tree.type_specifier="int"

    def number_float(self, tree: Tree):
        tree.type_specifier="float"

    def neg(self, tree: Tree):
        tree.type_specifier=tree.children[0].type_specifier

    def cast(self, tree: Tree):
        if tree.children[0].data!="float" or tree.children[1].type_specifier=="float":
            self.output.append("float无法转换为其他类型")
            self.error=True
            tree.type_specifier="float"
        else :
            tree.type_specifier=tree.children[0].data

    def plus(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        elif tree.children[0].type_specifier!="float" and tree.children[1].type_specifier!="float":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="float"

    def minus(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        elif tree.children[0].type_specifier!="float" and tree.children[1].type_specifier!="float":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="float"

    def multi(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        elif tree.children[0].type_specifier!="float" and tree.children[1].type_specifier!="float":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="float"

    def divide(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        elif tree.children[0].type_specifier!="float" and tree.children[1].type_specifier!="float":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="float"

    def mod(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        elif tree.children[0].type_specifier!="float" and tree.children[1].type_specifier!="float":
            tree.type_specifier="unsigned_int"
        else:
            self.output.append("%仅能用于整数")
            self.error=True
            tree.type_specifier="int"

    def bit_not(self, tree: Tree):
        if tree.children[0].type_specifier=="float":
            self.output.append("~仅适用于int型")
            self.error=True
            tree.type_specifier="int"
        else:
            tree.type_specifier=tree.children[0].type_specifier
    
    def bit_and(self, tree: Tree):
        if tree.children[0].type_specifier=="float" or tree.children[1].type_specifier=="float":
            self.output.append("&表达式两边需要均为int型")
            self.error=True
            tree.type_specifier="int"
        elif tree.children[0].type_specifier=="unsigned_int" or tree.children[1].type_specifier=="unsigned_int":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="int"

    def bit_xor(self, tree: Tree):
        if tree.children[0].type_specifier=="float" or tree.children[1].type_specifier=="float":
            self.output.append("^表达式两边需要均为int型")
            self.error=True
            tree.type_specifier="int"
        elif tree.children[0].type_specifier=="unsigned_int" or tree.children[1].type_specifier=="unsigned_int":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="int"
    
    def bit_or(self, tree: Tree):
        if tree.children[0].type_specifier=="float" or tree.children[1].type_specifier=="float":
            self.output.append("|表达式两边需要均为int型")
            self.error=True
            tree.type_specifier="int"
        elif tree.children[0].type_specifier=="unsigned_int" or tree.children[1].type_specifier=="unsigned_int":
            tree.type_specifier="unsigned_int"
        else:
            tree.type_specifier="int"

    def left_shift(self, tree: Tree):
        if tree.children[0].type_specifier=="float" or tree.children[1].type_specifier=="float":
            self.output.append("<<表达式两边需要均为int型")
            self.error=True
            tree.type_specifier="int"
        else :
            tree.type_specifier=tree.children[0].type_specifier
    
    def right_shift(self, tree: Tree):
        if tree.children[0].type_specifier=="float" or tree.children[1].type_specifier=="float":
            self.output.append(">>表达式两边需要均为int型")
            self.error=True
            tree.type_specifier="int"
        else :
            tree.type_specifier=tree.children[0].type_specifier
    
    def var_use(self, tree: Tree):
        for exp in tree.children[1:]:
            if exp.type_specifier!="int" and exp.type_specifier!="unsigned_int":
                self.output.append(tree.children[0].value, "数组下标不为整数")
                self.error=True   
        if tree.children[0].value not in self.symbol_dict:
            self.output.append(tree.children[0].value, "使用前未声明")
            self.error=True    
            tree.type_specifier="int"
        else:
            tree.type_specifier=self.symbol_dict[tree.children[0].value][0]
            if len(tree.children[1:])!=self.symbol_dict[tree.children[0].value][1]:
                self.output.append(tree.children[0].value, "使用时下标数量与声明不符")
                self.error=True
             
    def assignment(self, tree: Tree):
        e1, e2 = tree.children
        if (e1.type_specifier=="int" or e1.type_specifier=="unsigned_int") and e2.type_specifier=="float":
            self.output.append(e1.children[0].value, "赋值时左右类型不匹配")
            self.error = True

    def exits(self, tree: Tree):
        for name in tree.children[0:-1]:
            if name.value not in self.symbol_dict:
                self.output.append("约束变量", name.value, "未定义")
                self.error = True

    def forall(self, tree: Tree):
        for name in tree.children[0:-1]:
            if name.value not in self.symbol_dict:
                self.output.append("约束变量", name.value, "未定义")
                self.error = True

