"""
Check Database Schema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)
columns = inspector.get_columns('companies')

print("Companies table columns:")
print("-" * 40)
for col in columns:
    print(f"  - {col['name']}: {col['type']}")
