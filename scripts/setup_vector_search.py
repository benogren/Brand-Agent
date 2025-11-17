#!/usr/bin/env python3
"""
Setup Vertex AI Vector Search for AI Brand Studio.

This script:
1. Generates embeddings for brand names dataset
2. Creates Vector Search index
3. Deploys index to endpoint
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

# Load environment
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_embeddings(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Generate embeddings for brand names dataset.

    Args:
        dataset_path: Path to brand names JSON file

    Returns:
        List of dictionaries with embeddings and metadata
    """
    logger.info(f"Loading dataset from {dataset_path}")

    with open(dataset_path, 'r') as f:
        brands = json.load(f)

    logger.info(f"Loaded {len(brands)} brands")

    # Initialize embedding model
    logger.info("Initializing text embedding model...")
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    # Generate embeddings in batches
    batch_size = 250  # API limit
    embeddings_data = []

    for i in range(0, len(brands), batch_size):
        batch = brands[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(brands)-1)//batch_size + 1}")

        # Create text for embedding (brand name + description)
        texts = [
            f"{brand['brand_name']} {brand.get('description', '')} {brand.get('category', '')}"
            for brand in batch
        ]

        # Get embeddings
        try:
            embeddings = model.get_embeddings(texts)

            for brand, embedding in zip(batch, embeddings):
                embeddings_data.append({
                    "id": brand['brand_name'].lower().replace(' ', '_'),
                    "embedding": embedding.values,
                    "metadata": {
                        "brand_name": brand['brand_name'],
                        "industry": brand.get('industry', ''),
                        "category": brand.get('category', ''),
                        "naming_strategy": brand.get('naming_strategy', ''),
                        "year_founded": brand.get('year_founded', 0),
                        "description": brand.get('description', '')
                    }
                })
        except Exception as e:
            logger.error(f"Error generating embeddings for batch: {e}")
            continue

    logger.info(f"Generated {len(embeddings_data)} embeddings")
    return embeddings_data


def save_embeddings_for_vector_search(embeddings_data: List[Dict], output_path: str):
    """
    Save embeddings in JSONL format for Vector Search.

    Args:
        embeddings_data: List of embedding dictionaries
        output_path: Path to save JSONL file
    """
    logger.info(f"Saving embeddings to {output_path}")

    with open(output_path, 'w') as f:
        for item in embeddings_data:
            # Format for Vector Search
            record = {
                "id": item['id'],
                "embedding": item['embedding'],
                **item['metadata']  # Flatten metadata into main object
            }
            f.write(json.dumps(record) + '\n')

    logger.info(f"Saved {len(embeddings_data)} embeddings")


def upload_to_gcs(local_file: str, bucket_name: str, blob_name: str):
    """Upload file to Google Cloud Storage."""
    from google.cloud import storage

    logger.info(f"Uploading {local_file} to gs://{bucket_name}/{blob_name}")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(local_file)

    logger.info(f"✓ Uploaded to gs://{bucket_name}/{blob_name}")
    return f"gs://{bucket_name}/{blob_name}"


def create_vector_search_index(
    project_id: str,
    location: str,
    gcs_path: str,
    display_name: str = "brand-names-index"
) -> aiplatform.MatchingEngineIndex:
    """
    Create Vertex AI Vector Search index.

    Args:
        project_id: GCP project ID
        location: GCP region
        gcs_path: GCS path to embeddings JSONL file
        display_name: Index display name

    Returns:
        Created MatchingEngineIndex
    """
    logger.info(f"Creating Vector Search index: {display_name}")

    aiplatform.init(project=project_id, location=location)

    # Create index
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        contents_delta_uri=gcs_path,
        dimensions=768,  # text-embedding-004 dimension
        approximate_neighbors_count=50,
        distance_measure_type="DOT_PRODUCT_DISTANCE",
        leaf_node_embedding_count=1000,
        leaf_nodes_to_search_percent=10,
        description="Brand names vector search index for AI Brand Studio",
        labels={"app": "brand-studio", "version": "1.0"}
    )

    logger.info(f"✓ Index created: {index.resource_name}")
    return index


