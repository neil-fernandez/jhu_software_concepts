import load_data as db
import psycopg


if __name__ == "__main__":
    db.load()

    connection = psycopg.connect(
        dbname="studentCourses",
        user="postgres")

    with connection.cursor() as cur:
        cur.execute("""
        select * from applicantData
        """)
        rows = cur.fetchall()

    print(rows)
