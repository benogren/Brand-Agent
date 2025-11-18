# AI Brand Studio - Quick Start Guide

🚀 **Your environment is already set up and ready to use!**

## ✅ Pre-Setup Complete

You already have:
- ✅ Python 3.14.0 installed
- ✅ Virtual environment (`venv/`) created
- ✅ All dependencies installed
- ✅ `.env` file configured with Google API key
- ✅ All Phase 2 features tested and working
- ✅ **NEW: Interactive Phase 3 workflow with selective validation**

## 🆕 What's New in Phase 3?

The Brand Agent now features an **interactive 3-phase workflow**:

1. **Generate 20 names** - AI creates initial brand candidates
2. **Select 5-10 favorites** - You pick the names you like
3. **Validate selected only** - Domain, trademark, SEO checks run ONLY on your picks
4. **Regenerate if needed** - Not satisfied? Try again with context preserved

**Why this matters:**
- 🚀 **70% faster** - Validate only what you care about (5-10 names vs 20)
- 💰 **70% cheaper** - Fewer API calls (15-30 vs 90)
- ♻️ **Iterative** - Regenerate with your context preserved
- 🎯 **User-driven** - You control what gets validated

📖 **[See full workflow documentation](INTERACTIVE_WORKFLOW.md)**

## Running the Application

### 1. Activate Virtual Environment

```bash
cd /Users/benogren/Desktop/projects/Brand-Agent
source venv/bin/activate
```

### 2. Verify Everything Works

```bash
# Run comprehensive Phase 2 tests
python test_phase2.py
```

Expected: All 7 features passing ✅

### 3. Generate Brand Names (Interactive Mode - RECOMMENDED)

#### The New Way: Interactive 3-Phase Workflow

```bash
python -m src.cli
```

**What happens:**

**Phase 1 - Generate:**
```
Generating 20 brand names...

GENERATED BRAND NAMES (20 total)
======================================================================
 1. MealMind             - Intelligent meal planning...
 2. NutriNest            - Warm, family-oriented brand...
 3. Yumora               - Brings joy to mealtime...
 ...
 20. KitchenIQ          - Smart kitchen solutions...
```

**Phase 2 - Select:**
```
SELECT YOUR FAVORITE NAMES (5-10 names)
======================================================================
Enter the numbers of your favorite names (comma-separated)
Example: 1,5,7,12,18
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

**Phase 3 - Validate:**
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

[Results for other 4 names...]

VALIDATION RESULTS
======================================================================
[Detailed breakdown with domain, trademark, SEO for each name]

Are you satisfied with these results? (y/n/regenerate):
```

### 4. Alternative Usage Modes

#### Option A: Direct Command-Line (Still Interactive)

```bash
# Skip the prompts, go straight to interactive workflow
python -m src.cli \
  --product "AI-powered meal planning app for busy parents" \
  --audience "Parents aged 28-40" \
  --personality professional \
  --industry food_tech
```

This will still:
- Generate 20 names
- Let you select favorites
- Validate only selected names
- Allow regeneration

#### Option B: Direct Command-Line

```bash
# Generate 30 brand names for an AI meal planning app
python -m src.cli \
  --product "AI-powered meal planning app for busy parents" \
  --audience "Parents aged 28-40" \
  --personality warm \
  --industry food_tech \
  --count 30
```

#### Option C: Quiet Mode (Names Only)

```bash
python -m src.cli \
  --product "Healthcare telemedicine app" \
  --personality professional \
  --quiet
```

#### Option D: Verbose Mode (Debugging)

```bash
python -m src.cli \
  --product "Fintech lending platform" \
  --personality innovative \
  --verbose
```

#### Option E: Save to JSON File

```bash
python -m src.cli \
  --product "E-commerce sustainable fashion marketplace" \
  --personality playful \
  --json output.json
```

## CLI Options

```
--product, -p          Product description (required in direct mode)
--audience, -a         Target audience (optional)
--personality, -P      Brand personality (playful/professional/innovative/luxury)
--industry, -i         Industry category (e.g., healthcare, fintech)
--count, -c            Number of names (20-50, default: 30)

--verbose, -v          Show detailed output
--quiet, -q            Minimal output (names only)
--json FILE            Save results to JSON file

--project-id           Google Cloud project ID (overrides .env)
--location             GCP region (default: us-central1)
```

## ✅ Phase 2 Features (All Active!)

**All features are fully operational:**

✅ **Name Generator**: Real Google AI API (Gemini 2.5 Flash) integration
✅ **Research Agent**: Industry-specific insights and trend analysis
✅ **RAG System**: Retrieves similar successful brands (31-brand dataset)
✅ **Validation Agent**: Domain availability + trademark checking
✅ **SEO Optimizer**: Meta tags, keywords, content suggestions
✅ **Brand Story Generator**: Real LLM-powered taglines & narratives
✅ **Session Management**: Tracks generation history in `.sessions/`
✅ **CLI Interface**: Interactive + command-line modes

