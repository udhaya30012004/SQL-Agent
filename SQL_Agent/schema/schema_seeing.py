"""
Schema Inspector Script

Displays all schema information extracted from the database:
- Table names and descriptions
- Columns with data types and nullability
- Primary keys
- Foreign key relationships
"""

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.db.db_connector import connect_database


def print_schema_overview(schema: dict) -> None:
    """Print a comprehensive overview of all tables in the schema."""
    
    print("\n" + "=" * 90)
    print("DATABASE SCHEMA OVERVIEW")
    print("=" * 90)
    
    print(f"\n📊 Total Tables: {len(schema)}\n")
    
    for i, (table_name, table_info) in enumerate(schema.items(), 1):
        
        print(f"\n{i}. TABLE: {table_name.upper()}")
        print("-" * 90)
        
        # Description
        description = table_info.get("description", "")
        if description:
            print(f"   📝 Description: {description}")
        
        # Columns
        columns = table_info.get("columns", [])
        print(f"\n   📋 Columns ({len(columns)}):")
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "")
            nullable = col.get("nullable", False)
            nullable_str = "NULL" if nullable else "NOT NULL"
            print(f"      • {col_name:<25} {col_type:<20} [{nullable_str}]")
        
        # Primary Keys
        pk = table_info.get("primary_keys", [])
        if pk:
            print(f"\n   🔑 Primary Key: {', '.join(pk)}")
        
        # Foreign Keys
        fks = table_info.get("foreign_keys", [])
        if fks:
            print(f"\n   🔗 Foreign Keys ({len(fks)}):")
            for fk in fks:
                col = fk.get("column", [])
                ref_table = fk.get("referred_table", "")
                ref_cols = fk.get("referred_columns", [])
                col_str = ", ".join(col) if isinstance(col, list) else col
                ref_col_str = ", ".join(ref_cols) if isinstance(ref_cols, list) else ref_cols
                print(f"      • {col_str} → {ref_table}({ref_col_str})")
        
        print()


def print_schema_json(schema: dict) -> None:
    """Print schema in JSON format for detailed inspection."""
    
    print("\n" + "=" * 90)
    print("SCHEMA IN JSON FORMAT")
    print("=" * 90 + "\n")
    
    print(json.dumps(schema, indent=2))


def print_relationship_summary(schema: dict) -> None:
    """Print a summary of all table relationships."""
    
    print("\n" + "=" * 90)
    print("RELATIONSHIP SUMMARY")
    print("=" * 90)
    
    print("\n🔗 TABLE RELATIONSHIPS:\n")
    
    for table_name, table_info in schema.items():
        fks = table_info.get("foreign_keys", [])
        
        if fks:
            print(f"📌 {table_name}")
            for fk in fks:
                ref_table = fk.get("referred_table", "")
                print(f"   └─ references → {ref_table}")


def print_table_stats(schema: dict) -> None:
    """Print statistics about the schema."""
    
    print("\n" + "=" * 90)
    print("SCHEMA STATISTICS")
    print("=" * 90 + "\n")
    
    total_tables = len(schema)
    total_columns = sum(len(table.get("columns", [])) for table in schema.values())
    total_fks = sum(len(table.get("foreign_keys", [])) for table in schema.values())
    total_pks = sum(1 for table in schema.values() if table.get("primary_keys"))
    
    print(f"📊 Total Tables:           {total_tables}")
    print(f"📋 Total Columns:          {total_columns}")
    print(f"🔑 Tables with PK:         {total_pks}")
    print(f"🔗 Total Foreign Keys:     {total_fks}")
    
    avg_cols_per_table = total_columns / total_tables if total_tables > 0 else 0
    print(f"📈 Avg Columns per Table:  {avg_cols_per_table:.1f}")


def main():
    """Main function to run schema inspection."""
    
    # ==================== DATABASE SETUP ====================
    
    CONNECTION_STRING = 'postgresql+psycopg2://postgres:1234@localhost:5432/pagila'
    
    print("\n" + "=" * 90)
    print("SCHEMA INSPECTOR")
    print("=" * 90)
    
    print("\n🔌 Connecting to database...")
    engine = connect_database(CONNECTION_STRING)
    
    print("📚 Extracting schema...")
    schema = extract_schema(engine)
    
    # ==================== DISPLAY OPTIONS ====================
    
    while True:
        print("\n" + "=" * 90)
        print("SCHEMA INSPECTION MENU")
        print("=" * 90)
        print("\n1. 📊 Overview (Formatted table view)")
        print("2. 📑 JSON (Raw JSON format)")
        print("3. 🔗 Relationships (Table relationships summary)")
        print("4. 📈 Statistics (Schema statistics)")
        print("5. 🔍 Search Table (Find specific table)")
        print("6. 🚪 Exit\n")
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            print_schema_overview(schema)
        
        elif choice == "2":
            print_schema_json(schema)
        
        elif choice == "3":
            print_relationship_summary(schema)
        
        elif choice == "4":
            print_table_stats(schema)
        
        elif choice == "5":
            table_search = input("\nEnter table name to search (partial match): ").strip().lower()
            matching_tables = {k: v for k, v in schema.items() if table_search in k.lower()}
            
            if matching_tables:
                print(f"\n✅ Found {len(matching_tables)} matching table(s):\n")
                for table_name, table_info in matching_tables.items():
                    print(f"TABLE: {table_name.upper()}")
                    columns = table_info.get("columns", [])
                    for col in columns:
                        print(f"  • {col.get('name')}: {col.get('type')}")
                    print()
            else:
                print(f"\n❌ No tables found matching '{table_search}'")
        
        elif choice == "6":
            print("\n👋 Goodbye!\n")
            break
        
        else:
            print("\n⚠️  Invalid option. Please select 1-6.")


if __name__ == "__main__":
    main()
