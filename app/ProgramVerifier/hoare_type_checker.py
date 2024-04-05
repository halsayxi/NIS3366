import z3
from lark import Visitor, Tree
from PyQt5.QtWidgets import QTextBrowser

class TypeChecker(Visitor):
    '''类型检查器，涉及int和float；Visitor为lark遍历结点的类'''
    def __init__(self, output: QTextBrowser):
        super().__init__()
        self.symbol_dict = {}
        self.error=False
        self.output = output
        self.output.clear()

    def name_list(self, tree: Tree):
        type = tree.children[0].data
        for var in tree.children[1:]:
            name=var.children[0].value
            if name in self.symbol_dict:
                self.output.append("变量"+str(name)+"重复声明")
                self.error=True
            else:
                n = len(var.children)-1
                if n==0 and type=="int":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Int(var.children[0].value)]
                elif type=="int":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Array(var.children[0].value, z3.IntSort(), z3.IntSort())]
                elif n==0 and type=="float":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Real(var.children[0].value)]
                elif type=="float":
                    self.symbol_dict[var.children[0].value]=[type, n, z3.Array(var.children[0].value, z3.IntSort(), z3.RealSort())]

    def number_int(self, tree: Tree):
        tree.type_specifier="int"

    def number_float(self, tree: Tree):
        tree.type_specifier="float"

    def neg(self, tree: Tree):
        tree.type_specifier=tree.children[0].type_specifier

    def plus(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        else:
            tree.type_specifier="float"

    def minus(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        else:
            tree.type_specifier="float"

    def multi(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        else:
            tree.type_specifier="float"

    def divide(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        else:
            tree.type_specifier="float"

    def mod(self, tree: Tree):
        if tree.children[0].type_specifier=="int" and tree.children[1].type_specifier=="int":
            tree.type_specifier="int"
        else:
            self.output.append("%仅能用于整数")
            self.error=True
            tree.type_specifier="int"

    def var_use(self, tree: Tree):
        for exp in tree.children[1:]:
            if exp.type_specifier!="int":
                self.output.append(tree.children[0].value+"数组下标不为整数")
                self.error=True   
        if tree.children[0].value not in self.symbol_dict:
            self.output.append(tree.children[0].value+"使用前未声明")
            self.error=True    
            tree.type_specifier="int"
        else:
            tree.type_specifier=self.symbol_dict[tree.children[0].value][0]
            if len(tree.children[1:])!=self.symbol_dict[tree.children[0].value][1]:
                self.output.append(tree.children[0].value+"使用时下标数量与声明不符")
                self.error=True
             
    def assignment(self, tree: Tree):
        e1, e2 = tree.children
        if e1.type_specifier=="int" and e2.type_specifier=="float":
            self.output.append(e1.children[0].value+"赋值时左右类型不匹配")
            self.error = True

    def exits(self, tree: Tree):
        for name in tree.children[0:-1]:
            if name.value not in self.symbol_dict:
                self.output.append("约束变量"+str(name.value)+"未定义")
                self.error = True

    def forall(self, tree: Tree):
        for name in tree.children[0:-1]:
            if name.value not in self.symbol_dict:
                self.output.append("约束变量"+str(name.value)+"未定义")
                self.error = True
        