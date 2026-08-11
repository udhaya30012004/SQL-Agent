"""
Test Script for TableSelectorWithGraph

Tests table selection across 3 complexity levels:
- LEVEL 1: Simple / Single Table Queries
- LEVEL 2: Intermediate / 1-2 Joins
- LEVEL 3: Advanced / Multi-table Analytics
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.db.db_connector import connect_database


def main():
    # ==================== DATABASE SETUP ====================
    
    CONNECTION_STRING = 'postgresql+psycopg2://postgres:1234@localhost:5432/pagila'
    
    print("\n" + "=" * 70)
    print("TABLE SELECTOR TEST SUITE")
    print("=" * 70)
    
    engine = connect_database(CONNECTION_STRING)
    schema = extract_schema(engine)
    selector = TableSelectorWithGraph(schema)
    
    # Optional: View relationship graph structure
    print("\nInitializing schema and relationship graph...")
    # selector.print_graph_debug()
    
    # ==================== TEST QUESTIONS ====================
    
    questions = [
        # 🟢 LEVEL 1: Simple / Single Table Queries
        {
            "level": "LEVEL 1",
            "color": "🟢",
            "query": "Show all available movies in alphabetical order",
            "expected": ["film"]
        },
        {
            "level": "LEVEL 1",
            "color": "🟢",
            "query": "How many active customers do we currently have?",
            "expected": ["customer"]
        },
        {
            "level": "LEVEL 1",
            "color": "🟢",
            "query": "List the top 10 longest movies in the database",
            "expected": ["film"]
        },
        {
            "level": "LEVEL 1",
            "color": "🟢",
            "query": "What are the different unique movie ratings available?",
            "expected": ["film"]
        },
        
        # 🟡 LEVEL 2: Intermediate / 1-2 Joins
        {
            "level": "LEVEL 2",
            "color": "🟡",
            "query": "List customer names and the titles of the movies they rented",
            "expected": ["customer", "rental", "inventory", "film"]
        },
        {
            "level": "LEVEL 2",
            "color": "🟡",
            "query": "Which movies are in the 'Action' or 'Comedy' categories?",
            "expected": ["film", "category", "film_category"]
        },
        {
            "level": "LEVEL 2",
            "color": "🟡",
            "query": "Find all movies that feature the actor 'Nick Stallone'",
            "expected": ["film", "actor", "film_actor"]
        },
        {
            "level": "LEVEL 2",
            "color": "🟡",
            "query": "Show the total rental revenue collected by each store location",
            "expected": ["store", "rental", "payment_p2022_01"]
        },
        {
            "level": "LEVEL 2",
            "color": "🟡",
            "query": "List all customers who live in Canada",
            "expected": ["customer", "address", "city", "country"]
        },
        
        # 🔴 LEVEL 3: Advanced / Multi-table Analytics
        {
            "level": "LEVEL 3",
            "color": "🔴",
            "query": "What are the top 5 most rented movies of all time?",
            "expected": ["film", "rental", "inventory"]
        },
        {
            "level": "LEVEL 3",
            "color": "🔴",
            "query": "Which customer has spent the most money on movie rentals?",
            "expected": ["customer", "rental", "payment_p2022_01"]
        },
        {
            "level": "LEVEL 3",
            "color": "🔴",
            "query": "What is the average rental cost for each distinct movie category?",
            "expected": ["film", "category", "film_category", "rental"]
        },
        {
            "level": "LEVEL 3",
            "color": "🔴",
            "query": "Which staff member processed the highest number of rental transactions?",
            "expected": ["staff", "rental", "payment_p2022_01"]
        },
        {
            "level": "LEVEL 3",
            "color": "🔴",
            "query": "List the top 3 countries with the highest number of registered customers",
            "expected": ["country", "city", "address", "customer"]
        }
    ]
    
    # ==================== TEST EXECUTION ====================
    
    level_1_correct = 0
    level_2_correct = 0
    level_3_correct = 0
    
    for i, test_case in enumerate(questions, 1):
        level = test_case["level"]
        color = test_case["color"]
        query = test_case["query"]
        expected = test_case["expected"]
        
        # Select tables
        selected = selector.select_tables(
            query,
            top_k=3,
            expand_depth=1
        )
        
        # Check correctness (at least one expected table in selected)
        is_correct = any(table in selected for table in expected)
        
        # Update statistics
        if level == "LEVEL 1" and is_correct:
            level_1_correct += 1
        elif level == "LEVEL 2" and is_correct:
            level_2_correct += 1
        elif level == "LEVEL 3" and is_correct:
            level_3_correct += 1
        
        # Print result
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"\n{color} [{level}] Query {i}")
        print("-" * 70)
        print(f"Question:        {query}")
        print(f"Expected tables: {expected}")
        print(f"Selected tables: {selected}")
        print(f"Status:          {status}")
    
    # ==================== SUMMARY ====================
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\n🟢 LEVEL 1 (Simple):       {level_1_correct}/4 passed")
    print(f"🟡 LEVEL 2 (Intermediate): {level_2_correct}/5 passed")
    print(f"🔴 LEVEL 3 (Advanced):     {level_3_correct}/6 passed")
    
    total_passed = level_1_correct + level_2_correct + level_3_correct
    total_tests = 15
    percentage = (total_passed / total_tests) * 100
    
    print(f"\n📊 Overall: {total_passed}/{total_tests} passed ({percentage:.1f}%)")
    print("\n" + "=" * 70)
    
    # ==================== DETAILED ANALYSIS ====================
    
    print("\nDETAILED ANALYSIS (Optional - uncomment to view)")
    print("-" * 70)
    
    # Uncomment to see detailed selection process for a specific query
    # selector.print_selection_process(
    #     "List customer names and the titles of the movies they rented",
    #     top_k=3,
    #     expand_depth=1
    # )


if __name__ == "__main__":
    main()
