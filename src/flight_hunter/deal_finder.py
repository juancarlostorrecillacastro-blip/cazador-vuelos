"""Decide si un precio ya juzgado como chollo merece un aviso nuevo."""


def is_new_best_price(price: float, previous_best: float | None) -> bool:
    """Solo merece un aviso nuevo si no habia aviso previo, o si el precio bajo aun mas."""
    return previous_best is None or price < previous_best
