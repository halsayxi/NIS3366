import z3
from lark import Tree
from PyQt5.QtWidgets import QTextBrowser

from .bitvec_hoare_parser import bitvec_simple_parser
from .bitvec_hoare_type_checker import BitvecTypeChecker
    
from .hoare_prover import print_with_tab_prefix

class BitvecHoareProver():
    def __init__(self, int_bit_num: int, exponent_length: int, significand_length: int, output: QTextBrowser):
        '''
        int类型用z3.BitVec表示
        float类型用z3.FPSort表示
        int_bit_num设置int类型比特数，
        exponent_length设置浮点类型指数位长度，
        significand_length设置浮点类型底数位长度，
        '''
        self.hoare_parser = bitvec_simple_parser
        self.symbol_dict = {}
        # 符号表，含有类型、是否为数组、对应的z3求解器中符号等标注
        self.int_bit_num = int_bit_num
        self.float_type = z3.FPSort(exponent_length, significand_length)
        self.output = output
        self.output.clear()

    def int_to_float(self, vec):
        '''将有符号整型转化为浮点型，由于不存在bitvec到float的直接函数，通过int、real间接转换'''
        n=z3.BV2Int(vec, is_signed=True)
        real=z3.ToReal(n)
        return z3.fpRealToFP(z3.RNE(), real, self.float_type)
    
    def unsigned_int_to_float(self, vec):
        '''将无符号整型转化为浮点型，由于不存在bitvec到float的直接函数，通过int、real间接转换'''
        n=z3.BV2Int(vec, is_signed=False)
        real=z3.ToReal(n)
        return z3.fpRealToFP(z3.RNE(), real, self.float_type)
    
    def couple_to_float(self, e1, e2):
        '''将运算符两边的表达式均转换为浮点型'''
        if e1.type_specifier=="float":
            number1 = self.bool_exp_to_z3(e1)
        elif e1.type_specifier=="int":
            number1 = self.int_to_float(self.bool_exp_to_z3(e1))
        else:
            number1 = self.unsigned_int_to_float(self.bool_exp_to_z3(e1))

        if e2.type_specifier=="float":
            number2 = self.bool_exp_to_z3(e2)
        elif e1.type_specifier=="int":
            number2 = self.int_to_float(self.bool_exp_to_z3(e2))
        else:
            number2 = self.unsigned_int_to_float(self.bool_exp_to_z3(e2))

        return number1, number2

    def get_var_name_in_z3(self, var: Tree):
        '''将程序中的变量转化为对应的z3求解器中的变量'''
        if len(var.children)==1:
            return self.symbol_dict[var.children[0].value][-1]
        else:
            return self.symbol_dict[var.children[0].value][-1][self.bool_exp_to_z3(var.children[1])]
 
    def get_bounded_var(self, exp: Tree):
        '''获得一阶公式的约束变量对应的的符号'''
        var_list=[]
        for name in exp.children[0:-1]:
            var_list.append(self.symbol_dict[name.value][-1])
        return var_list 

    def z3_exp_to_z3(self, exp: Tree):
        '''将程序中的z3表达式转化为z3求解器中的公式'''
        if exp.data == "equiv":
            z1, z2 = exp.children
            return self.z3_exp_to_z3(z1)==self.z3_exp_to_z3(z2)
        
        elif exp.data == "imply":
            z1, z2 = exp.children
            return z3.Implies(self.z3_exp_to_z3(z1),self.z3_exp_to_z3(z2))
        
        elif exp.data == "z3_or": 
            z1, z2 = exp.children
            return z3.Or(self.z3_exp_to_z3(z1),self.z3_exp_to_z3(z2))
        
        elif exp.data == "z3_and":
            z1, z2 = exp.children
            return z3.And(self.z3_exp_to_z3(z1),self.z3_exp_to_z3(z2))
        
        elif exp.data == "z3_not":
            z1 = exp.children[0]
            return z3.Not(self.z3_exp_to_z3(z1))
        
        elif exp.data == "forall":
            z = exp.children[-1]
            return z3.ForAll(self.get_bounded_var(exp), self.z3_exp_to_z3(z))
        
        elif exp.data == "exists":
            z = exp.children[-1]
            return z3.Exists(self.get_bounded_var(exp), self.z3_exp_to_z3(z))
        else:
            return self.bool_exp_to_z3(exp)

    def bool_exp_to_z3(self, exp: Tree):
        '''将布尔表达式转化为z3求解器中的公式'''
        if exp.data == "le":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpLEQ
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpLEQ(n1, n2)
            elif e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) <= self.bool_exp_to_z3(e2)
            else:
                return z3.ULE(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            
        elif exp.data == "ge":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpGEQ
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpGEQ(n1, n2)
            elif e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) >= self.bool_exp_to_z3(e2)
            else:
                return z3.UGE(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号比较需要通过UGE
            #只要有一个表达式为无符号，则采用无符号比较
            
        elif exp.data == "eq":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpEQ
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpEQ(n1, n2)
            else:
                return self.bool_exp_to_z3(e1) == self.bool_exp_to_z3(e2)
        
        elif exp.data == "neq":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpNEQ
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpNEQ(n1, n2)
            else:
                return self.bool_exp_to_z3(e1) != self.bool_exp_to_z3(e2)
        
        elif exp.data == "lt":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpLT
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpLT(n1, n2)
            elif e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) < self.bool_exp_to_z3(e2)
            else:
                return z3.ULT(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号比较需要通过ULT
            #只要有一个表达式为无符号，则采用无符号比较
            
        elif exp.data == "gt":
            e1, e2 = exp.children
            #浮点类型比较需要通过fpGT
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpGT(n1, n2)
            elif e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) > self.bool_exp_to_z3(e2)
            else:
                return z3.UGT(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号比较需要通过UGT
            #只要有一个表达式为无符号，则采用无符号比较
            
        elif exp.data == "and":
            e1, e2 = exp.children
            return z3.And(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
        
        elif exp.data == "or":
            e1, e2 = exp.children
            return z3.Or(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
        
        elif exp.data == "not":
            e1 = exp.children[0]
            return z3.Not(self.bool_exp_to_z3(e1))
        
        elif exp.data == "plus":
            e1, e2 = exp.children
            #浮点类型运算需要通过fpADD
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpAdd(z3.RNE(), n1, n2)
            else:
                return self.bool_exp_to_z3(e1) + self.bool_exp_to_z3(e2)
        
        elif exp.data == "minus":
            e1, e2 = exp.children
            #浮点类型运算需要通过fpSub
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpSub(z3.RNE(), n1, n2)
            else:
                return self.bool_exp_to_z3(e1) - self.bool_exp_to_z3(e2)
        
        elif exp.data == "multi":
            e1, e2 = exp.children
            #浮点类型运算需要通过fpNul
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpMul(z3.RNE(), n1, n2)
            else:
                return self.bool_exp_to_z3(e1) * self.bool_exp_to_z3(e2)
        
        elif exp.data == "divide":
            e1, e2 = exp.children
            #浮点类型运算需要通过fpDiv
            #只要有一个表达式为浮点类型，其余表达式也提升为浮点型
            if e1.type_specifier=="float" or e2.type_specifier=="float":
                n1, n2 = self.couple_to_float(e1, e2)
                return z3.fpDiv(z3.RNE(), n1, n2)
            elif e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) / self.bool_exp_to_z3(e2)
            else:
                return z3.UDiv(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号运算需要通过UDiv
            #只要有一个表达式为无符号，则采用无符号运算
            
        elif exp.data == "mod":
            e1, e2 = exp.children
            if e1.type_specifier!="unsigned_int" and e2.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) % self.bool_exp_to_z3(e2)
            else:
                return z3.URem(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号运算需要通过URem
            #只要有一个表达式为无符号，则采用无符号运算
            
        elif exp.data == "bit_or":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) | self.bool_exp_to_z3(e2)
        
        elif exp.data == "bit_xor":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) ^ self.bool_exp_to_z3(e2)

        elif exp.data == "bit_and":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) & self.bool_exp_to_z3(e2)

        elif exp.data == "left_shift":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) << self.bool_exp_to_z3(e2)

        elif exp.data == "right_shift":
            e1, e2 = exp.children
            if e1.type_specifier!="unsigned_int":
                return self.bool_exp_to_z3(e1) >> self.bool_exp_to_z3(e2)
            #有符号采用算数右移
            else:
                return z3.LShR(self.bool_exp_to_z3(e1), self.bool_exp_to_z3(e2))
            #无符号采用逻辑右移

        elif exp.data == "bit_not":
            e1 = exp.children[0]
            return ~ self.bool_exp_to_z3(e1)

        elif exp.data == "cast":
            #类型转换
            e1, e2 = exp.children
            if e1.data=="float" and e2.type_specifier=="int":
                return self.int_to_float(self.bool_exp_to_z3(e2))
            elif e1.data=="float" and e2.type_specifier=="unsigned_int":
                return self.unsigned_int_to_float(self.bool_exp_to_z3(e2))
            else:
                return self.bool_exp_to_z3(e2)

        elif exp.data == "neg":
            e1 = exp.children[0]
            return 0-self.bool_exp_to_z3(e1)
        
        elif exp.data == "number_int":
            return z3.BitVecVal(exp.children[0], self.int_bit_num)
        
        elif exp.data == "number_float":
            return z3.FPVal(exp.children[0], self.float_type)
        
        elif exp.data == "true":
            return True
        
        elif exp.data == "false":
            return False
        
        elif exp.data == "var_use":
            return self.get_var_name_in_z3(exp)

    def get_var_name_str(self, var:Tree):
        '''获得赋值符号左端（可能为数组）的字符串表示形式'''
        if len(var.children)==1:
            var_name= var.children[0].value
        else:
            var_name= var.children[0].value + "["+  str(self.bool_exp_to_z3(var.children[1]))   + "]"
        return var_name

    def weakest_pre(self, code, flag, postcond, n):
        '''递归计算代码块的最弱前置条件'''
        if not flag:
        #flag==False表示while循环的循环不变式不满足要求，不必再继续验证
            return flag, postcond

        if code.data == "skip":
            return True, postcond
        
        elif code.data == "assignment":
            var, exp = code.children
            number = self.bool_exp_to_z3(exp)
            if exp.type_specifier=="int" and var.type_specifier=="float":
                number=self.int_to_float(number)
            elif exp.type_specifier=="unsigned_int" and var.type_specifier=="float":
                number=self.unsigned_int_to_float(number)
                
            wpre = z3.substitute(postcond, (self.get_var_name_in_z3(var), number))
            var_name=self.get_var_name_str(var)

            print_with_tab_prefix("当前语句：" + str(var_name) + " = " +str(number), n, self.output)
            print_with_tab_prefix("计算assignment语句的最弱前置条件\n" + str(wpre)+"\n", n, self.output)

            return True, wpre
        
        elif code.data == "if_else":
            guard, c1, c2 = code.children

            print_with_tab_prefix("计算if else语句的最弱前置条件", n, self.output)
            print_with_tab_prefix("计算条件成立时子语句的最弱前置条件", n, self.output)

            c1_flag, wpre_c1 = self.weakest_pre(c1, True, postcond, n+1)
            if c1_flag:
                print_with_tab_prefix("条件成立时子语句的最弱前置条件为\n" + str(wpre_c1), n, self.output)
                print_with_tab_prefix("计算条件不成立时子语句的最弱前置条件", n, self.output)

                c2_flag, wpre_c2 = self.weakest_pre(c2, True, postcond, n+1)
                if c2_flag:
                    guard=self.bool_exp_to_z3(guard)
                    wpre=z3.And(z3.Implies(guard, wpre_c1), z3.Implies(z3.Not(guard), wpre_c2))
                    
                    print_with_tab_prefix("条件不成立时子语句的最弱前置条件为\n" + str(wpre_c2), n, self.output)
                    print_with_tab_prefix("if_else语句最弱前置条件为\n" + str(wpre) +"\n", n, self.output)

                    return True, wpre
            return False, postcond
        
        elif code.data == "if":
            guard, c1 = code.children
            print_with_tab_prefix("计算if语句的最弱前置条件\n", n, self.output)
            print_with_tab_prefix("计算条件成立时子语句的最弱前置条件", n, self.output)

            c1_flag, wpre_c1 = self.weakest_pre(c1, True, postcond)
            if c1_flag:
                print_with_tab_prefix("条件成立时子语句的最弱前置条件为\n"+ str(wpre_c1), n, self.output)
                wpre_c2 = postcond
                guard=self.bool_exp_to_z3(guard)
                wpre=z3.And(z3.Implies(guard, wpre_c1), z3.Implies(z3.Not(guard), wpre_c2))

                print_with_tab_prefix("if语句最弱前置条件为\n"+ str(wpre) + "\n", n, self.output)

                return (True, wpre)
            else:
                return (False, postcond)
                 
        elif code.data == "seq":
            wpre = postcond
            stmt_flag = True
            for stmt in reversed(code.children):
                stmt_flag, wpre = self.weakest_pre(stmt, stmt_flag, wpre, n)
            return (stmt_flag, wpre)
        
        elif code.data == "while":
            inv, guard, c = code.children
            print_with_tab_prefix("计算while语句的最弱前置条件", n, self.output)
            inv = self.bool_exp_to_z3(inv)
            guard = self.bool_exp_to_z3(guard)
            c_flag, wpre_c = self.weakest_pre(c, True, inv, n+1)

            if c_flag:
                print_with_tab_prefix("while语句最弱前置条件为\n" + str(wpre_c), n, self.output)
                wpre = z3.And(z3.Implies(z3.And(guard, inv), wpre_c), z3.Implies(z3.And(z3.Not(guard), inv), postcond))
                if self.prove_formula(wpre):
                    print_with_tab_prefix("循环不变式" + str(inv) + "蕴含后续条件", n, self.output)
                    print_with_tab_prefix("返回循环不变式\n", n, self.output)
                    return True, inv
            print_with_tab_prefix("循环不变式" + str(inv) + "不蕴含后续条件，请尝试新的循环不变式，或检查程序的正确性\n", n, self.output)    
            return False, postcond

    def prove_formula(self, what_to_prove):
        '''检验公式正确性'''
        s = z3.Solver()
        s.add(z3.Not(what_to_prove))
        if str(s.check()) == "unsat":
            return True
        else:
            return False
    
    def prove_program(self, precond, code, postcond):
        '''检验程序正确性'''
        flag, wpre = self.weakest_pre(code, True, postcond, 0)
        if flag:
            formula_to_prove = z3.Implies(precond, wpre)
            self.output.append("最终验证\n"+str(formula_to_prove))
            flag = self.prove_formula(formula_to_prove)

        return flag 

    def run(self, program):
        #print("希望证明:\n", program, "\n")
        tree = self.hoare_parser.parse(program)
        checker = BitvecTypeChecker(self.int_bit_num, self.float_type, self.output)
        checker.visit(tree.children[0])
        checker.visit(tree.children[1])
        checker.visit(tree.children[2])
        checker.visit(tree.children[3])
        #语义分析，检查类型、变量使用等是否有误
        if checker.error==False:
            self.symbol_dict = checker.symbol_dict

            proof_flag = self.prove_program(
                self.z3_exp_to_z3(tree.children[1]),
                tree.children[2],
                self.z3_exp_to_z3(tree.children[3])
            )
            if proof_flag:
                self.output.append("已完成验证")
            else:
                self.output.append("无法证明有效性")
        else:
            self.output.append("\n语义分析发现错误，停止运行")

if __name__ == '__main__':
    with open("file_name") as f:
        prover = BitvecHoareProver(16,16,16)
        prover.run(f.read())
