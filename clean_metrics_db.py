"""
Clean (clear) all metrics from the database.

This script removes all metrics data from the database tables
while preserving the database structure.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.observability.metrics_db import get_metrics_db
from sqlalchemy import text


def clean_database():
    """Remove all metrics from the database."""
    print("🗑️  Cleaning metrics database...")
    
    db = get_metrics_db()
    
    try:
        with db.get_session() as session:
            # Count records before deletion
            request_count = session.execute(
                text("SELECT COUNT(*) FROM request_metrics")
            ).scalar()
            
            aggregated_count = session.execute(
                text("SELECT COUNT(*) FROM aggregated_metrics")
            ).scalar()
            
            print(f"\n📊 Current database state:")
            print(f"  - Request metrics: {request_count} records")
            print(f"  - Aggregated metrics: {aggregated_count} records")
            
            if request_count == 0 and aggregated_count == 0:
                print("\n✅ Database is already clean!")
                return
            
            # Confirm deletion
            response = input(f"\n⚠️  Are you sure you want to delete all {request_count + aggregated_count} records? (yes/no): ")
            
            if response.lower() not in ['yes', 'y']:
                print("❌ Cancelled. No data was deleted.")
                return
            
            # Delete all records
            session.execute(text("DELETE FROM aggregated_metrics"))
            session.execute(text("DELETE FROM request_metrics"))
            session.commit()
            
            print(f"\n✅ Successfully deleted:")
            print(f"  - {request_count} request metrics")
            print(f"  - {aggregated_count} aggregated metrics")
            print(f"\n📍 Database location: {db.db_path}")
            print(f"📊 Database is now clean and ready for new metrics!")
            
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        clean_database()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
