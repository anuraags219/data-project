import random
import string
import time

import psycopg2

conn = psycopg2.connect(
    host="postgres",
    database="inventory",
    user="postgres",
    password="postgres"
)

conn.autocommit = True


def random_name():
    return "".join(
        random.choices(string.ascii_uppercase, k=6)
    )


while True:
    operation = random.choices(
        ["insert", "update", "delete"],
        weights=[70, 25, 5]
    )[0]

    with conn.cursor() as cur:

        if operation == "insert":

            cur.execute(
                """
                INSERT INTO customers(name, age)
                VALUES (%s, %s)
                RETURNING id
                """,
                (
                    random_name(),
                    random.randint(18, 80)
                )
            )

            row_id = cur.fetchone()[0]

            print(
                f"[INSERT] id={row_id}"
            )

        elif operation == "update":

            cur.execute(
                """
                SELECT id
                FROM customers
                ORDER BY random()
                LIMIT 1
                """
            )

            row = cur.fetchone()

            if row:

                cur.execute(
                    """
                    UPDATE customers
                    SET age=%s,
                        updated_at=NOW()
                    WHERE id=%s
                    """,
                    (
                        random.randint(18, 80),
                        row[0]
                    )
                )

                print(
                    f"[UPDATE] id={row[0]}"
                )

        else:

            cur.execute(
                """
                SELECT id
                FROM customers
                ORDER BY random()
                LIMIT 1
                """
            )

            row = cur.fetchone()

            if row and row[0] > 1:

                cur.execute(
                    """
                    DELETE FROM customers
                    WHERE id=%s
                    """,
                    (row[0],)
                )

                print(
                    f"[DELETE] id={row[0]}"
                )

    time.sleep(10)