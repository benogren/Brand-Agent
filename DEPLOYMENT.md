# AI Brand Studio - Deployment Guide

Complete guide for deploying AI Brand Studio to Google Cloud Platform.

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
- Python 3.9+ installed locally
- Basic understanding of Google Cloud services

## Phase 3: Production Deployment

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    VERTEX AI AGENT ENGINE                 │
│  ┌───────────────────────────────────────────────────┐   │
│  │   Orchestrator Agent (gemini-2.5-flash)          │   │
│  │   ├── Research Agent                              │   │
│  │   ├── Name Generator Agent (gemini-2.5-pro)      │   │
│  │   ├── Validation Agent                            │   │
│  │   ├── SEO Optimizer Agent                         │   │
│  │   └── Story Generator Agent (gemini-2.5-pro)     │   │
│  └───────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────┘
                 │
        ┌────────┴────────┬────────────────┬────────────┐
        ↓                 ↓                ↓            ↓
┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐
│ CLOUD SQL    │  │ VECTOR       │  │ CLOUD    │  │ CLOUD  │
│ (PostgreSQL) │  │ SEARCH       │  │ STORAGE  │  │ LOGGING│
│              │  │              │  │          │  │        │
│ - Sessions   │  │ - Brand DB   │  │ -Datasets│  │ -Traces│
│ - Events     │  │ - Embeddings │  │ - Exports│  │ -Metrics│
└──────────────┘  └──────────────┘  └──────────┘  └────────┘
```

## Step-by-Step Deployment

### Step 1: Initial Google Cloud Setup (10-15 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-username/Brand-Agent.git
cd Brand-Agent

# 2. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run GCP setup script
./scripts/setup_gcp.sh
```

This script will:
- ✅ Enable required Google Cloud APIs
- ✅ Create Cloud Storage bucket
- ✅ Set up service accounts with proper IAM roles
- ✅ Configure authentication
- ✅ Generate `.env` file

**Follow the prompts** to:
- Enter your Google Cloud Project ID
- Choose whether to create Cloud SQL instance
- Configure Secret Manager for API keys

### Step 2: Cloud SQL Database Setup (Optional, 15-20 minutes)

If you chose to set up Cloud SQL in Step 1:

```bash
# Run database migrations
./scripts/run_migrations.py
```

This creates:
- Sessions table
- Events table
- Generated brands table
- Brand stories table
- Indexes and constraints

**Note**: For Phase 2 testing, file-based session storage works fine. Cloud SQL is for production scale.

### Step 3: Vector Search Setup (30-45 minutes)

```bash
# Generate embeddings and create Vector Search index
python scripts/setup_vector_search.py
```

This script:
1. Generates embeddings for brand names dataset (31 brands + any additional)
2. Uploads embeddings to Cloud Storage
3. Creates Vertex AI Vector Search index
4. Deploys index to endpoint

**Important**: This step takes 30-45 minutes. The Vector Search index creation is asynchronous.

**What's created:**
- Embeddings file in Cloud Storage
- Vector Search index (768 dimensions)
- Index endpoint for queries
- Configuration saved to `.env`

### Step 4: Test Locally with Production Config (5 minutes)

```bash
# Ensure environment is configured
source venv/bin/activate

# Run Phase 2 tests with production config
python test_phase2.py

# Test CLI with production RAG
python -m src.cli --product "AI fitness app" --count 10
```

Verify that:
- ✅ All tests pass
- ✅ Names are generated successfully
- ✅ Domain and trademark validation works
- ✅ Cloud Logging is capturing events (check console.cloud.google.com)

### Step 5: Deploy to Vertex AI Agent Engine (10-15 minutes)

```bash
# Deploy the multi-agent system
./scripts/deploy.sh
```

This script:
1. ✅ Runs tests before deployment
2. ✅ Packages source code and dependencies
3. ✅ Deploys to Vertex AI Agent Engine
4. ✅ Creates agent endpoint
5. ✅ Tests deployed agent

**Deployment config** (`.agent_engine_config.json`):
- Min instances: 0 (scale to zero)
- Max instances: 5 (auto-scaling)
- Resources: 2 CPU, 4GB memory
- Timeout: 600s (10 minutes)

### Step 6: Test Deployed Agent (5 minutes)

```bash
# Test via gcloud CLI
gcloud ai agents query brand_studio_agent \
  --region=us-central1 \
  --query="I need a brand name for an AI-powered fitness app for millennials"

# View deployment info
cat deployment/deployment_info.json
```

Expected response:
```json
{
  "brand_names": ["FitGenius", "PulsAI", "TrainSmart", ...],
  "validation_results": {...},
  "seo_data": {...},
  "brand_story": {...}
}
```

### Step 7: Run Evaluation Suite (10 minutes)

```bash
# Run comprehensive evaluation tests
adk eval brand_studio_agent tests/integration.evalset.json \
  --config_file_path=tests/eval_config.json \
  --print_detailed_results
```

This runs 12 test cases covering:
- Healthcare apps
- Fintech platforms
- E-commerce SaaS
- Consumer apps
- B2B services

**Success criteria:**
- ✅ 80%+ test cases passing
- ✅ Average name quality score >75/100
- ✅ Domain availability >50%
- ✅ Response time <2 minutes

### Step 8: Monitor and Observe (Ongoing)

#### Cloud Logging

View logs in real-time:

```bash
# View agent logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Agent" \
  --limit=50 \
  --format=json

# View specific events
gcloud logging read "jsonPayload.event_type=agent_event" \
  --limit=20
```

Or use **Cloud Console**:
https://console.cloud.google.com/logs/query?project=YOUR_PROJECT_ID

#### Cloud Monitoring

Set up monitoring dashboards:

