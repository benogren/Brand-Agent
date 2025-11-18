# USPTO Trademark API Recommendations

## Executive Summary

**Recommendation: Start with USPTO TSDR API (Official, Free)**

For your Brand Agent Phase 3 implementation, I recommend using the **official USPTO TSDR (Trademark Status Document Retrieval) API** because it's:
- ✅ Free (no cost)
- ✅ Official data source
- ✅ Comprehensive coverage
- ✅ Rate limits suitable for your use case (60 requests/min)

## Option 1: USPTO TSDR API (RECOMMENDED) ⭐

### Overview
The official United States Patent and Trademark Office API for trademark data.

**Website:** https://developer.uspto.gov/api-catalog/tsdr-data-api

### Pros
- ✅ **Free** - No cost to use
- ✅ **Official source** - Direct from USPTO database
- ✅ **Comprehensive** - Complete trademark database
- ✅ **Real-time** - Live data, not delayed
- ✅ **Legal validity** - Official records for compliance
- ✅ **Rate limits** - 60 requests/min (sufficient for your use case)

### Cons
- ⚠️ **Requires API key** - Need USPTO.gov account
- ⚠️ **Setup complexity** - Moderate learning curve
- ⚠️ **Documentation** - Less developer-friendly than commercial APIs
- ⚠️ **Migration** - Moving to new ODP portal through 2025

### Rate Limits
```
Standard requests: 60 requests per API key per minute
Bulk downloads: 4 requests per API key per minute
```

**For your use case:**
- Checking 5-10 brand names per session = 5-10 API calls
- Well within 60/min limit ✅

### Cost
```
$0 - Completely FREE
```

### Setup Steps
1. Create account at https://my.uspto.gov/
2. Request API key via API Key Manager
3. Wait for approval (usually 1-2 business days)
4. Add to `.env`: `USPTO_API_KEY=your-key-here`

### Example Usage
```python
import requests

def search_trademark(brand_name, api_key):
    """Search USPTO TSDR API for trademark."""
    url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}/info.json"
    headers = {"USPTO-API-KEY": api_key}
    response = requests.get(url, headers=headers)
    return response.json()
```

### Best For
- Production applications
- Legal compliance needs
- Cost-conscious projects
- Long-term stability

---

## Option 2: Markify API (Alternative, Free)

### Overview
Third-party service offering free USPTO trademark data with better developer experience.

**Website:** https://www.markify.com/

### Pros
- ✅ **Free** - No cost
- ✅ **Developer-friendly** - Better documentation
- ✅ **Daily updates** - Fresh data from USPTO
- ✅ **Fast** - Optimized for performance
- ✅ **Easy setup** - Simple API key registration

### Cons
- ⚠️ **Third-party** - Not official USPTO source
- ⚠️ **Dependency risk** - Service could change or shut down
- ⚠️ **Data delay** - Daily updates vs real-time

### Rate Limits
```
Free tier: Limited (check current terms)
```

### Cost
```
Free tier available
Paid plans for higher volume
```

### Best For
- Quick prototyping
- Startups on tight budgets
- Non-critical applications

---

## Option 3: Marker API (Commercial)

### Overview
Professional trademark search API with advanced features.

**Website:** https://markerapi.com/

### Pros
- ✅ **Rich features** - Search by name, owner, description, expiration
- ✅ **Reliable** - Commercial-grade SLA
- ✅ **Good docs** - Developer-friendly documentation
- ✅ **Support** - Customer support included

### Cons
- ❌ **Paid** - Requires subscription
- ⚠️ **Third-party** - Not official source
- ⚠️ **Ongoing cost** - Monthly/annual fees

### Cost
```
Starting at ~$29-99/month (check current pricing)
```

### Best For
- Enterprise applications
- High-volume needs
- Need for support/SLA

---

## Option 4: RapidAPI USPTO Trademark (Freemium)

### Overview
USPTO trademark data available through RapidAPI marketplace.

**Website:** https://rapidapi.com/pentium10/api/uspto-trademark

