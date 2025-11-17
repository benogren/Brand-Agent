# .env File Setup Guide

This guide explains how to fill out your `.env` file for different scenarios.

## Quick Setup for Local Testing (Phase 1)

For **Phase 1 local testing without Google Cloud**, you only need these minimal settings:

```bash
# Google Cloud Configuration (use test values for local testing)
GOOGLE_CLOUD_PROJECT=test-project-local
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1

# Application Settings (these work as-is)
LOG_LEVEL=INFO
ENABLE_TRACING=false
MAX_NAME_CANDIDATES=50
MIN_NAME_CANDIDATES=20
MAX_LOOP_ITERATIONS=3
DOMAIN_CACHE_TTL_SECONDS=300
```

**Everything else can be left empty or commented out for Phase 1!**

---

## Full Setup for Production (Phase 2+)

### 1. Google Cloud Project (REQUIRED for real LLM calls)

```bash
GOOGLE_CLOUD_PROJECT=your-actual-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
```

**How to get your Google Cloud Project ID:**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Copy the Project ID (not the project name!)
4. Paste it in the `.env` file

**Or use command line:**
```bash
# Create new project
gcloud projects create my-brand-studio

# Get project ID
gcloud projects list

# Set in .env
GOOGLE_CLOUD_PROJECT=my-brand-studio
```

### 2. Database Configuration (Optional for Phase 1)

**For local PostgreSQL:**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/brandstudio
```

**For Cloud SQL:**
```bash
# First, get your Cloud SQL instance connection name:
gcloud sql instances describe brandstudio-db --format="value(connectionName)"

# Then use it in the URL:
DATABASE_URL=postgresql://user:password@/brandstudio?host=/cloudsql/PROJECT:REGION:INSTANCE
```

**Skip this for Phase 1** - database features aren't used yet.

### 3. Vector Search (Phase 2 - RAG Implementation)

```bash
VECTOR_SEARCH_INDEX_ENDPOINT=projects/YOUR_PROJECT/locations/us-central1/indexEndpoints/ENDPOINT_ID
VECTOR_SEARCH_DEPLOYED_INDEX_ID=brand_names_deployed
```

**How to get these values:**
- These are created in Phase 2, Task 7.0
- Run `./scripts/setup_vector_search.py` (created in Task 7.3)
- Copy the endpoint ID from the output

**Skip this for Phase 1** - RAG features not implemented yet.

### 4. External API Keys (Optional)

All of these are **OPTIONAL**. The system uses free alternatives if not provided:

#### Namecheap API (for domain checking)
```bash
NAMECHEAP_API_KEY=your-namecheap-api-key
```
- Sign up at [Namecheap](https://www.namecheap.com)
- Enable API access in your account
- **If not provided:** Uses python-whois library (works fine!)

#### USPTO API (for trademark search)
```bash
USPTO_API_KEY=your-uspto-api-key
```
- Register at [USPTO Developer Portal](https://developer.uspto.gov)
- **If not provided:** Uses public USPTO TESS API (works fine!)

#### Social Media APIs (for handle checking)
```bash
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
INSTAGRAM_API_KEY=your-instagram-api-key
LINKEDIN_API_KEY=your-linkedin-api-key
```
- **Twitter/X:** Get from [Twitter Developer Portal](https://developer.twitter.com)
- **Instagram:** Get from [Meta Developers](https://developers.facebook.com)
- **LinkedIn:** Get from [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- **If not provided:** Falls back to web scraping (limited functionality)

**Skip all of these for Phase 1** - these tools aren't implemented yet.

### 5. Application Settings (Use defaults)

These are already set correctly in `.env.example`:

```bash
LOG_LEVEL=INFO                    # INFO, DEBUG, WARNING, ERROR
ENABLE_TRACING=true              # Enable Cloud Trace (only works with GCP)
MAX_NAME_CANDIDATES=50           # Maximum names to generate
MIN_NAME_CANDIDATES=20           # Minimum names to generate
MAX_LOOP_ITERATIONS=3            # Max validation retry loops
DOMAIN_CACHE_TTL_SECONDS=300     # Cache domain checks for 5 minutes
```

---

## Current Setup Steps (Phase 1)

Here's what you should do **right now** to run the project locally:

### Step 1: Edit your .env file

```bash
# Open in your editor
code .env
# or
nano .env
```

### Step 2: Replace the content with this minimal config:

```bash
# Google Cloud Configuration (test values for local Phase 1)
GOOGLE_CLOUD_PROJECT=test-project-local
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1

# Application Settings (keep defaults)
LOG_LEVEL=INFO
ENABLE_TRACING=false
MAX_NAME_CANDIDATES=50
MIN_NAME_CANDIDATES=20
MAX_LOOP_ITERATIONS=3
DOMAIN_CACHE_TTL_SECONDS=300
```

### Step 3: Save and test

```bash
# Test that it works
python -m src.cli --help
```

---

## When to Update .env

### After Creating Google Cloud Project:
1. Create GCP project: `gcloud projects create my-brand-studio`
2. Update `GOOGLE_CLOUD_PROJECT=my-brand-studio`
3. Authenticate: `gcloud auth application-default login`

### After Setting Up Cloud SQL (Phase 1, Task 1.5):
1. Run `./scripts/setup_cloud_sql.sh`
2. Copy the connection details to `DATABASE_URL`

### After Creating Vector Search Index (Phase 2, Task 7.0):
1. Run `./scripts/setup_vector_search.py`
2. Copy endpoint ID to `VECTOR_SEARCH_INDEX_ENDPOINT`

### When Adding External APIs (Optional):
1. Get API keys from respective services
2. Add to `.env` file
3. These are stored in Secret Manager in production

---

## Security Notes

⚠️ **NEVER commit .env to git!**
- The `.env` file is in `.gitignore`
- Use `.env.example` as a template
- Store real API keys in Google Cloud Secret Manager for production

✅ **Safe to commit:**
- `.env.example` (template with no real values)
- `ENV_SETUP_GUIDE.md` (this file)
- Code that reads from environment variables

❌ **Never commit:**
- `.env` (your actual environment variables)
- Any files with real API keys or passwords

---

## Troubleshooting

### "GOOGLE_CLOUD_PROJECT environment variable is required"

**Solution:** Add this to `.env`:
```bash
GOOGLE_CLOUD_PROJECT=test-project-local
```

### "Could not automatically determine credentials"

**For Phase 1 (placeholder mode):** This is fine! The CLI will use placeholder data.

**For Phase 2 (real LLM calls):** Run:
```bash
gcloud auth application-default login
```

### "Database connection failed"

**For Phase 1:** Comment out `DATABASE_URL` - database features aren't used yet.

**For Phase 2:** Verify your Cloud SQL instance is running:
```bash
gcloud sql instances list
```

---

## Quick Reference

### Minimal .env (Phase 1 - Local Testing)
```bash
GOOGLE_CLOUD_PROJECT=test-project-local
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
LOG_LEVEL=INFO
```

### Full .env (Phase 2+ - Production Ready)
```bash
GOOGLE_CLOUD_PROJECT=my-real-gcp-project
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
DATABASE_URL=postgresql://user:pass@localhost:5432/brandstudio
VECTOR_SEARCH_INDEX_ENDPOINT=projects/.../indexEndpoints/...
VECTOR_SEARCH_DEPLOYED_INDEX_ID=brand_names_deployed
LOG_LEVEL=INFO
ENABLE_TRACING=true
```

---

**For now, just use the minimal Phase 1 config and you're good to go!** 🚀
