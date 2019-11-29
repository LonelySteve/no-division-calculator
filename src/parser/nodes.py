from copy import deepcopy
from itertools import groupby
from operator import add, mul, pow, sub

from .utils import after_traverse


class Node(object):
    NAME = 'node'

    def __repr__(self):
        return f"<{self.__class__.NAME} {', '.join([k + '=' + str(v) for k, v in self.__dict__.items()])}>"

    def clone(self):
        return self.__class__()


class SingleValueNode(Node):
    """单值节点"""
    def __init__(self, value):
        self.value = value

    def clone(self):
        if hasattr(self.value, "clone"):
            copy_value = self.value.clone()
        else:
            copy_value = deepcopy(self.value)

        return self.__class__(copy_value)


class Number(SingleValueNode):
    NAME = 'number'

    def __init__(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError()
        super().__init__(value)


class Variable(SingleValueNode):
    """变元"""
    NAME = 'variable'

    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError()
        super().__init__(value)


# 这个项目只有二元操作符
class BinExpr(Node):
    NAME = 'binExpr'
    OP = ''

    _OPS = {
        '+': add,
        '-': sub,
        '*': mul,
        '^': pow,
    }

    def __init__(self, l_value, r_value):
        self.l_value = l_value
        self.r_value = r_value

    @property
    def value(self):
        return self.OP

    @property
    def op_method(self):
        return BinExpr._OPS[self.OP]

    def clone(self):
        if hasattr(self.l_value, "clone"):
            copy_l_value = self.l_value.clone()
        else:
            copy_l_value = deepcopy(self.l_value)

        if hasattr(self.r_value, "clone"):
            copy_r_value = self.r_value.clone()
        else:
            copy_r_value = deepcopy(self.r_value)

        return self.__class__(copy_l_value, copy_r_value)

    def __repr__(self):
        return f"<{self.__class__.NAME} '{self.__class__.OP}' " \
            f" {', '.join([k + '=' + str(v) for k, v in self.__dict__.items()])} > "


class Add(BinExpr):
    """加法"""
    OP = '+'


class Sub(BinExpr):
    """减法"""
    OP = '-'


class Mul(BinExpr):
    """乘法"""
    OP = '*'


class Pow(BinExpr):
    """幂"""
    OP = '^'


item_wrapper_dict = {
    "item": lambda value: value,
    "number": lambda value: Item(value.value),
    "variable": lambda value: Item(1, SubItem(**{value.value: 1}))
}


def node2item_wrapper(node):
    return item_wrapper_dict[node.__class__.__name__.lower()](node)


class MPExpression(object):
    """多元多项表达式"""
    def __init__(self, root_node):
        self._vars = set()
        self.root_node = root_node

        calc_stack = []

        def calc(node):
            # 如果是二元操作符，则弹出左右操作数，并以指定的操作方法进行计算，并将结果压回栈中
            if isinstance(node, BinExpr):
                rhs = calc_stack.pop()
                lhs = calc_stack.pop()
                # TODO 处理出错
                result = node.op_method(lhs, rhs)
                calc_stack.append(result)
            else:
                wrapped_item = node2item_wrapper(node)
                calc_stack.append(wrapped_item)

        # 逆波兰表达式计算求值
        after_traverse(root_node, calc)
        # 如果没有出错的话，结果就是栈里面最后剩下的这个结点
        # TODO 处理栈中元素不止一个的情况
        result = calc_stack[0]
        # 如果计算结果是Item，再包装成MultielementPolynomial
        if isinstance(result, Item):
            self._value = MultielementPolynomial(result)
        self._value = result

    def __eq__(self, other):
        if not isinstance(other, MPExpression):
            raise TypeError()
        return self.value == other.value

    @property
    def vars(self):
        return self._vars

    @property
    def value(self):
        return self._value


class MultielementPolynomial(Node):
    """多项式的真正容器类，会过滤掉系数为 0 的项，并确保在合适的时候进行同类项的合并"""
    def __init__(self, *items):
        self.items = [item for item in items
                      if item.coefficient != 0]  # 过滤掉系数为 0 的项
        # 合并同类项
        self.merge_similar_items()
        # 对项集合进行排序
        self.items.sort(reverse=False)

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        buffer = []
        for i, item in enumerate(self.items):
            if i == 0 and item.coefficient != 0:  # 如果为开头，且项的系数不等于0，则直接加入项
                buffer.append(item)
            else:
                if item.coefficient > 0:
                    buffer.append("+")
                    buffer.append(item)
                elif item.coefficient < 0:
                    buffer.append(item)
                # 系数为0的不显示

        # 如果buffer为空说明表达式值为0
        if not buffer:
            buffer.append(Item(0))

        return ''.join([str(i) for i in buffer])

    def merge_similar_items(self):
        """合并同类项"""
        items = self.items.copy()

        work_list = []
        result_list = []

        # 算法的基本思想是：
        # 1. 取当前项集合中的一个元素作为参照，把集合中和它有相同的项加入到 work_list 中，并从原集合中移除
        # 2. 将 work_list 中的项进行相加，最后结果加入 result_list，清空 work_list
        # 3. 如果当前集合中还有元素，继续 Step 1，否则进行 Step 4
        # 4. 将 self.items 的引用设定到 result_list

        while items:
            refer = items.pop()
            work_list.append(refer)
            work_list.extend(
                (item for item in items if item.sub_item == refer.sub_item))
            for item in work_list[1:]:
                # 不要忘了从原集合中移除这些项！
                items.remove(item)
                work_list[0] += item
            assert isinstance(
                work_list[0],
                Item)  # 理论上这里不会产生 MultielementPolynomial 类的对象，否则会造成递归问题！
            result_list.append(work_list[0])
            work_list.clear()
        self.items = result_list

    def add_or_sub(self, other, flag: bool):
        """与其他对象相加或相减 flag为True 则进行加法，否则进行减法"""
        other_items = other.items if isinstance(
            other, MultielementPolynomial) else [node2item_wrapper(other)]
        if not flag:  # 减法
            other_items = [-item for item in other_items]
        return MultielementPolynomial(*(self.items + other_items))

    def __add__(self, other):
        return self.add_or_sub(other, True)

    def __sub__(self, other):
        return self.add_or_sub(other, False)

    def __mul__(self, other):
        retVal = Item()
        if isinstance(other, MultielementPolynomial):
            # 多项式和多项式相乘
            for item_1 in self.items:
                for item_2 in other.items:
                    retVal += item_1 * item_2
        elif isinstance(other, (Item, Number, Variable, int, float)):
            # 项与多项式相乘
            for item in self.items:
                retVal += item * other
        else:
            raise TypeError()

        return retVal

    def __pow__(self, power, modulo=None):
        if isinstance(power, Number):
            result = self
            for _ in range(power.value):
                result *= self
            return result
        else:
            raise NotImplementedError("暂不支持幂为其他类型的情况")

    def __eq__(self, other):
        if not isinstance(other, MultielementPolynomial):
            raise TypeError()
        return self.items == other.items


class Item(Node):
    """项"""
    def __init__(self, coefficient=0, sub_item=None):
        self.coefficient = coefficient
        self.sub_item = sub_item or SubItem()

    def __str__(self):
        if not self.sub_item.is_empty and self.coefficient == 1:
            # 如果子项非空的情况下为系数为 1，则省去系数的显示
            if self.coefficient == 1:
                return f"{self.sub_item}"
            # 如果子项非空的情况下系数为 0，则省去项的显示，也就是 0
            if self.coefficient == 0:
                return f"{self.coefficient}"

        return f"{self.coefficient}{self.sub_item}"

    def __neg__(self):
        return Item(-self.coefficient, self.sub_item)

    def __add__(self, other):
        if isinstance(other, Item):
            # 判断是否能合并
            if (self.sub_item == other.sub_item):
                coefficient_result = self.coefficient + other.coefficient
                return Item(coefficient_result, self.sub_item)
            return MultielementPolynomial(self, other)
        elif isinstance(other, (MultielementPolynomial, Number, Variable)):
            return MultielementPolynomial(self) + other
        else:
            raise TypeError()

    def __sub__(self, other):
        if isinstance(other, Item):
            # 判断是否能合并
            if (self.sub_item == other.sub_item):
                coefficient_result = self.coefficient - other.coefficient
                return Item(coefficient_result, self.sub_item)
            return MultielementPolynomial(self, -other)
        elif isinstance(other, (MultielementPolynomial, Number, Variable)):
            return MultielementPolynomial(self) - other
        else:
            raise TypeError()

    def __mul__(self, other):
        if isinstance(other, Item):
            return Item(self.coefficient * other.coefficient,
                        self.sub_item * other.sub_item)
        elif isinstance(other, MultielementPolynomial):
            return MultielementPolynomial(self) * other
        elif isinstance(other, Number):
            return Item(self.coefficient * other.value, self.sub_item)
        elif isinstance(other, Variable):
            return Item(self.coefficient, self.sub_item * other)
        else:
            raise TypeError()

    def __pow__(self, power, modulo=None):
        if isinstance(power, Number):
            return Item(self.coefficient**power.value, self.sub_item**power)
        elif isinstance(power, Item) and power.sub_item.is_empty:
            return Item(self.coefficient**power.coefficient,
                        self.sub_item**power.coefficient)
        else:
            raise NotImplementedError("暂不支持幂为其他类型的情况")

    def __lt__(self, other):
        if isinstance(other, Item):
            # 当子项都是空的时，按系数比较大小
            if self.sub_item.is_empty and other.sub_item.is_empty:
                return self.coefficient < other.coefficient
            # 比较方式按子项比较，不管系数
            return self.sub_item < other.sub_item
        else:
            raise TypeError()

    def __eq__(self, other):
        if not isinstance(other, Item):
            raise TypeError()
        if self.coefficient != other.coefficient:
            return False
        return self.sub_item == other.sub_item


class SubItem(Node):
    def __init__(self, **kwargs):
        self.var_pow_dict = kwargs

    @property
    def is_empty(self):
        return not bool(self.var_pow_dict)

    def __str__(self):
        buffer = []
        for c, e in sorted(self.var_pow_dict.items()):
            if e == 1:
                buffer.append(f"{c}")
            else:
                buffer.append(f"{c}^{e}")
        return "*".join(buffer)

    def __eq__(self, other):
        if isinstance(other, SubItem):
            return self.var_pow_dict == other.var_pow_dict

    def __getitem__(self, item):
        return self.var_pow_dict.get(item, 0)

    def __mul__(self, other):
        if isinstance(other, SubItem):
            new_var_pow_dict = self.var_pow_dict.copy()

            for k, v in other.var_pow_dict.items():
                if k in new_var_pow_dict:
                    new_var_pow_dict[k] += v
                else:
                    new_var_pow_dict[k] = v

        elif isinstance(other, Variable):
            new_var_pow_dict = self.var_pow_dict.copy()

            if other.value in new_var_pow_dict:
                new_var_pow_dict[other.value] += 1
            else:
                new_var_pow_dict[other.value] = 1
        else:
            raise TypeError()

        return SubItem(**new_var_pow_dict)

    def __pow__(self, power, modulo=None):
        if isinstance(power, Number):
            return SubItem(
                **{k: v * power.value
                   for k, v in self.var_pow_dict.items()})
        elif isinstance(power, (int, float)):
            return SubItem(
                **{k: v * power
                   for k, v in self.var_pow_dict.items()})
        else:
            raise NotImplementedError("暂不支持幂为其他类型的情况")

    def __lt__(self, other):
        if isinstance(other, SubItem):
            # 如果己方或者对方是空，有三种情况
            if self.is_empty or other.is_empty:
                # 当己方是空，对方非空，则己方更大
                if self.is_empty and not other.is_empty:
                    return False
                # 当对方是空，己方非空，则对方更大
                elif not self.is_empty and other.is_empty:
                    return True
                # 由于没有系数信息，因此这里直接返回 False，这层实现交给上一层
                return False
            # 己方和对方都不是空，比较方案是按变量幂字典中的键的ASCII排序后对应值的大小关系
            # 有这样的情况，两个子项的变量集不一致，这个时候很好处理，直接把拥有最小变量名的子项作为较小方
            if self.var_pow_dict.keys() != other.var_pow_dict.keys():
                all_var_set = self.var_pow_dict.keys(
                ) | other.var_pow_dict.keys()
                min_var = min(all_var_set)
                return min_var in self.var_pow_dict.keys()
            for var in sorted(self.var_pow_dict.keys()):
                if self.var_pow_dict[var] == other.var_pow_dict[var]:
                    continue
                return self.var_pow_dict[var] < other.var_pow_dict[var]
        else:
            raise TypeError()
