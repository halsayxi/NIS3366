from lark import Lark

simple_grammar = """
    ?program: var_dec_list "{" z3_exp "}" stmt_list "{" z3_exp "}"      

    ?var_dec_list:  (var_dec)*                          -> var_dec_list

    ?var_dec : specifier var_decl ("," var_decl)* ";"   -> name_list

    ?var_decl : CNAME ("[" INT "]")?                    -> var_decl

    ?specifier : "int"                                  -> int
        | "float"                                       -> float

    ?var_use : CNAME ("[" exp "]")?                     -> var_use

    ?stmt_list: (stmt)*                                                                         -> seq

    ?stmt: "if" "(" bool_exp ")" "{" stmt_list "}" "else" "{" stmt_list "}"                     -> if_else
        | "if" "(" bool_exp ")" "{" stmt_list "}"                                               -> if
        | "{" "inv" ":" bool_exp "}" "while" "(" bool_exp ")" "{" stmt_list "}"                 -> while
        | "skip" ";"                                                                            -> skip
        | var_use "=" exp ";"                                                                   -> assignment
        | ";"                                                                                   -> skip
      
    ?z3_exp: z3_imply
        | z3_exp "<=>" z3_imply                         -> equiv
    
    ?z3_imply: z3_or
        | z3_imply "->" z3_or                           -> imply
    
    ?z3_or: z3_and
        | z3_or "or" z3_and                             -> z3_or
    
    ?z3_and: z3_not
        | z3_and "and" z3_not                           -> z3_and
        | z3_and ";" z3_not                             -> z3_and

    ?z3_not: z3_atom       
        | "not" z3_atom                                 -> z3_not
        
    ?z3_atom: "(" z3_exp ")"
        | bool_exp
        | "forall"  CNAME ("," CNAME)*  "(" z3_exp ")"    -> forall
        | "exists"  CNAME ("," CNAME)*  "(" z3_exp ")"    -> exists
                             
    ?bool_exp: and_term
        | bool_exp "||" and_term        -> or
        
    ?and_term: not_term
        | and_term "&&" not_term        -> and
        
    ?not_term: bool_atom
        |"!" bool_atom                  -> not
    
    ?bool_atom : "(" bool_exp ")"       
        | "true"                        -> true
        | "false"                       -> false
        | exp "<=" exp                  -> le
        | exp ">=" exp                  -> ge
        | exp "==" exp                  -> eq
        | exp "!=" exp                  -> neq
        | exp "<" exp                   -> lt
        | exp ">" exp                   -> gt

    ?exp: product
        | exp "+" product               -> plus
        | exp "-" product               -> minus

    ?product: atom
        | product "*" atom              -> multi
        | product "/" atom              -> divide
        | product "%" atom              -> mod

    ?atom: INT                          -> number_int
        | FLOAT                         -> number_float
        | "-" atom                      -> neg
        | var_use                      
        | "(" exp ")"  

    COMMENT : "/*" /(.|\\n|\\r)+/ "*/"  
        |  "//" /(.)+/ NEWLINE
    
    %import common.NEWLINE
    %ignore COMMENT
        
    %import common.CNAME 
    %import common.INT
    %import common.FLOAT
    %import common.WS
    %ignore WS
    """
simple_parser = Lark(simple_grammar, start='program')