1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Create dashboard for:
   - Request count
   - Response latency (p50, p95, p99)
   - Error rate
   - Agent utilization

#### Cost Monitoring

Set up billing alerts:

```bash
# Create billing alert at $10
gcloud alpha billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Brand Studio Budget" \
  --budget-amount=10USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

## Deployment Checklist

### Pre-Deployment
- [ ] Google Cloud project created
- [ ] Billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Repository cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)

### Phase 1: Infrastructure
- [ ] `setup_gcp.sh` completed successfully
- [ ] APIs enabled (Vertex AI, Cloud SQL, Storage, Logging)
- [ ] Service account created with proper roles
- [ ] Cloud Storage bucket created
- [ ] `.env` file generated with correct values

### Phase 2: Database & Storage
- [ ] Cloud SQL instance created (optional)
- [ ] Database migrations run
- [ ] Tables and indexes created
- [ ] Brand dataset uploaded to Cloud Storage

### Phase 3: Vector Search
- [ ] Embeddings generated for brand dataset
- [ ] Embeddings uploaded to Cloud Storage
- [ ] Vector Search index created
- [ ] Index endpoint deployed
- [ ] `.env` updated with endpoint info

### Phase 4: Testing
- [ ] Local tests passing (`python test_phase2.py`)
- [ ] CLI working with production config
- [ ] Cloud Logging capturing events
- [ ] Domain/trademark validation working

### Phase 5: Deployment
- [ ] `deploy.sh` completed successfully
- [ ] Agent deployed to Vertex AI Agent Engine
- [ ] Deployment endpoint URL obtained
- [ ] Test query successful
- [ ] `deployment_info.json` created

### Phase 6: Validation
- [ ] Evaluation suite run (`adk eval`)
- [ ] 80%+ test cases passing
- [ ] Monitoring dashboards configured
- [ ] Billing alerts set up
- [ ] Documentation complete

## Common Issues & Troubleshooting

### Issue: "Permission denied" during deployment

**Solution:**
```bash
# Ensure you have proper permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/aiplatform.admin
```

### Issue: Vector Search index creation timeout

**Solution:**
- Vector Search index creation is asynchronous and takes 30-45 minutes
- Check status in Cloud Console: https://console.cloud.google.com/vertex-ai/matching-engine
- Script will wait automatically, but you can check manually:

```bash
gcloud ai indexes list --region=us-central1
```

### Issue: Cloud SQL connection failed

**Solution:**
```bash
# Ensure Cloud SQL Proxy is configured
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# Or use Unix socket path in DATABASE_URL
export DATABASE_URL="postgresql://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

### Issue: Agent deployment fails

**Solution:**
- Check `.agent_engine_config.json` is valid JSON
- Ensure all dependencies in `requirements.txt`
- Verify service account has `roles/aiplatform.user`
- Check logs:

```bash
gcloud logging read "resource.type=aiplatform.googleapis.com" --limit=50
```

### Issue: High costs

**Solution:**
- Set `min_instances: 0` in `.agent_engine_config.json` (scale to zero)
- Use `gemini-2.5-flash` for most agents (cheaper than Pro)
- Enable request caching
- Monitor costs: https://console.cloud.google.com/billing

## Production Optimization

### Performance

1. **Caching**: Enable response caching for repeated queries
2. **Batching**: Batch domain/trademark checks
3. **Async Processing**: Use async for validation agent
4. **Connection Pooling**: Use pgBouncer for Cloud SQL

### Security

1. **API Keys**: Store in Secret Manager (not `.env`)
2. **Authentication**: Enable Cloud IAM authentication
3. **Rate Limiting**: Implement request throttling
4. **Input Validation**: Sanitize user inputs

### Scaling

1. **Auto-scaling**: Adjust max_instances based on load
2. **Read Replicas**: Add Cloud SQL read replicas for analytics
3. **CDN**: Use Cloud CDN for static assets
4. **Multi-region**: Deploy to multiple regions for HA

## Cost Estimation

### Free Tier (First Month)
- Vertex AI Agent Engine: 10 agents free
- Cloud SQL: f1-micro instance free (us-central1)
- Cloud Storage: 5 GB free
- Cloud Logging: 50 GB free

### Expected Monthly Costs (100 generations/month)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Gemini 2.5 Flash | 500K tokens | ~$1.25 |
| Gemini 2.5 Pro | 100K tokens | ~$2.50 |
| Vector Search | 1M queries | $0.00 (free tier) |
| Cloud SQL | f1-micro | $0.00 (free tier) |
| Cloud Storage | 2 GB | $0.00 (free tier) |
| Cloud Logging | 10 GB | $0.00 (free tier) |
| **Total** | | **~$4-5/month** |

### Scale Pricing (1000 generations/month)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Gemini Models | 5M tokens | ~$35 |
| Vector Search | 10M queries | ~$10 |
| Cloud SQL | db-n1-standard-1 | ~$50 |
| Cloud Storage | 20 GB | ~$0.50 |
| **Total** | | **~$95/month** |

## Next Steps

After deployment:

1. **Create Demo Video**: Record 3-minute demo showing features
2. **Update README**: Add deployment badge and production URL
3. **Write Blog Post**: Share your experience
4. **Submit to Kaggle**: Submit for capstone evaluation
5. **Monitor & Iterate**: Watch metrics, improve based on usage

## Resources

- [Vertex AI Agent Engine Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Vector Search Guide](https://cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Cloud SQL PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Cloud Logging](https://cloud.google.com/logging/docs)
- [Gemini API Pricing](https://ai.google.dev/pricing)

---

**Deployment Status**: Ready for production! 🚀

For questions or issues, open an issue on GitHub or check the troubleshooting section above.
