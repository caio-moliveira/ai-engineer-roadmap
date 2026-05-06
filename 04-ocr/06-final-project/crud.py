from database import get_db


def get_all_receipts() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM receipts ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_receipt(receipt_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM receipts WHERE id = ?", (receipt_id,)
        ).fetchone()
    return dict(row) if row else None


def insert_receipt(receipt: dict) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO receipts
               (id, description, amount, purchase_time, location, raw_text, created_at)
               VALUES (:id, :description, :amount, :purchase_time, :location, :raw_text, :created_at)""",
            receipt,
        )


def update_receipt(receipt_id: str, fields: dict) -> dict | None:
    set_clause = ", ".join(f"{col} = :{col}" for col in fields)
    params = {**fields, "receipt_id": receipt_id}

    with get_db() as conn:
        result = conn.execute(
            f"UPDATE receipts SET {set_clause} WHERE id = :receipt_id", params
        )
        if result.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT * FROM receipts WHERE id = ?", (receipt_id,)
        ).fetchone()

    return dict(row)


def delete_receipt(receipt_id: str) -> bool:
    with get_db() as conn:
        result = conn.execute(
            "DELETE FROM receipts WHERE id = ?", (receipt_id,)
        )
    return result.rowcount > 0
