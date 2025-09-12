from the_package.base_functions import do_this, do_that, do_it


def entrypoint(
        toto: int,
        titi: float,
        tata: float,
        param: float,
        stuff: dict
) -> dict[str, float]:
    return {
        'done_this': do_this(toto=toto, param=param),
        'done_that': do_that(titi=titi, tata=tata),
        'do_it': do_it(stuff=stuff),
    }


if __name__ == "__main__":
    print(entrypoint(toto=1, titi=2, tata=3, param=1, stuff={'a': 1, 'b': 2}))
