from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.database import Base, engine
Base.metadata.create_all(engine)
print(f"Database ready: {engine.url}")
