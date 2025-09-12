def do_this(toto: int, param: float = 1.) -> float:
    return toto * param


def do_that(titi: float, tata: float) -> float:
    return titi - tata


def do_it(stuff: dict) -> int:
    return stuff['a'] + stuff['b']
