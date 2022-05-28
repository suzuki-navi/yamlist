import json

import jinja2
import jinja2.meta

from yamlist import calculator
from yamlist import expr

class EvaluatingStr(expr.EvaluatingExpr):
    def __init__(self, expr, bindings):
        super().__init__(expr, bindings)

    def __repr__(self):
        return f"EvaluatingStr({self.expr})"

    def fetch(self):
        src = self.expr
        if src.startswith("$$"):
            return self.render_template(src[1:])
        #elif src.startswith("$"):
        #    return evaluate_func_call_str([], src[1:], {}, self.bindings)
        else:
            return self.render_template(src)

    def render_template(self, src):
        env = jinja2.Environment(keep_trailing_newline=True)
        ast = env.parse(src)
        var_names = []
        var_names.extend(jinja2.meta.find_undeclared_variables(ast))
        vars2 = {}
        for name in var_names:
            if calculator.exists_in_bindings(self.bindings, name):
                v = calculator.evaluate_final(calculator.get_from_bindings(self.bindings, name))
            else:
                v = "ERROR"
            vars2[name] = value_to_string(v)
        result = env.from_string(src).render(vars2)
        return result

def value_to_string(value):
    if isinstance(value, str):
        return value
    return json.dumps(value)

