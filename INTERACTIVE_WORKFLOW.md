# Interactive Phase 3 Workflow

## Overview

The Brand Agent now features an interactive 3-phase workflow that makes the brand name generation process more efficient and user-friendly.

## Why This Change?

Previously, Phase 3 validation (domain checks, trademark searches, SEO optimization) ran on ALL generated names, which was:
- Time-consuming (checking 20-30 names takes significant time)
- Expensive (multiple API calls per name)
- Wasteful (users might only like a few names anyway)

**New Approach**: Generate names first, let users pick their favorites, then validate only those selections.

## Workflow Steps

### Phase 1: Name Generation
```
Generate 20 brand names
↓
Display in simple list format
```

**What happens:**
- System generates 20 brand names using AI
- Names are displayed with brief rationales
- No validation yet - just creative generation

**Example output:**
```
GENERATED BRAND NAMES (20 total)
======================================================================

 1. MealMind             - Combines "Meal" and "Mind" to suggest intelligent ...
 2. NutriNest            - Nutrition + Nest creates a warm, family-oriented b...
 3. Yumora               - Invented name suggesting yum + aura, brings joy to...
...
```

### Phase 2: User Selection
```
User reviews 20 names
↓
Selects 5-10 favorites
↓
Confirms selection OR regenerates
```

**What happens:**
- User enters comma-separated numbers (e.g., `1,5,7,12,18`)
- System validates selection (must pick 5-10 names)
- User confirms or re-selects
- Option to type `regenerate` to get 20 new names

**Example interaction:**
```
SELECT YOUR FAVORITE NAMES (5-10 names)
======================================================================

Enter the numbers of your favorite names (comma-separated)
Example: 1,5,7,12,18
Or type 'all' to select all names
Or type 'regenerate' to start over with new names

Your selection (5-10 names): 1,2,5,7,12

You selected 5 names:
  - MealMind
  - NutriNest
  - PlateWise
  - FamilyFeast
  - KitchenIQ

Confirm selection? (y/n): y
```

### Phase 3: Validation & Optimization
```
Run validation on selected names only
↓
- Domain availability (.com, .ai, .io)
- Trademark risk assessment (USPTO)
- SEO optimization (meta tags, keywords)
- Enhanced taglines
↓
Display detailed results
↓
User accepts OR regenerates
```

**What happens:**
- Domain checker: Verify `.com`, `.ai`, `.io` availability
- Trademark checker: Search USPTO database for conflicts
- SEO agent: Generate meta titles, descriptions, keyword strategies
- Results displayed in detailed format

**Example output:**
```
PHASE 3: VALIDATING SELECTED NAMES
======================================================================

[1/5] Validating: MealMind
----------------------------------------------------------------------
  Checking domain availability...
  Checking trademark conflicts...
  Optimizing for SEO...
  ✓ Domains available: mealmind.com, mealmind.ai, mealmind.io
  ✓ Trademark risk: low
  ✓ SEO score: 87/100

...

VALIDATION RESULTS
======================================================================

MealMind
----------------------------------------------------------------------
Domain Availability:
  mealmind.com         ✓ Available
  mealmind.ai          ✓ Available
  mealmind.io          ✓ Available

Trademark Risk: ✓ LOW
  Conflicts found: 0

SEO Score: 87/100
Meta Title: MealMind - AI meal planning app | Food Tech
Meta Description: MealMind: AI meal planning app for busy parents
Primary Keywords: meal, planning, parents, food_tech

Tagline: "Smart planning for busy families"
```

### Phase 4: Final Decision
```
User reviews results
↓
Satisfied? (y/n/regenerate)
↓
YES: Complete ✓
NO/REGENERATE: Loop back to Phase 1
```

**What happens:**
- User can accept results
- User can regenerate with same context (product brief preserved)
- Process repeats until user is satisfied

## Usage Examples

### Command Line
```bash
# Interactive mode
python -m src.cli

# Direct input
python -m src.cli --product "AI meal planning app" --audience "Busy parents" --personality professional
```

### Interactive Session
```bash
$ python -m src.cli

======================================================================
AI BRAND STUDIO - INTERACTIVE MODE
======================================================================

Product description (what does it do?): AI meal planning app
Target audience (who is it for?) [optional]: Busy parents
Brand personality options:
  1. Playful (fun, whimsical, lighthearted)
  2. Professional (authoritative, trustworthy)
  3. Innovative (forward-thinking, tech-savvy)
  4. Luxury (elegant, sophisticated, premium)
Select personality (1-4) [default: 2]: 2
Industry/category [default: general]: food_tech

# System generates 20 names...
# User selects 5-10 favorites...
# System validates selected names...
# User accepts or regenerates...
```

## Key Features

### 1. Context Preservation
When you regenerate, the system remembers:
- Your product description
- Target audience
- Brand personality
- Industry

This ensures consistency across regenerations.

### 2. Selective Validation
Only selected names are validated, which means:
- Faster results (validate 5-10 instead of 20)
- Lower costs (fewer API calls)
- Better user experience (see results for names you care about)

### 3. Iterative Refinement
You can regenerate as many times as needed:
```
Generate → Select → Validate → Not satisfied? → Regenerate
```

## Benefits

| Old Workflow | New Workflow |
|--------------|--------------|
| Generate 30 names | Generate 20 names |
| Validate ALL 30 | User selects 5-10 |
| Wait for all results | Validate selected only |
| Take it or leave it | Regenerate with context |
| ~30 domain checks | ~5-10 domain checks |
| ~30 trademark searches | ~5-10 trademark searches |
| **Slower, expensive** | **Faster, efficient** |

## Technical Details

### Functions Added to `src/cli.py`

1. **`print_brand_names_simple(names)`**
   - Displays names in compact format for selection
   - Shows name + brief rationale

2. **`get_user_selection(names, min_select, max_select)`**
   - Interactive selection interface
   - Validates user input
   - Supports regeneration trigger

3. **`run_phase3_validation(config, selected_names, brief, verbose)`**
   - Runs domain availability checks
   - Performs trademark searches
   - Optimizes SEO
   - Returns comprehensive results

4. **`print_validation_results(validation_results)`**
   - Formats and displays validation data
   - Shows domain status, trademark risk, SEO scores
   - Easy-to-read output with symbols (✓, ✗, ⚠)

### Modified Functions

1. **`main()`**
   - Implements interactive loop
   - Handles regeneration flow
   - Manages context preservation

## Future Enhancements

Potential improvements for later:
- Save favorite names across sessions
- Compare multiple validation results side-by-side
- Filter names by criteria (e.g., "show only names with .com available")
- Export validation reports to PDF
- Integration with domain registrars for instant purchase
- Real-time trademark monitoring

## Troubleshooting

### "Please select at least 5 names"
You must select between 5-10 names. Enter more numbers.

### "Numbers must be between 1 and 20"
Check that your selected numbers match the displayed list.

### "No brand names generated"
Check your internet connection and API credentials.

### Want to skip selection and validate all?
Type `all` when prompted for selection.

### Want to start over completely?
Type `regenerate` when prompted for selection.

## Support

For issues or questions:
- Check logs: `.sessions/` directory
- Review `.env` configuration
- Ensure API credentials are set
- Run with `--verbose` flag for detailed output
