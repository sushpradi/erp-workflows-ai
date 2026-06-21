from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def _read_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_all_data() -> dict[str, Any]:
    return {
        "workflows": _read_json("workflows.json"),
        "budgets": _read_json("budgets.json"),
        "vendors": _read_json("vendors.json"),
        "invoices": _read_json("invoices.json"),
        "approvals": _read_json("approvals.json"),
        "payments": _read_json("payments.json"),
        "revenue": _read_json("revenue.json"),
        "payroll": _read_json("payroll.json"),
        "receivables": _read_json("receivables.json"),
        "subscriptions": _read_json("subscriptions.json"),
    }


def reload_all_data() -> dict[str, Any]:
    load_all_data.cache_clear()
    return load_all_data()
