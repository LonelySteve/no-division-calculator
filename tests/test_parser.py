from src.parser.parser import Parser


def assert_parse(expression, result, strict=True):
    p = Parser(expression)
    if strict:
        assert str(p.parse().value) == result
    else:
        assert p.parse() == Parser(result).parse()


class TestLiteral(object):
    def test_alone_number(self):
        assert_parse("-22", "-22")
        assert_parse("33", "33")
        assert_parse("0.001", "0.001")

        assert_parse("0", "0")
        assert_parse("0.0", "0.0")
        assert_parse("-0", "0")

    def test_0_add_something(self):
        assert_parse("0+0", "0")
        assert_parse("1+0", "1")
        assert_parse("-1+0", "-1")
        assert_parse("1.0+0", "1.0")
        assert_parse("0+1", "1")
        assert_parse("0+1.0", "1.0")
        assert_parse("0+233", "233")

    def test_0_sub_something(self):
        assert_parse("0-0", "0")
        assert_parse("1-0", "1")
        assert_parse("-1-0", "-1")
        assert_parse("1.0-0", "1.0")
        assert_parse("0-1", "-1")
        assert_parse("0-1.0", "-1.0")
        assert_parse("0-233", "-233")

    def test_add(self):
        assert_parse("1+1", "2")
        assert_parse("-1+-1", "-2")
        assert_parse("123+456", "579")
        assert_parse("1+1+1", "3")
        assert_parse("1+2+3", "6")
        assert_parse("1-1+1-1", "0")
        assert_parse("2-(1+1)+((1+2)-3)", "0")
        assert_parse("1.5+1.5", "3.0")

    def test_sub(self):
        assert_parse("1-1", "0")
        assert_parse("1-2", "-1")
        assert_parse("1.5-1.5", "0.0")
        assert_parse("123-456", "-333")
        assert_parse("1-(1-1)-1-(1-1)", "0")

    def test_mul(self):
        assert_parse("1*1", "1")
        assert_parse("1*1*0", "0")
        assert_parse("1*(1*1*(1*1*1))", "1")
        assert_parse("1*(1*1*(1*1*1))*0", "0")
        assert_parse("-1*-1", "1")
        assert_parse("-2 * 2", "-4")
        assert_parse("2 * -3", "-6")
        assert_parse("-3*(1+2-3)", "0")
        assert_parse("9-8*1", "1")
        assert_parse("9-9*1", "0")
        assert_parse("9-9*(2-3^6)", "6552")


class TestVariable(object):
    def test_simple(self):
        assert_parse("x", "x")
        assert_parse("x*y", "x*y")
        assert_parse("z*y*x", "x*y*z")

        assert_parse("x^1", "x")
        assert_parse("x*y^1", "x*y")
        assert_parse("z^2*y^1*x", "x*y*z^2")

        assert_parse("10*z*y*x", "10x*y*z")
        assert_parse("10*z*y^2*x", "10x*y^2*z")

    def test_normal(self):
        assert_parse("x*x^2*x^3", "x^6")
        assert_parse("x*x^2*x^3*y", "x^6*y")

    def test_difficulty(self):
        assert_parse("(x^2+2*y^8) * (x^2+2*y^8)", "x^4+4x^2*y^8+4y^16")
        assert_parse("x*(x^2+x^3)", "x^3+x^4")
        assert_parse("(8*x^9+5*x^8*y^7+3*x^4*y^4+6*y^2-5) * (6*x^5*y^4+7*x^3*y^2+21*x*y^2+8)",
        "48*x^14*y^4+56*x^12*y^2+168*x^10*y^2+64*x^9+30*x^13*y^11" \
                            "+35*x^11*y^9+105*x^9*y^9+40*x^8*y^7+18*x^9*y^8+21*x^7*y^6" \
                            "+99*x^5*y^6+24*x^4*y^4+42*y^4*x^3+126*y^4*x+48*y^2-30*x^5*y^4-35*x^3*y^2-105*x*y^2-40",
                            strict=False)

    def test_mixed(self):
        assert_parse("(0+a)", "a")
        assert_parse("0+a", "a")
        assert_parse("a-(0+3*x)", "a-3x")
