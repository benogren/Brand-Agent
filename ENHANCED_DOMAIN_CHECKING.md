# Enhanced Domain Checking Features

## Summary

The Brand Agent now supports **10 TLDs** and **6 prefix variations** for comprehensive domain availability checking!

## What's New

### 🆕 Additional TLDs (7 new extensions)

**Before:**
- .com
- .ai
- .io

**Now:**
- .com
- .ai
- .io
- **.so** (Somalia - popular for "social" brands)
- **.app** (Google's TLD for apps)
- **.co** (Colombia - popular .com alternative)
- **.is** (Iceland - for "is" wordplay)
- **.me** (Montenegro - for personal brands)
- **.net** (Network - classic alternative)
- **.to** (Tonga - for "to" wordplay)

**Total: 10 TLDs** ✅

### 🆕 Prefix Variations (6 new options)

If `brandname.com` is taken, automatically check:
- **get**brandname.com
- **try**brandname.com
- **your**brandname.com
- **my**brandname.com
- **hello**brandname.com
- **use**brandname.com

**Total: 6 prefixes** ✅

## Usage

### Basic Usage (All 10 TLDs)

```python
from src.tools.domain_checker import check_domain_availability

# Check all 10 TLDs
results = check_domain_availability('MealMind')

# Returns:
{
    'mealmind.com': True,
    'mealmind.ai': True,
    'mealmind.io': False,
    'mealmind.so': True,
    'mealmind.app': True,
    'mealmind.co': False,
    'mealmind.is': True,
    'mealmind.me': True,
    'mealmind.net': True,
    'mealmind.to': True
}
```

### With Prefix Variations

```python
# Check with prefix variations (for .com only)
results = check_domain_availability(
    'MealMind',
    extensions=['.com'],
    include_prefixes=True
)

# Returns:
{
    'mealmind.com': False,          # Base
    'getmealmind.com': True,        # Prefix variations
    'trymealmind.com': True,
    'yourmealmind.com': True,
    'mymealmind.com': True,
    'hellomealmind.com': True,
    'usemealmind.com': True
}
```

### Get Available Alternatives

```python
from src.tools.domain_checker import get_available_alternatives

# Get smart alternatives
results = get_available_alternatives('BrandName', extensions=['.com'])

# Returns:
{
    'base': {
        'brandname.com': False
    },
    'variations': {
        'getbrandname.com': True,
        'trybrandname.com': True,
        'yourbrandname.com': False,
        'mybrandname.com': True,
        'hellobrandname.com': True,
        'usebrandname.com': True
    }
}
```

## CLI Integration

### Automatic in Phase 3 Workflow

When you run the Brand Agent:

```bash
python -m src.cli
```

**What happens:**
1. Generate 20 brand names ✅
2. Select 5-10 favorites ✅
3. **Check all 10 TLDs for each selected name** ✅
4. Display results grouped by availability ✅
5. **Suggest prefix variations if base domains are taken** ✅

### Sample Output

```
MealMind
----------------------------------------------------------------------
Domain Availability:
  ✓ Available (8):
    • mealmind.com
    • mealmind.ai
    • mealmind.so
    • mealmind.app
    • mealmind.is
    ... and 3 more

  ✗ Taken (2):
    • mealmind.io
    • mealmind.co

Trademark Risk: ✓ LOW
SEO Score: 87/100
```

### When Base Domains Are Taken

```
PopularName
----------------------------------------------------------------------
Domain Availability:
  ✗ Taken (10):
    • popularname.com
    • popularname.ai
    • popularname.io
    ... and 7 more

  💡 Try these variations:
    • getpopularname.com
    • trypopularname.com
    • mypopularname.com
```

## TLD Guide

### .com - Commercial (Most Popular)
- **Best for:** All businesses
- **Pros:** Universal recognition, trusted
- **Cons:** Highly competitive, expensive

### .ai - Artificial Intelligence
- **Best for:** AI/ML companies, tech startups
- **Pros:** Modern, tech-focused
- **Cons:** Associated with Anguilla (country code)

### .io - Input/Output
- **Best for:** Tech startups, SaaS
- **Pros:** Popular in tech community
- **Cons:** British Indian Ocean Territory (political concerns)

### .so - Social
- **Best for:** Social networks, community sites
- **Pros:** Short, memorable
- **Cons:** Somalia country code

### .app - Applications
- **Best for:** Apps, software
- **Pros:** Managed by Google, HTTPS required (secure)
- **Cons:** Relatively new

### .co - Company/Colombia
- **Best for:** Startups, .com alternative
- **Pros:** Short, looks like .com
- **Cons:** Often confused with .com

### .is - Iceland
- **Best for:** Brands with "is" wordplay (e.g., "this.is")
- **Pros:** Unique positioning
- **Cons:** Limited use cases

### .me - Personal/Montenegro
- **Best for:** Personal brands, portfolios
- **Pros:** Personal touch
- **Cons:** Less professional for B2B

### .net - Network
- **Best for:** Tech companies, .com alternative
- **Pros:** Classic TLD, trusted
- **Cons:** Less popular than .com

### .to - Tonga
- **Best for:** Brands with "to" wordplay (e.g., "go.to")
- **Pros:** Short, memorable
- **Cons:** Tonga country code

## Prefix Strategy Guide

### get[name].com
**Use case:** Action-oriented, acquisition
**Examples:**
- getslack.com → slack.com
- getdropbox.com → dropbox.com

### try[name].com
**Use case:** Free trials, demos
**Examples:**
- trynotion.com → notion.so
- tryfigma.com → figma.com

### your[name].com
**Use case:** Personalization, ownership
**Examples:**
- yourbrand.com
- yourplatform.com

### my[name].com
**Use case:** Personal dashboard, account access
**Examples:**
- myshopify.com
- myaccount.com

### hello[name].com
**Use case:** Friendly, welcoming, landing pages
**Examples:**
- hellobar.com
- hellosign.com

### use[name].com
**Use case:** Utility, tools, clear purpose
**Examples:**
- useplenty.com
- usetiful.com

## Performance

### Checking Speed

**10 TLDs (no prefixes):**
- Time: ~5-10 seconds
- Requests: 10 WHOIS lookups
- Cached: 5 minutes

**10 TLDs + 6 prefixes:**
- Time: ~35-45 seconds
- Requests: 70 WHOIS lookups (10 base + 60 variations)
- Cached: 5 minutes

**Tip:** Check base domains first, then add prefixes only if needed.

### Caching

All results are cached for 5 minutes:
```python
# First check: 10 seconds
check_domain_availability('MealMind')

# Second check (within 5 min): Instant!
check_domain_availability('MealMind')
```

## Real-World Examples

### Scenario 1: All Base Domains Available
```
Brand: "NutriNest"
Result: nutrinest.com, nutrinest.ai, nutrinest.app available
Action: Pick your favorite TLD!
```

### Scenario 2: .com Taken, Others Available
```
Brand: "FoodFlow"
Result: foodflow.com ✗, foodflow.app ✓, foodflow.io ✓
Action: Use .app or .io instead
```

### Scenario 3: All Base Domains Taken
```
Brand: "MealPlan"
Result: All base domains taken
Suggestions: getmealplan.com, trymealplan.com, mymealplan.app
Action: Use prefix variation or rebrand
```

### Scenario 4: Wordplay Opportunities
```
Brand: "ThinkBig"
Result: thinkbig.is available!
Action: Use "thinkbig.is" (reads as "Think Big Is")
```

## Configuration

### Change Default TLDs

```python
# In src/tools/domain_checker.py
DEFAULT_EXTENSIONS = ['.com', '.ai', '.io']  # Custom list
```

### Add/Remove Prefixes

```python
# In src/tools/domain_checker.py
DOMAIN_PREFIXES = ['get', 'try', 'go']  # Custom prefixes
```

### Custom Check

```python
# Check specific TLDs
check_domain_availability(
    'BrandName',
    extensions=['.com', '.app', '.co']
)

# Check with custom prefixes
check_domain_availability(
    'BrandName',
    extensions=['.com'],
    include_prefixes=True  # Uses all 6 default prefixes
)
```

## Testing

### Run Test Suite

```bash
python test_enhanced_domains.py
```

**Expected output:**
```
TEST 1: New TLD Extensions
✅ Checked 10 domains

TEST 2: Prefix Variations
✅ Checked 7 domains (1 base + 6 prefixes)

TEST 3: Available Alternatives Helper
Found X available alternatives

TEST 4: Performance Test
✅ Checked 70 domains in ~35 seconds
```

### Manual Test

```python
from src.tools.domain_checker import check_domain_availability

# Test your brand
results = check_domain_availability('YourBrandName')

# See what's available
available = [d for d, avail in results.items() if avail]
print(f"Available: {available}")
```

## Best Practices

### 1. Start with Base Domains
Check all 10 TLDs first before adding prefix variations.

### 2. Use Caching
Results are cached for 5 minutes. Check multiple names in one session.

### 3. Prioritize .com
If available, .com is still the gold standard for businesses.

### 4. Consider Brand Fit
- Tech startup? → .ai, .io, .app
- Social platform? → .so, .me
- General business? → .com, .co, .net

### 5. Prefix Variations Last Resort
Only use prefixes if base domains are all taken.

### 6. Test Wordplay
Some TLDs enable clever branding:
- "make.it" using .it
- "think.is" using .is
- "go.to" using .to

## Troubleshooting

### Slow Checks
**Cause:** WHOIS servers can be slow
**Solution:**
- Results are cached for 5 min
- Add small delay between checks (built-in)
- Check fewer TLDs: `extensions=['.com', '.app']`

### Too Many Requests
**Cause:** Hitting WHOIS rate limits
**Solution:**
- Built-in 50ms delay for large batches
- Use caching (don't re-check same domains)
- Space out checks over time

### All Domains Taken
**Cause:** Popular/generic brand name
**Solution:**
1. Try prefix variations
2. Try different TLDs (.app, .so, .is)
3. Consider rebranding
4. Add industry suffix (e.g., mealmindhealth.com)

## Summary

**Enhanced Features:**
- ✅ 10 TLDs (was 3, now 10)
- ✅ 6 prefix variations (new!)
- ✅ Smart alternative suggestions
- ✅ Grouped results display
- ✅ 5-minute caching
- ✅ Automatic integration in CLI

**Coverage:**
- Base: 10 domains per brand
- With prefixes: 70 domains per brand (10 TLDs × 7 options)

**Performance:**
- Base check: ~5-10 seconds
- Full check: ~35-45 seconds
- Cached: Instant

**Ready to use!** 🚀

Your Brand Agent now provides comprehensive domain availability checking with 10 TLDs and smart prefix suggestions!
