from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DELETE FROM normalized_measurements"))
    conn.execute(text("DELETE FROM raw_events"))
    conn.execute(text("DELETE FROM devices"))
    conn.execute(text("DELETE FROM buildings"))
    conn.commit()
    print("All data cleared!")