## Testing the Code

Run the comprehensive Phase 2 test suite:

```bash
# Run all Phase 2 feature tests
python test_phase2.py

# This tests:
# - Research Agent
# - RAG Brand Retrieval
# - Validation Agent (domain + trademark)
# - SEO Optimizer
# - Brand Story Generator (real LLM)
# - Session Management
# - Integrated Name Generation
```

## Example Workflows

### Example 1: Generate Names for Healthcare App

```bash
python -m src.cli \
  --product "AI-powered telemedicine app for remote consultations with specialists" \
  --audience "Patients aged 40-65 with chronic conditions" \
  --personality professional \
  --industry healthcare \
  --count 40
```

### Example 2: Fintech Startup (Verbose)

```bash
python -m src.cli \
  --product "Peer-to-peer lending platform for small business owners" \
  --audience "Small business owners seeking working capital" \
  --personality innovative \
  --industry fintech \
  --verbose
```

### Example 3: E-commerce (Save Results)

```bash
python -m src.cli \
  --product "Sustainable fashion marketplace connecting eco-conscious shoppers with ethical brands" \
  --audience "Women aged 25-40 who value sustainability" \
  --personality playful \
  --industry e_commerce \
  --json fashion_brands.json \
  --count 50
```

## What You Get from Each Generation

Each brand name includes:

1. **Brand Name**: Creative, unique name
2. **Naming Strategy**: portmanteau, invented, descriptive, or acronym
3. **Tagline**: Marketing tagline option
4. **Rationale**: Explanation of why it works
5. **Syllables**: Phonetic complexity (1-3 ideal)
6. **Memorable Score**: Memorability rating (1-10)

## Performance Expectations

- **Name Generation**: ~10-15 seconds for 20 names
- **Validation**: ~2-3 seconds per name (domain + trademark)
- **Story Generation**: ~5-8 seconds (real LLM)
- **Full Test Suite**: ~30-40 seconds

## Advanced Features

### Session History

All generations are saved in `.sessions/` directory:

```bash
# View session statistics
ls -la .sessions/

# Recent sessions contain:
# - All generated brands
# - User interactions
# - Validation results
# - Timestamps
```

### Generate Brand Stories

Use the Story Agent to create full marketing copy:

```python
from src.agents.story_agent import StoryAgent

agent = StoryAgent(
    project_id='brand-agent-478519',
    location='us-central1'
)

story = agent.generate_brand_story(
    brand_name="YourBrand",
    product_description="What it does",
    brand_personality="innovative",
    target_audience="Who it's for"
)

# Returns:
# - 5 tagline options
# - Brand story (200-300 words)
# - Hero copy (landing page)
# - Value proposition
```

## Troubleshooting

### "Vertex AI 404 NOT_FOUND"
**This is expected!** The system automatically falls back to Google AI API. You can safely ignore this warning.

### "ModuleNotFoundError: No module named 'src'"
Make sure you're in the project root:
```bash
cd /Users/benogren/Desktop/projects/Brand-Agent
source venv/bin/activate
python -m src.cli
```

### Virtual environment not activated
```bash
source venv/bin/activate
```
You should see `(venv)` in your terminal prompt.

### Dependencies missing
```bash
pip install -r requirements.txt
```

## Quick Reference

```bash
# Get help
python -m src.cli --help

# Run tests
python test_phase2.py

# Interactive mode
python -m src.cli

# Quick generation
python -m src.cli --product "Your product" --personality innovative

# Save to file
python -m src.cli --product "Your product" --json results.json
```

## Project Structure

```
Brand-Agent/
├── src/
│   ├── agents/          # All AI agents
│   │   ├── orchestrator.py
│   │   ├── name_generator.py
│   │   ├── research_agent.py
│   │   ├── validation_agent.py
│   │   ├── seo_agent.py
│   │   └── story_agent.py
│   ├── tools/           # Utilities
│   │   ├── domain_checker.py
│   │   └── trademark_checker.py
│   ├── rag/             # RAG brand retrieval
│   ├── data/            # 31-brand dataset
│   ├── database/        # Session management
│   └── cli.py           # Main interface
├── test_phase2.py       # Comprehensive tests
├── .env                 # Your config
└── QUICKSTART.md        # This file
```

---

## 🚀 Ready to Generate Brand Names?

**Start with interactive mode:**

```bash
source venv/bin/activate
python -m src.cli
```

**Or try a quick example:**

```bash
python -m src.cli \
  --product "AI-powered productivity app" \
  --audience "Remote workers" \
  --personality innovative \
  --count 20
```

Enjoy creating amazing brands! 🎨
