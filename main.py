from eeval.evaluator import evaluate

from math import pi
import timeit

exprs = (
	"2+2*2",
	"(2+2)+(2+2)",
	"-(2+2)+-(2+2)",
	"(2+2)*-(2+2)",
	"-(-(-(-(3*88888))))",
	"pi*2",
	"(pi+1)*(pi+2)",
	"-pi",
	"pi^2"
)

constants = {
	"pi": pi
}

itercount = 1000

print("Evaluator test:")

for expr in exprs:
	print(expr, "=", evaluate(expr, constants=constants), "timeit: ", end="", flush=True)
	print(timeit.timeit("e(expr, constants=c)", globals={"e": evaluate, "expr": expr, "c": constants}, number=itercount))

