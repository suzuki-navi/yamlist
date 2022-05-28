from yamlist import expr

class EvaluatingStr(expr.EvaluatingExpr):
    def __init__(self, expr, bindings):
        super().__init__(expr, bindings)

    def __repr__(self):
        return f"EvaluatingStr({self.expr})"

    def fetch(self):
        src = self.expr
        return src # TODO