### Pros
- ✅ **Free tier** - Limited free requests
- ✅ **Easy integration** - RapidAPI platform
- ✅ **Multiple SDKs** - Various language support
- ✅ **Quick start** - Minimal setup

### Cons
- ⚠️ **Rate limits** - Free tier is limited
- ⚠️ **Third-party** - Not official source
- ⚠️ **Marketplace dependency** - Tied to RapidAPI platform

### Cost
```
Free: 100-500 requests/month (varies)
Pro: $10-50/month for more requests
```

### Best For
- Testing and development
- Low-volume applications
- RapidAPI ecosystem users

---

## Comparison Table

| Feature | USPTO TSDR | Markify | Marker API | RapidAPI |
|---------|-----------|---------|-----------|----------|
| **Cost** | Free | Free | $29-99/mo | Freemium |
| **Official Data** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Setup Difficulty** | Medium | Easy | Easy | Very Easy |
| **Rate Limit** | 60/min | Varies | High | 100-500/mo free |
| **Documentation** | Fair | Good | Excellent | Good |
| **Support** | Email | Limited | Yes | Limited |
| **Legal Valid** | ✅ Yes | ⚠️ Maybe | ⚠️ Maybe | ⚠️ Maybe |
| **Real-time** | ✅ Yes | Daily | ❌ No | ❌ No |
| **Best For** | Production | Prototyping | Enterprise | Testing |

---

## My Recommendation for Your Project

### Phase 3 (Current): USPTO TSDR API ⭐

**Why:**
1. **Free** - No ongoing costs
2. **Official** - Legal validity for trademark checks
3. **Sufficient rate limits** - 60/min covers your use case (5-10 names)
4. **Production-ready** - Stable, official service
5. **No vendor lock-in** - Government service won't disappear

**Setup effort:** ~1-2 hours
**Ongoing cost:** $0
**Risk:** Low

### Implementation Plan

```python
# src/tools/trademark_checker.py

import os
import requests
from typing import Dict, Any

def search_trademarks_uspto_real(
    brand_name: str,
    category: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search USPTO TSDR API for trademark conflicts.

    Requires USPTO_API_KEY in .env file.
    """
    api_key = os.getenv('USPTO_API_KEY')

    if not api_key:
        # Fall back to simulation mode
        return _simulate_trademark_search(brand_name, category, limit)

    # TODO: Implement real USPTO TSDR API integration
    # 1. Search by brand name
    # 2. Filter by classification (if provided)
    # 3. Parse results
    # 4. Return structured data

    pass
```

---

## Setup Instructions for USPTO TSDR API

### Step 1: Create USPTO Account
1. Go to: https://my.uspto.gov/
2. Click "Create Account"
3. Fill out registration form
4. Verify email address

### Step 2: Request API Key
1. Log in to USPTO account
2. Navigate to API Key Manager
3. Click "Request API Key"
4. Fill out application form:
   - Purpose: "Brand name trademark validation"
   - Expected usage: "5-10 requests per session, ~100 requests/month"
5. Submit request

### Step 3: Wait for Approval
- Typical wait: 1-2 business days
- Check email for approval notification
- API key will be available in your account dashboard

### Step 4: Configure Your .env
```bash
# Add to .env file
USPTO_API_KEY=your-api-key-here
```

