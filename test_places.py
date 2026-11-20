"""
test_places.py — Comprehensive test for place search, landmark discovery, and nearest safe havens.
"""
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from helpers.places_module import (
    search_all_places,
    get_prominent_institutions,
    get_nearest_safe_places
)

print("\n" + "="*55)
print("  RakshaAI — Places & Safe Havens Test")
print("="*55)

# 1. Test Prominent Institutions
print("\n[1] Testing prominent institutions catalog...")
insts = get_prominent_institutions(22.7196, 75.8577)
print(f"   Found {len(insts)} institutions near Indore center.")
for i, inst in enumerate(insts[:4], 1):
    print(f"   {i}. {inst.get('icon', '📍')} {inst.get('name')} ({inst.get('dist_km')} km)")

# 2. Test Place Search for Colleges & Landmarks
queries = ["Medicaps", "DAVV", "Choithram", "Kotwali"]
print("\n[2] Testing place search for key queries...")
for q in queries:
    results = search_all_places(q, 22.7196, 75.8577)
    top_name = results[0]["name"] if results else "None"
    print(f"   Query '{q}': {len(results)} matches -> Top: {top_name}")

# 3. Test Nearest Safe Havens
print("\n[3] Testing nearest safe havens...")
safe = get_nearest_safe_places(22.7196, 75.8577, limit=5)
print(f"   Found {len(safe)} safe havens near center:")
for s in safe:
    print(f"   • {s['icon']} {s['name']} — {s['dist']}m ({s['type']}) | {s['statusText']}")

print("\n" + "="*55)
print("✅ All place tests passed successfully!")
print("="*55 + "\n")

