import sys
from sqlalchemy import create_engine, text

# Configurations
ORDER_DB_URL = "mysql+pymysql://user:password@localhost:3307/order_db"
DRIVER_DB_URL = "mysql+pymysql://user:password@localhost:3308/driver_db"

def soft_reset():
    print("Starting SOFT RESET (Keeping Users, Restaurants, Drivers)...")
    
    # 1. Clear Orders (Order Service)
    print("Resetting ORDERS...")
    engine_order = create_engine(ORDER_DB_URL)
    with engine_order.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("TRUNCATE TABLE order_items;"))
        conn.execute(text("TRUNCATE TABLE orders;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()
    print("Orders Cleared.")
    
    # 2. Reset Driver Earnings & Salaries (Driver Service)
    print("Resetting DRIVER EARNINGS & SALARIES...")
    engine_driver = create_engine(DRIVER_DB_URL)
    with engine_driver.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("TRUNCATE TABLE driver_salaries;"))
        conn.execute(text("UPDATE drivers SET total_earnings = 0;")) # Reset Wallet
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()
    print("Driver Earnings Reset.")
    
    print("SOFT RESET COMPLETE. Users, Restaurants, and Driver Accounts are preserved.")

if __name__ == "__main__":
    soft_reset()