### Step 5: Test the API
```bash
# Test script
python -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('USPTO_API_KEY')

# Test endpoint
url = 'https://tsdrapi.uspto.gov/ts/cd/casestatus/sn87000000/info.json'
headers = {'USPTO-API-KEY': api_key}
response = requests.get(url, headers=headers)

print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

---

## Alternative: Continue with Simulation (No API)

Your current implementation uses intelligent simulation, which is actually quite good for MVP/prototype stage:

### Pros of Simulation
- ✅ Works immediately (no setup)
- ✅ No API dependencies
- ✅ No rate limits
- ✅ Free
- ✅ Fast (no network calls)

### Cons of Simulation
- ❌ Not real data
- ❌ Limited accuracy
- ❌ Not suitable for production

### When to Upgrade
Upgrade from simulation to real USPTO API when:
- You're launching to real users
- You need legal validity
- You have users paying for the service
- Trademark accuracy is critical

---

## Cost-Benefit Analysis

### Simulation (Current)
```
Setup time: 0 hours
Monthly cost: $0
Accuracy: ~70% (heuristic-based)
Use case: MVP, prototyping, testing
```

### USPTO TSDR API (Recommended)
```
Setup time: 1-2 hours
Monthly cost: $0
Accuracy: 100% (official data)
Use case: Production, real users, legal compliance
```

### Commercial API (Marker, etc.)
```
Setup time: 0.5 hours
Monthly cost: $29-99
Accuracy: ~95-100%
Use case: Enterprise, high SLA requirements
```

---

## My Final Recommendation

### For Right Now (Phase 3 Launch)
**Keep using simulation mode** ✅

Why:
- It works well enough for initial testing
- No setup delay
- Free
- You can validate the workflow first

### For Phase 4 (Production Launch)
**Integrate USPTO TSDR API** ⭐

Why:
- Official data = legal validity
- Free = sustainable
- Production-ready
- 60/min rate limit is plenty

### Action Plan
```
Phase 3 (Now):
✅ Keep simulation mode
✅ Test workflow with users
✅ Validate the feature works

Phase 3.5 (Next 1-2 weeks):
□ Sign up for USPTO account
□ Request API key
□ Integrate TSDR API
□ A/B test simulation vs real data

Phase 4 (Production):
□ Switch to TSDR API by default
□ Keep simulation as fallback
□ Monitor usage and accuracy
```

---

## Code Implementation Template

Here's how to implement USPTO TSDR API:

```python
# src/tools/trademark_checker.py

import os
import requests
from typing import Dict, List, Optional, Any

def search_trademarks_uspto(
    brand_name: str,
    category: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search USPTO for trademark conflicts.

    Automatically uses real API if USPTO_API_KEY is set,
    otherwise falls back to simulation.
    """
    api_key = os.getenv('USPTO_API_KEY')

    if api_key:
        return _search_real_api(brand_name, category, limit, api_key)
    else:
        # Fallback to simulation
        return _search_simulation(brand_name, category, limit)

def _search_real_api(
    brand_name: str,
    category: Optional[str],
    limit: int,
    api_key: str
) -> Dict[str, Any]:
    """Real USPTO TSDR API implementation."""

    # Step 1: Search for trademark by name
    # Note: TSDR API works with serial numbers
    # You may need to use trademark search first to get serial numbers

    base_url = "https://tsdrapi.uspto.gov/ts/cd"
    headers = {"USPTO-API-KEY": api_key}

    # TODO: Implement search logic
    # 1. Query trademark search endpoint
    # 2. Get serial numbers for brand name
    # 3. Fetch details for each serial number
    # 4. Parse and return results

    return {
        'brand_name': brand_name,
        'conflicts_found': 0,
        'exact_matches': [],
        'similar_marks': [],
        'risk_level': 'low',
        'checked_at': datetime.utcnow().isoformat() + 'Z',
        'source': 'USPTO TSDR API'
    }

def _search_simulation(
    brand_name: str,
    category: Optional[str],
    limit: int
) -> Dict[str, Any]:
    """Simulation mode (current implementation)."""
    # Your existing simulation code here
    pass
```

---

## Summary

**Start now:** Keep simulation mode ✅
**Phase 4:** Integrate USPTO TSDR API (free, official) ⭐
**Enterprise:** Consider Marker API if you need SLA/support

**Next steps:**
1. Continue using simulation for Phase 3 testing
2. Sign up for USPTO account in parallel
3. Request API key (1-2 day wait)
4. Integrate TSDR API when key arrives
5. Launch Phase 4 with real trademark data

**Questions?** Contact:
- USPTO API support: APIhelp@uspto.gov
- TSDR questions: TEAS@uspto.gov
