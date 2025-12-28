import re
from typing import Set

_SQL_PARAM_RE = re.compile(r":([a-zA-Z_][a-zA-Z0-9_]*)")

def extract_sql_params(sql: str) -> Set[str]:
    return set(_SQL_PARAM_RE.findall(sql))


from pydantic import BaseModel

def assert_sql_model_aligned(
    *,
    sql: str,
    model: type[BaseModel],
):
    sql_params = extract_sql_params(sql)
    model_fields = set(model.model_fields.keys())

    missing = sql_params - model_fields
    extra = model_fields - sql_params

    if missing or extra:
        raise AssertionError(
            "SQL <-> Model alignment error\n"
            f"Missing in model: {sorted(missing)}\n"
            f"Unused in model: {sorted(extra)}"
        )