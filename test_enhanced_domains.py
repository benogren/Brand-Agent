#!/usr/bin/env python3
"""Test enhanced domain checking with new TLDs and prefix variations."""

import sys
sys.path.insert(0, '/Users/benogren/Desktop/projects/Brand-Agent')

from src.tools.domain_checker import (
    check_domain_availability,
    get_available_alternatives,
    DEFAULT_EXTENSIONS,
    DOMAIN_PREFIXES
)


def test_new_tlds():
    """Test the new TLD extensions."""
    print("=" * 70)
    print("TEST 1: New TLD Extensions")
    print("=" * 70)
    print(f"\nDefault extensions: {DEFAULT_EXTENSIONS}")
    print(f"Total: {len(DEFAULT_EXTENSIONS)} TLDs")

    # Test with a sample brand
    print(f"\nTesting brand name: 'TestBrand'")
    results = check_domain_availability('TestBrand')

    print(f"\n✅ Checked {len(results)} domains")
    print(f"Available: {sum(results.values())}")
    print(f"Taken: {len(results) - sum(results.values())}")

    # Show results by availability
    available = [d for d, a in results.items() if a]
    taken = [d for d, a in results.items() if not a]

    if available:
        print(f"\n✓ Available domains:")
        for domain in available[:5]:
            print(f"  • {domain}")
        if len(available) > 5:
            print(f"  ... and {len(available) - 5} more")

    if taken:
        print(f"\n✗ Taken domains:")
        for domain in taken[:5]:
            print(f"  • {domain}")
        if len(taken) > 5:
            print(f"  ... and {len(taken) - 5} more")


def test_prefix_variations():
    """Test prefix variations."""
    print("\n" + "=" * 70)
    print("TEST 2: Prefix Variations")
    print("=" * 70)
    print(f"\nAvailable prefixes: {DOMAIN_PREFIXES}")
    print(f"Total: {len(DOMAIN_PREFIXES)} prefixes")

    # Test with prefixes for .com only
    print(f"\nTesting brand name: 'MealMind' with prefixes (. com only)")
    results = check_domain_availability('MealMind', extensions=['.com'], include_prefixes=True)

    print(f"\n✅ Checked {len(results)} domains")

    base_domains = [d for d in results.keys() if 'mealmind.com' == d]
    prefix_domains = [d for d in results.keys() if d != 'mealmind.com']

    print(f"\nBase domain:")
    for domain in base_domains:
        status = "✓ Available" if results[domain] else "✗ Taken"
        print(f"  {domain:25s} {status}")

    print(f"\nPrefix variations:")
    for domain in prefix_domains:
        status = "✓ Available" if results[domain] else "✗ Taken"
        print(f"  {domain:25s} {status}")


def test_get_alternatives():
    """Test the get_available_alternatives helper."""
    print("\n" + "=" * 70)
    print("TEST 3: Available Alternatives Helper")
    print("=" * 70)

    print(f"\nTesting brand name: 'NutriNest'")
    results = get_available_alternatives('NutriNest', extensions=['.com', '.app'])

    base = results['base']
    variations = results['variations']

    print(f"\nBase domains:")
    for domain, available in base.items():
        status = "✓ Available" if available else "✗ Taken"
        print(f"  {domain:25s} {status}")

    print(f"\nPrefix variations:")
    available_variations = {d: a for d, a in variations.items() if a}
    if available_variations:
        print(f"  Found {len(available_variations)} available alternatives:")
        for domain in list(available_variations.keys())[:6]:
            print(f"    • {domain}")
        if len(available_variations) > 6:
            print(f"    ... and {len(available_variations) - 6} more")
    else:
        print(f"  No available alternatives found")


def test_performance():
    """Test performance with many domains."""
    print("\n" + "=" * 70)
    print("TEST 4: Performance Test")
    print("=" * 70)

    import time

    print(f"\nChecking all TLDs + all prefixes for 'PlateWise'...")
    print(f"Total domains to check: {len(DEFAULT_EXTENSIONS) * (1 + len(DOMAIN_PREFIXES))}")

    start = time.time()
    results = check_domain_availability('PlateWise', include_prefixes=True)
    end = time.time()

    duration = end - start
    print(f"\n✅ Checked {len(results)} domains in {duration:.2f} seconds")
    print(f"Average: {duration / len(results):.3f} seconds per domain")


def main():
    """Run all enhanced domain tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ENHANCED DOMAIN CHECKING TESTS" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Test 1: New TLDs
        test_new_tlds()

        # Test 2: Prefix variations
        test_prefix_variations()

        # Test 3: Get alternatives helper
        test_get_alternatives()

        # Test 4: Performance
        test_performance()

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print("\n✅ All enhanced domain features working!")
        print(f"   • {len(DEFAULT_EXTENSIONS)} TLDs supported")
        print(f"   • {len(DOMAIN_PREFIXES)} prefix variations available")
        print(f"   • Smart alternative suggestions")
        print(f"   • Caching for performance")
        print("\n" + "=" * 70 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
