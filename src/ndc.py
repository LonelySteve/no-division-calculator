import sys

from .parser.parser import Parser


def handle_args(args):
    if len(args) > 1:
        if args[1] == '-c':
            if len(args) > 2:
                p = Parser(args[2])
                print(p.parse().value)
                return
        elif args[1] == '-h' or args[1] == '--help':
            print("-c <expression> 计算指定表达式，结果输出到标准输出流")
            print("-h, --help    显示此帮助消息")
            print()
            # 打印版权声明
            print("no-division-calculator Copyright (C) 2019 JLoeve")
            return
    interactive()


def interactive():
    # 打印欢迎信息
    print("Welcome to the no-division-calculator!")
    # 打印版权声明
    print("no-division-calculator Copyright (C) 2019 JLoeve")
    while True:
        try:
            expression = input(">")
            if not expression.strip():
                continue  # 跳过空语句
            p = Parser(expression)
            print(p.parse().value)
        except KeyboardInterrupt as ex:
            exit(0)
        except Exception as ex:
            print(ex)


def main(args):
    handle_args(args)


if __name__ == '__main__':
    main(sys.argv)
