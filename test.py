from sympy import *
from sympy.abc import x, y, z, a, b, c, f, t, k, n
from process_latex import process_sympy
theta = Symbol('theta')
f = Function('f')
# shorthand definitions


def _Add(a, b):
    return Add(a, b, evaluate=False)


def _Mul(a, b):
    return Mul(a, b, evaluate=False)


def _Pow(a, b):
    return Pow(a, b, evaluate=False)


def _Abs(a):
    return Abs(a, evaluate=False)


def _factorial(a):
    return factorial(a, evaluate=False)


def _log(a, b):
    return log(a, b, evaluate=False)


# These latex strings should parse to the corresponding
# SymPy expression
GOOD_PAIRS = [
    ("0", 0),
    ("1", 1),
    ("-3.14", _Mul(-1, 3.14)),
    ("(-7.13)(1.5)", _Mul(_Mul(-1, 7.13), 1.5)),
    ("x", x),
    ("2x", 2*x),
    ("x^2", x**2),
    ("x^{3 + 1}", x**_Add(3, 1)),
    ("-c", -c),
    ("a \\cdot b", a * b),
    ("a / b", a / b),
    ("a \\div b", a / b),
    ("a + b", a + b),
    ("a + b - a", _Add(a+b, -a)),
    ("a^2 + b^2 = c^2", Eq(a**2 + b**2, c**2)),
    ("\\sin \\theta", sin(theta)),
    ("\\sin(\\theta)", sin(theta)),
    ("\\sin^{-1} a", asin(a)),
    ("\\sin a \\cos b", _Mul(sin(a), cos(b))),
    ("\\sin \\cos \\theta", sin(cos(theta))),
    ("\\sin(\\cos \\theta)", sin(cos(theta))),
    ("\\frac{a}{b}", a / b),
    ("\\frac{a + b}{c}", _Mul(a + b, _Pow(c, -1))),
    ("\\frac{7}{3}", _Mul(7, _Pow(3, -1))),
    ("(\\csc x)(\\sec y)", csc(x)*sec(y)),
    ("\\lim_{x \\to 3} a", Limit(a, x, 3)),
    ("\\lim_{x \\rightarrow 3} a", Limit(a, x, 3)),
    ("\\lim_{x \\Rightarrow 3} a", Limit(a, x, 3)),
    ("\\lim_{x \\longrightarrow 3} a", Limit(a, x, 3)),
    ("\\lim_{x \\Longrightarrow 3} a", Limit(a, x, 3)),
    ("\\lim_{x \\to 3^{+}} a", Limit(a, x, 3, dir='+')),
    ("\\lim_{x \\to 3^{-}} a", Limit(a, x, 3, dir='-')),
    ("\\infty", oo),
    ("\\lim_{x \\to \\infty} \\frac{1}{x}",
     Limit(_Mul(1, _Pow(x, -1)), x, oo)),
    ("\\frac{d}{dx} x", Derivative(x, x)),
    ("\\frac{d}{dt} x", Derivative(x, t)),
    ("f(x)", f(x)),
    ("f(x, y)", f(x, y)),
    ("f(x, y, z)", f(x, y, z)),
    ("\\frac{d f(x)}{dx}", Derivative(f(x), x)),
    # ("\\frac{d\\theta(x)}{dx}", Derivative(theta(x), x)),
    ("|x|", _Abs(x)),
    ("||x||", _Abs(Abs(x))),
    ("|x||y|", _Abs(x)*_Abs(y)),
    ("||x||y||", _Abs(_Abs(x)*_Abs(y))),
    ("\pi^{|xy|}", Symbol('pi')**_Abs(x*y)),
    ("\\int x dx", Integral(x, x)),
    ("\\int x d\\theta", Integral(x, theta)),
    ("\\int (x^2 - y)dx", Integral(x**2 - y, x)),
    ("\\int x + a dx", Integral(_Add(x, a), x)),
    ("\\int da", Integral(1, a)),
    ("\\int_0^7 dx", Integral(1, (x, 0, 7))),
    ("\\int_a^b x dx", Integral(x, (x, a, b))),
    ("\\int^b_a x dx", Integral(x, (x, a, b))),
    ("\\int_{a}^b x dx", Integral(x, (x, a, b))),
    ("\\int^{b}_a x dx", Integral(x, (x, a, b))),
    ("\\int_{a}^{b} x dx", Integral(x, (x, a, b))),
    ("\\int^{b}_{a} x dx", Integral(x, (x, a, b))),
    ("\\int_{f(a)}^{f(b)} f(z) dz", Integral(f(z), (z, f(a), f(b)))),
    ("\\int (x+a)", Integral(_Add(x, a), x)),
    ("\\int a + b + c dx", Integral(_Add(_Add(a, b), c), x)),
    ("\\int \\frac{dz}{z}", Integral(Pow(z, -1), z)),
    ("\\int \\frac{3 dz}{z}", Integral(3*Pow(z, -1), z)),
    ("\\int \\frac{1}{x} dx", Integral(Pow(x, -1), x)),
    ("\\int \\frac{1}{a} + \\frac{1}{b} dx",
     Integral(_Add(_Pow(a, -1), Pow(b, -1)), x)),
    ("\\int \\frac{3 \cdot d\\theta}{\\theta}",
     Integral(3*_Pow(theta, -1), theta)),
    ("\\int \\frac{1}{x} + 1 dx", Integral(_Add(_Pow(x, -1), 1), x)),
    ("x_0", Symbol('x_{0}')),
    ("x_{1}", Symbol('x_{1}')),
    ("x_a", Symbol('x_{a}')),
    ("x_{b}", Symbol('x_{b}')),
    ("h_\\theta", Symbol('h_{theta}')),
    ("h_{\\theta}", Symbol('h_{theta}')),
    ("h_{\\theta}(x_0, x_1)", Function('h_{theta}')(
        Symbol('x_{0}'), Symbol('x_{1}'))),
    ("x!", _factorial(x)),
    ("100!", _factorial(100)),
    ("\\theta!", _factorial(theta)),
    ("(x + 1)!", _factorial(_Add(x, 1))),
    ("(x!)!", _factorial(_factorial(x))),
    ("x!!!", _factorial(_factorial(_factorial(x)))),
    ("5!7!", _Mul(_factorial(5), _factorial(7))),
    ("\\sqrt{x}", sqrt(x)),
    ("\\sqrt{x + b}", sqrt(_Add(x, b))),
    ("\\sqrt[3]{\\sin x}", root(sin(x), 3)),
    ("\\sqrt[y]{\\sin x}", root(sin(x), y)),
    ("\\sqrt[\\theta]{\\sin x}", root(sin(x), theta)),
    ("x < y", StrictLessThan(x, y)),
    ("x \\leq y", LessThan(x, y)),
    ("x > y", StrictGreaterThan(x, y)),
    ("x \\geq y", GreaterThan(x, y)),
    ("\\mathit{x}", Symbol('x')),
    ("\\mathit{test}", Symbol('test')),
    ("\\mathit{TEST}", Symbol('TEST')),
    ("\\mathit{HELLO world}", Symbol('HELLO world')),
    ("\\sum_{k = 1}^{3} c", Sum(c, (k, 1, 3))),
    ("\\sum_{k = 1}^3 c", Sum(c, (k, 1, 3))),
    ("\\sum^{3}_{k = 1} c", Sum(c, (k, 1, 3))),
    ("\\sum^3_{k = 1} c", Sum(c, (k, 1, 3))),
    ("\\sum_{k = 1}^{10} k^2", Sum(k**2, (k, 1, 10))),
    ("\\sum^{\\infty}_{n = 0} \\frac{1}{n!}",
     Sum(_factorial(n) ** -1, (n, 0, oo))),
    ("\\prod_{a = b}^{c} x", Product(x, (a, b, c))),
    ("\\prod_{a = b}^c x", Product(x, (a, b, c))),
    ("\\prod^{c}_{a = b} x", Product(x, (a, b, c))),
    ("\\prod^c_{a = b} x", Product(x, (a, b, c))),
    ("\\ln x", _log(x, E)),
    ("\\ln xy", _log(x*y, E)),
    ("\\log x", _log(x, 10)),
    ("\\log xy", _log(x*y, 10)),
    ("\\log_{2} x", _log(x, 2)),
    ("\\log_{a} x", _log(x, a)),
    ("\\log_{11} x", _log(x, 11)),
    ("\\log_{a^2} x", _log(x, _Pow(a, 2))),
    ("[x]", x),
    ("[a + b]", _Add(a, b)),
    ("\\frac{d}{dx} [ \\tan x ]", Derivative(tan(x), x))
]
# These bad latex strings should raise an exception when parsed
BAD_STRINGS = [
    "(",
    ")",
    # "a / b /",
    "\\frac{d}{dx}",
    "(\\frac{d}{dx})"
    "\\sqrt{}",
    "\\sqrt",
    "{",
    "}",
    # "1.1.1",
    "\\mathit{x + y}",
    "\\mathit{21}",
    "\\frac{2}{}",
    "\\frac{}{2}",
    "\\int",
    # "1 +",
    # "a +",
    "!",
    "!0",
    "_",
    "^",
    # "a // b",
    # "a \\cdot \\cdot b",
    # "a \\div \\div b",
    "|",
    "||x|",
    "()",
    "((((((((((((((((()))))))))))))))))",
    "-",
    "\\frac{d}{dx} + \\frac{d}{dt}",
    # "f()",
    # "f(,",
    "f(x,,y)",
    "f(x,y,",
    "\\sin^x",
    "\\cos^2",
    # "\\cos 1 \\cos",
    "@", "#", "$", "%", "&", "*",
    "\\",
    "~",
    "\\frac{(2 + x}{1 - x)}"]
total = 0
passed = 0
for s, eq in GOOD_PAIRS:
    total += 1
    try:
        if process_sympy(s) != eq:
            print("ERROR: \"%s\" did not parse to %s" % (s, eq))
        else:
            passed += 1
    except Exception as e:
        print("ERROR: Exception when parsing \"%s\"" % s)
for s in BAD_STRINGS:
    total += 1
    try:
        process_sympy(s)
        print("ERROR: Exception should have been raised for \"%s\"" % s)
    except Exception:
        passed += 1
print("%d/%d STRINGS PASSED" % (passed, total))
