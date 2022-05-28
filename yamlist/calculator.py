from yamlist import expr
from yamlist import strexpr
from yamlist import dictexpr

def calc(src, config):
    bindings = {}

    bindings["null"] = None
    bindings["true"] = True
    bindings["debug"] = True
    bindings["false"] = False
    bindings["empty"] = NoElementValue()

    for key, value in config.items():
        bindings[key] = value

    result = evaluate_final(buildEvaluating(src, bindings))
    result = value_to_single(result)
    return result


class NoElementValue:
    pass

def buildEvaluating(expr, bindings):
    if isinstance(expr, str):
        return strexpr.EvaluatingStr(expr, bindings)
    elif isinstance(expr, dict):
        return dictexpr.EvaluatingDict(expr, bindings)
    #elif isinstance(expr, list):
    #    return EvaluatingList(expr, bindings)
    else:
        return expr

def evaluate_final(src):
    while True:
        if not isinstance(src, expr.EvaluatingExpr):
            return src
        src = src.evaluate()

def value_to_single(obj):
    if isinstance(obj, NoElementValue):
        return None
    #elif isinstance(obj, ListInListValue):
    #    return obj.items
    else:
        return obj

def exists_in_bindings(bindings, name):
    if name is None:
        return True

    if isinstance(bindings, expr.EvaluatingExpr):
        return bindings.exists_name(name)

    if not isinstance(bindings, dict):
        return False

    n1, n2 = parse_name(name)
    if n1 in bindings:
        return exists_in_bindings(bindings[n1], n2)
    else:
        return False

def get_from_bindings(bindings, name):
    if name is None:
        return bindings

    if isinstance(bindings, expr.EvaluatingExpr):
        return bindings.get_by_name(name)

    if not isinstance(bindings, dict):
        return None

    n1, n2 = parse_name(name)
    if n1 in bindings:
        return get_from_bindings(bindings[n1], n2)
    else:
        return None

def parse_name(name):
    p = name.find(".")
    if p < 0:
        return (name, None)
    else:
        return (name[0:p], name[p+1:])

