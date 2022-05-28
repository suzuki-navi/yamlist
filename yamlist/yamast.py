
import pyparsing as pp

from yamlist import calculator

def create_pp_expr():
    word = pp.Word(pp.alphanums + "_")

    expr = pp.Forward()

    exprs = expr + pp.ZeroOrMore("," + expr)

    def funccall_action(ss):
        if len(ss) == 1:
            return [ss[0]]
        else:
            args = []
            i = 2
            while i < len(ss):
                args.append(ss[i])
                i = i + 2
            return [[ss[0], args]]

    funccall = (word + pp.Opt("(" + exprs + ")")).setParseAction(funccall_action)

    def equal_expr_action(ss):
        if len(ss) == 1:
            return [ss[0]]
        if ss[1] == "==":
            return [["equal", [ss[0], ss[2]]]]
        elif ss[1] == "!=":
            return [["not_equal", [ss[0], ss[2]]]]

    equal_expr = (funccall + pp.Opt(pp.oneOf("== !=") + funccall)).setParseAction(equal_expr_action)

    expr << equal_expr

    return expr

parser = create_pp_expr()

def evaluate_ast(ast, bindings):
    if isinstance(ast, str):
        funcname = ast
        args = []
    else:
        funcname = ast[0]
        args = ast[1]
    if funcname == "if":
        if len(args) >= 3:
            return evaluate_if3(args[0], args[1], args[2], bindings)
        elif len(args) >= 2:
            return evaluate_if2(args[0], args[1], bindings)
        elif len(args) >= 1:
            return evaluate_if1(args[0], bindings)
    elif funcname == "elif":
        if len(args) >= 1:
            return evaluate_elif(args[0], bindings)
    elif funcname == "else":
        return evaluate_else(bindings)
    elif funcname == "endif":
        return evaluate_endif(bindings)

    if calculator.exists_in_bindings(bindings, funcname):
        return calculator.get_from_bindings(bindings, funcname)
        # TODO 関数だった場合の対応
    else:
        return funcname

def evaluate_if3(cond, then_expr, else_expr, bindings):
    cond_result = ast_to_boolean(cond, bindings)
    if cond_result:
        return evaluate_ast(then_expr, bindings)
    else:
        return evaluate_ast(else_expr, bindings)

def evaluate_if2(cond, then_expr, bindings):
    cond_result = ast_to_boolean(cond, bindings)
    if cond_result:
        return evaluate_ast(then_expr, bindings)
    else:
        return calculator.NoElementValue()

def evaluate_if1(cond, bindings):
    cond_result = ast_to_boolean(cond, bindings)
    def operate_stack_if(stack_if):
        stack_if2 = stack_if.copy()
        if cond_result:
            stack_if2.append(1)
        else:
            stack_if2.append(0)
        return stack_if2
    return calculator.CondStackOperationValue(operate_stack_if)

def evaluate_elif(cond, bindings):
    cond_result = ast_to_boolean(cond, bindings)
    def operate_stack_elif(stack_if):
        stack_if2 = stack_if.copy()
        c = stack_if2.pop()
        if c == 0:
            if cond_result:
                stack_if2.append(1)
            else:
                stack_if2.append(0)
        else:
            stack_if2.append(-1)
        return stack_if2
    return calculator.CondStackOperationValue(operate_stack_elif)

def evaluate_else(bindings):
    def operate_stack_else(stack_if):
        stack_if2 = stack_if.copy()
        c = stack_if2.pop()
        if c == 0:
            stack_if2.append(1)
        else:
            stack_if2.append(0)
        return stack_if2
    return calculator.CondStackOperationValue(operate_stack_else)

def evaluate_endif(bindings):
    def operate_stack_endif(stack_if):
        stack_if2 = stack_if.copy()
        stack_if2.pop()
        return stack_if2
    return calculator.CondStackOperationValue(operate_stack_endif)

def ast_to_boolean(cond, bindings):
    result = calculator.evaluate_final(evaluate_ast(cond, bindings))
    if result == False:
        return False
    if result == "":
        return False
    if result == 0:
        return False
    return True


