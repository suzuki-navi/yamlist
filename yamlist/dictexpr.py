import json

import jinja2
import jinja2.meta

from yamlist import calculator
from yamlist import expr

class EvaluatingDict(expr.EvaluatingExpr):
    def __init__(self, expr, bindings):
        super().__init__(expr, bindings)
        self.bindings2 = bindings.copy()
        self.prepared = None

    def fetch(self):
        prepared = self.prepare()
        dst = {}
        for key, elem in prepared.items():
            r = calculator.evaluate_final(elem)
            if not isinstance(r, calculator.NoElementValue):
                dst[key] = calculator.value_to_single(r)
        return dst

    def prepare(self):
        if self.prepared is not None:
            return self.prepared
        for key, expr in self.get_consts().items():
            self.bindings2[key] = expr
        params = self.get_params()
        if len(params) == 0:
            self.prepared = self.prepare_dict()
        else:
            self.prepared = self.prepare_func() # TODO
        return self.prepared

    def prepare_dict(self):
        if "$_" in self.expr:
            return calculator.buildEvaluating(src["$_"], self.bindings2)
        dst = {}
        for key, elem in self.expr.items():
            if key.startswith("$$"):
                key = key[1:]
            elif key.startswith("$"):
                key = None
            elif key.startswith("=$"):
                key_name_value = calculator.evaluate_final(calculator.buildEvaluating(key[1:], self.bindings2))
                key = strexpr.value_to_string(key_name_value)
            if key is not None:
                dst[key] = calculator.buildEvaluating(elem, self.bindings2)
        return dst

    def get_consts(self):
        consts = {}
        for key, elem in self.expr.items():
            if key.startswith("$") and not key.startswith("$$") and key != "$_":
                if elem != "$param":
                    consts[key[1:]] = calculator.buildEvaluating(elem, self.bindings2)
        return consts

    def get_params(self):
        params = []
        for key, elem in self.expr.items():
            if key.startswith("$") and not key.startswith("$$") and key != "$_":
                if elem == "$param":
                    params.append(key[1:])
        return params

    def exists_name(self, name):
        prepared = self.prepare()
        n1, n2 = parse_name(name)
        if n1 in prepared:
            return calculator.exists_in_bindings(prepared[n1], n2)
        else:
            return False

    def get_by_name(self, name):
        prepared = self.prepare()
        n1, n2 = parse_name(name)
        if n1 in prepared:
            return calculator.get_from_bindings(prepared[n1], n2)
        else:
            return False

