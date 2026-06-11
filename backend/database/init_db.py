from database.db import engine, Base
from database import models

def init():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    init()
