from typing import Any


def use_setter(obj: Any, setter_name: str, new_value: Any) -> None:
    setter = getattr(type(obj), setter_name).fset
    setter(obj, new_value)