def create_index_endpoint(
    project_id: str,
    location: str,
    display_name: str = "brand-names-endpoint"
) -> aiplatform.MatchingEngineIndexEndpoint:
    """
    Create Vector Search index endpoint.

    Args:
        project_id: GCP project ID
        location: GCP region
        display_name: Endpoint display name

    Returns:
        Created MatchingEngineIndexEndpoint
    """
    logger.info(f"Creating index endpoint: {display_name}")

    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name,
        description="Index endpoint for brand names search",
        public_endpoint_enabled=True,
        labels={"app": "brand-studio", "version": "1.0"}
    )

    logger.info(f"✓ Endpoint created: {endpoint.resource_name}")
    return endpoint


def deploy_index(
    index: aiplatform.MatchingEngineIndex,
    endpoint: aiplatform.MatchingEngineIndexEndpoint,
    deployed_index_id: str = "brand_names_deployed"
):
    """
    Deploy index to endpoint.

    Args:
        index: MatchingEngineIndex to deploy
        endpoint: MatchingEngineIndexEndpoint to deploy to
        deployed_index_id: ID for deployed index
    """
    logger.info(f"Deploying index to endpoint...")
    logger.info("This may take 10-15 minutes...")

    endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        display_name=deployed_index_id,
        machine_type="e2-standard-2",
        min_replica_count=1,
        max_replica_count=1
    )

    logger.info(f"✓ Index deployed with ID: {deployed_index_id}")


def main():
    """Main setup flow."""
    print("\n" + "=" * 70)
    print("AI Brand Studio - Vector Search Setup")
    print("=" * 70 + "\n")

    # Get configuration
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT not set. Please run setup_gcp.sh first.")
        sys.exit(1)

    logger.info(f"Project: {project_id}")
    logger.info(f"Location: {location}")

    # Paths
    dataset_path = "src/data/brand_names_dataset.py"
    embeddings_output = "data/brand_embeddings.jsonl"
    bucket_name = f"{project_id}-brand-studio"
    gcs_blob_name = "embeddings/brand_embeddings.jsonl"

    # Check if dataset exists
    if not os.path.exists("src/data/brand_names_dataset.py"):
        logger.error("Brand dataset not found. Please ensure src/data/brand_names_dataset.py exists.")
        sys.exit(1)

    # Step 1: Generate embeddings
    print("\nStep 1: Generating embeddings...")
    print("-" * 70)

    # Import dataset
    from src.data.brand_names_dataset import BRAND_NAMES_DATASET

    # Save dataset as JSON temporarily
    temp_dataset_path = "data/brands_temp.json"
    os.makedirs("data", exist_ok=True)
    with open(temp_dataset_path, 'w') as f:
        json.dump(BRAND_NAMES_DATASET, f)

    embeddings_data = generate_embeddings(temp_dataset_path)

    # Step 2: Save in Vector Search format
    print("\nStep 2: Saving embeddings...")
    print("-" * 70)
    save_embeddings_for_vector_search(embeddings_data, embeddings_output)

    # Step 3: Upload to GCS
    print("\nStep 3: Uploading to Cloud Storage...")
    print("-" * 70)
    gcs_path = upload_to_gcs(embeddings_output, bucket_name, gcs_blob_name)

    # Step 4: Create Vector Search index
    print("\nStep 4: Creating Vector Search index...")
    print("-" * 70)
    print("This may take 30-45 minutes...")

    try:
        index = create_vector_search_index(
            project_id=project_id,
            location=location,
            gcs_path=f"gs://{bucket_name}/embeddings/"
        )
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        logger.info("You can create it manually via Cloud Console")
        sys.exit(1)

    # Step 5: Create endpoint
    print("\nStep 5: Creating index endpoint...")
    print("-" * 70)

    try:
        endpoint = create_index_endpoint(project_id, location)
    except Exception as e:
        logger.error(f"Error creating endpoint: {e}")
        sys.exit(1)

    # Step 6: Deploy index
    print("\nStep 6: Deploying index to endpoint...")
    print("-" * 70)

    try:
        deploy_index(index, endpoint)
    except Exception as e:
        logger.error(f"Error deploying index: {e}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 70)
    print("Vector Search Setup Complete!")
    print("=" * 70 + "\n")

    print("Update your .env file with:")
    print(f"VECTOR_SEARCH_INDEX_ENDPOINT={endpoint.resource_name}")
    print("VECTOR_SEARCH_DEPLOYED_INDEX_ID=brand_names_deployed")
    print()

    # Cleanup
    os.remove(temp_dataset_path)

    print("✓ Setup complete!")


if __name__ == "__main__":
    main()
