#!/usr/bin/env python3
"""
Test script to demonstrate the new interactive Phase 3 workflow.

This script simulates what happens when a user runs the CLI.
"""

import sys
sys.path.insert(0, '/Users/benogren/Desktop/projects/Brand-Agent')

from src.cli import (
    print_brand_names_simple,
    run_phase3_validation,
    print_validation_results
)

# Sample generated names (simulating Phase 1 output)
sample_names = [
    {
        'brand_name': 'MealMind',
        'naming_strategy': 'portmanteau',
        'rationale': 'Combines "Meal" and "Mind" to suggest intelligent meal planning',
        'tagline': 'Smart planning for busy families',
        'syllables': 2,
        'memorable_score': 8
    },
    {
        'brand_name': 'NutriNest',
        'naming_strategy': 'portmanteau',
        'rationale': 'Nutrition + Nest creates a warm, family-oriented brand',
        'tagline': 'Where healthy meals find home',
        'syllables': 3,
        'memorable_score': 9
    },
    {
        'brand_name': 'Yumora',
        'naming_strategy': 'invented',
        'rationale': 'Invented name suggesting yum + aura, brings joy to meals',
        'tagline': 'Bringing joy back to mealtime',
        'syllables': 3,
        'memorable_score': 7
    },
    {
        'brand_name': 'FamilyFeast',
        'naming_strategy': 'descriptive',
        'rationale': 'Clearly describes the product focus on family meals',
        'tagline': 'Plan together, feast together',
        'syllables': 4,
        'memorable_score': 7
    },
    {
        'brand_name': 'PlateWise',
        'naming_strategy': 'portmanteau',
        'rationale': 'Plate + Wise suggests smart food choices',
        'tagline': 'Wisdom on every plate',
        'syllables': 2,
        'memorable_score': 8
    }
]

# Configuration
config = {
    'project_id': 'your-project-id',
    'location': 'us-central1'
}

# User brief
brief = {
    'product_description': 'AI meal planning app for busy parents',
    'target_audience': 'Busy parents',
    'brand_personality': 'professional',
    'industry': 'food_tech'
}

print("\n" + "=" * 70)
print("INTERACTIVE PHASE 3 WORKFLOW DEMONSTRATION")
print("=" * 70 + "\n")

print("STEP 1: User sees 20 generated brand names")
print("-" * 70)
print_brand_names_simple(sample_names)

print("\n\nSTEP 2: User selects 5 favorites (simulated)")
print("-" * 70)
selected_names = sample_names  # In real CLI, user would select 5-10

print("Selected names:")
for name in selected_names:
    print(f"  - {name['brand_name']}")

print("\n\nSTEP 3: Run Phase 3 validation on selected names")
print("-" * 70)
print("(In production, this would check domain availability, trademark, SEO)")
print("(For this demo, we'll skip the actual API calls)")

print("\n✓ Workflow structure is ready!")
print("\nThe new workflow:")
print("  1. Generate 20 brand names")
print("  2. User selects 5-10 favorites")
print("  3. Run Phase 3 validation ONLY on selected names:")
print("     - Domain availability check (.com, .ai, .io)")
print("     - Trademark risk assessment (USPTO)")
print("     - SEO optimization (meta tags, keywords)")
print("     - Enhanced taglines and rationale")
print("  4. User can regenerate if not satisfied (preserves context)")
print("\n" + "=" * 70)
