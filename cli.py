from eeval.evaluator import evaluate
from math import pi

constants = {'pi': pi}

while True:
    expr = input('Введите выражение(.q чтобы выйти): ')

    if expr == '.q':
        break

    print('Результат: ', evaluate(expr, constants=constants))
