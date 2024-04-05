import z3
from lark import Tree
from PyQt5.QtWidgets import QTextBrowser

from .hoare_parser import simple_parser
from .hoare_type_checker import TypeChecker

def print_with_tab_prefix(string: str, n: int, output: QTextBrowser):
    '''打印字符串，每行开头有n个回车前缀'''
    output.append(n*'\t'+string.replace('\n', '\n'+n*'\t'))

class HoareProver():
    def __init__(self, output: QTextBrowser):
        '''
        int类型用z3.Int表示
        float类型用z3.Real表示
        '''
        self.hoare_parser = simple_parser
        self.symbol_dict = {}
        # 符号表，含有类型、是否为数组、对应的z3求解器中符号等标注
        self.output = output
        self.output.clear()

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
            return self.bool_exp_to_z3(e1) <= self.bool_exp_to_z3(e2)
        
        elif exp.data == "ge":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) >= self.bool_exp_to_z3(e2)
        
        elif exp.data == "eq":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) == self.bool_exp_to_z3(e2)
        
        elif exp.data == "neq":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) != self.bool_exp_to_z3(e2)
        
        elif exp.data == "lt":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) < self.bool_exp_to_z3(e2)
        
        elif exp.data == "gt":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) > self.bool_exp_to_z3(e2)
        
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
            return self.bool_exp_to_z3(e1) + self.bool_exp_to_z3(e2)
        
        elif exp.data == "minus":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) - self.bool_exp_to_z3(e2)
        
        elif exp.data == "multi":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) * self.bool_exp_to_z3(e2)
        
        elif exp.data == "divide":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) / self.bool_exp_to_z3(e2)
        
        elif exp.data == "mod":
            e1, e2 = exp.children
            return self.bool_exp_to_z3(e1) % self.bool_exp_to_z3(e2)
        
        elif exp.data == "neg":
            e1 = exp.children[0]
            return 0-self.bool_exp_to_z3(e1)
        
        elif exp.data == "number_int":
            return z3.IntVal(exp.children[0])
        
        elif exp.data == "number_float":
            return z3.RealVal(exp.children[0])
        
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
                number=z3.ToReal(number)
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
            # if
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
        #语义分析，检查类型、变量使用等是否有误
        #print("希望证明:\n", program, "\n")
        tree = self.hoare_parser.parse(program)
        checker = TypeChecker(self.output)
        checker.visit(tree.children[0])
        checker.visit(tree.children[1])
        checker.visit(tree.children[2])
        checker.visit(tree.children[3])
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
    with open("swap.lpp") as f:
        prover = HoareProver()
        prover.run(f.read())