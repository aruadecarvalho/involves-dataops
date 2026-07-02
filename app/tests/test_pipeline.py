import pandas as pd

from pipeline.pipeline import transform


def _orders():
    return pd.DataFrame(
        [
            {
                "order_id": 1,
                "region": "North",
                "quantity": 2,
                "unit_price": 10.0,
                "order_date": "2026-01-01",
            },
            {
                "order_id": 2,
                "region": "North",
                "quantity": 1,
                "unit_price": 5.0,
                "order_date": "2026-01-02",
            },
            {
                "order_id": 3,
                "region": "South",
                "quantity": 3,
                "unit_price": 10.0,
                "order_date": "2026-01-03",
            },
        ]
    )


def test_transform_shape_and_columns():
    out = transform(_orders())
    assert set(out.columns) == {"region", "orders", "revenue"}
    assert len(out) == 2  # two regions


def test_transform_aggregates_revenue_and_counts():
    out = transform(_orders()).set_index("region")
    assert out.loc["North", "orders"] == 2
    assert out.loc["North", "revenue"] == 25.0  # 2*10 + 1*5
    assert out.loc["South", "revenue"] == 30.0  # 3*10


def test_transform_sorted_by_revenue_desc():
    out = transform(_orders())
    assert list(out["region"]) == ["South", "North"]  # 30 before 25
