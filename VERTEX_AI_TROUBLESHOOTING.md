# Vertex AI Gemini Access Troubleshooting

You're getting a 404 error when trying to access Gemini models in Vertex AI. This guide will help you resolve it.

## Problem

```
404 Publisher Model `projects/brand-agent-478519/locations/us-central1/publishers/google/models/gemini-1.5-flash` was not found or your project does not have access to it.
```

## Solutions (Try in Order)

### Option 1: Enable Vertex AI Generative AI API (Recommended)

The standard Vertex AI API may not include access to Gemini models. You need to explicitly enable the generative AI features:

```bash
# Enable the Vertex AI Vision API (includes Gemini access)
gcloud services enable aiplatform.googleapis.com \
  --project=brand-agent-478519

# Also enable the Generative Language API
gcloud services enable generativelanguage.googleapis.com \
  --project=brand-agent-478519

# Wait 2-3 minutes for APIs to fully propagate
```

After running these commands, wait 2-3 minutes and try again.

### Option 2: Request Gemini Access (If Still 404)

Some Gemini models require allowlisting. Request access here:
https://console.cloud.google.com/vertex-ai/generative/language

1. Go to the Vertex AI > Generative AI Studio in Google Cloud Console
2. Click "Enable" on any Gemini model cards
3. Accept terms of service if prompted
4. Wait 5-10 minutes for access to be granted

### Option 3: Try a Different Region

Some models are only available in specific regions:

Update your `.env` file:
```bash
# Try us-central1 (you're already using this)
GOOGLE_CLOUD_LOCATION=us-central1

# Or try us-west1
# GOOGLE_CLOUD_LOCATION=us-west1

# Or try europe-west1
# GOOGLE_CLOUD_LOCATION=europe-west1
```

### Option 4: Use Google AI API (Easiest Workaround)

Instead of Vertex AI, use the Google AI API which requires just an API key (no project setup):

1. Get an API key from Google AI Studio:
   - Go to: https://aistudio.google.com/apikey
   - Click "Create API Key"
   - Copy the key

2. Add to your `.env` file:
   ```bash
   GOOGLE_API_KEY=your-api-key-here
   ```

3. The code will automatically fall back to Google AI API when Vertex AI fails.

**Note:** Google AI API is free for development but has rate limits.

## Verify Access

After trying any solution, test with:

```bash
# Test Vertex AI access
python -c "from google import genai; client = genai.Client(vertexai=True, project='brand-agent-478519', location='us-central1'); print('Success!')"

# Or test Google AI API
python -c "from google import genai; import os; client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY')); print('Success!')"
```

## Current Status

- ✅ Billing enabled: Yes
- ✅ Project ID: brand-agent-478519
- ✅ Vertex AI API enabled: Yes
- ✅ Generative Language API enabled: Yes
- ❌ Gemini model access: **NOT YET** (getting 404)

## Recommended Next Step

**Try Option 4 (Google AI API) first** - it's the fastest way to get real LLM generation working:

1. Go to https://aistudio.google.com/apikey
2. Create an API key
3. Add `GOOGLE_API_KEY=your-key` to `.env`
4. Run the CLI again

The code will automatically use Google AI API as a fallback when Vertex AI isn't available.
