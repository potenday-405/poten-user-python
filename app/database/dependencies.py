async def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()