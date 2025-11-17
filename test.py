from sqlalchemy import create_engine
engine = create_engine('sqlite:///your_database.db')
with engine.connect() as conn:
    result = conn.execute("PRAGMA table_info(onboarding_registration);")
    for row in result:
        print(row)
