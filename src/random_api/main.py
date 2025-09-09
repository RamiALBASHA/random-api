from random_api.base_functions import do_this, do_that


def entrypoint(toto: int, titi: float, tata: float, param: float) -> dict[str, float]:
    return {
        'done_this': do_this(toto=toto, param=param),
        'done_that': do_that(titi=titi, tata=tata),
    }


if __name__ == "__main__":
    print(entrypoint(toto=1, titi=2, tata=3, param=1))
