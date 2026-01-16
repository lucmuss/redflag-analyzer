"""
Database Seeding Script
Imports questions from JSON file into MongoDB
Usage: python -m scripts.seed_db
"""
import sys
import os
import json
import asyncio
import math
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_old_weight(weight: int) -> int:
    """
    Convert old 1-10 weight scale to new 1-5 scale
    Formula: ceil(weight / 2)
    """
    if weight < 1 or weight > 10:
        logger.warning(f"Weight {weight} out of range, clamping to 1-10")
        weight = max(1, min(10, weight))
    return math.ceil(weight / 2)


async def seed_questions():
    """Import questions from JSON file into MongoDB"""
    
    # Load questions from JSON
    json_path = Path(__file__).parent.parent.parent / "seed_data" / "questions.json"
    
    if not json_path.exists():
        logger.error(f"Questions file not found at {json_path}")
        return False
    
    logger.info(f"Loading questions from {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    logger.info(f"Loaded {len(questions_data)} questions")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
        # Process and upsert questions
        inserted = 0
        updated = 0
        errors = 0
        
        for q_data in questions_data:
            try:
                # Validate required fields
                if 'key' not in q_data or 'category' not in q_data:
                    logger.error(f"Missing required fields in question: {q_data}")
                    errors += 1
                    continue
                
                # Convert weight if needed (1-10 scale to 1-5)
                initial_weight = q_data.get('initial_weight', 3)
                if initial_weight > 5:
                    default_weight = convert_old_weight(initial_weight)
                    logger.info(f"Converted weight for '{q_data['key']}': {initial_weight} -> {default_weight}")
                else:
                    default_weight = initial_weight
                
                # Prepare document (only store key, category, default_weight)
                # Text translations are stored in Flutter app, not in backend
                question_doc = {
                    "key": q_data['key'],
                    "category": q_data['category'],
                    "default_weight": default_weight
                }
                
                # Upsert (insert or update)
                result = await db.questions.update_one(
                    {"key": q_data['key']},
                    {"$set": question_doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted += 1
                    logger.debug(f"Inserted question: {q_data['key']}")
                elif result.modified_count > 0:
                    updated += 1
                    logger.debug(f"Updated question: {q_data['key']}")
                
            except Exception as e:
                logger.error(f"Error processing question '{q_data.get('key', 'unknown')}': {e}")
                errors += 1
        
        # Create index on key field
        await db.questions.create_index("key", unique=True)
        await db.questions.create_index("category")
        
        # Summary
        logger.info("=" * 60)
        logger.info("Database Seeding Summary")
        logger.info("=" * 60)
        logger.info(f"Total questions processed: {len(questions_data)}")
        logger.info(f"  - Inserted: {inserted}")
        logger.info(f"  - Updated: {updated}")
        logger.info(f"  - Errors: {errors}")
        
        # Verify count
        total_in_db = await db.questions.count_documents({})
        logger.info(f"Total questions in database: {total_in_db}")
        logger.info("=" * 60)
        
        # Display category distribution
        logger.info("\nCategory Distribution:")
        for category in ["TRUST", "BEHAVIOR", "VALUES", "DYNAMICS"]:
            count = await db.questions.count_documents({"category": category})
            logger.info(f"  {category}: {count}")
        
        return errors == 0
        
    except Exception as e:
        logger.error(f"Fatal error during seeding: {e}")
        return False
        
    finally:
        client.close()
        logger.info("Database connection closed")


async def clear_questions():
    """Clear all questions from database (use with caution!)"""
    logger.warning("WARNING: This will delete ALL questions from the database!")
    confirmation = input("Type 'YES' to confirm: ")
    
    if confirmation != "YES":
        logger.info("Operation cancelled")
        return
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        result = await db.questions.delete_many({})
        logger.info(f"Deleted {result.deleted_count} questions")
    finally:
        client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with questions")
    parser.add_argument("--clear", action="store_true", help="Clear all questions before seeding")
    parser.add_argument("--clear-only", action="store_true", help="Only clear questions (no seeding)")
    
    args = parser.parse_args()
    
    if args.clear_only:
        asyncio.run(clear_questions())
    else:
        if args.clear:
            asyncio.run(clear_questions())
        
        success = asyncio.run(seed_questions())
        
        if success:
            logger.info("✅ Database seeding completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Database seeding completed with errors")
            sys.exit(1)
