"""
Background Update Scheduler Service
Automatically updates BRI data every 6 hours
"""

import logging
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database.bri_database import BRIDatabase
from services.bri_update_service import BRIUpdateService
from data_fetch_and_process.bri_data_fetcher import BRI_ASSETS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackgroundUpdateScheduler:
    """Background scheduler for automatic BRI data updates"""

    def __init__(self, db_path='data/bri_data.db', interval_hours=6):
        self.db_path = db_path
        self.interval_hours = interval_hours
        self.db = BRIDatabase(db_path)
        self.update_service = BRIUpdateService(db_path)
        self.scheduler = BackgroundScheduler()

        # Add scheduled job
        self.scheduler.add_job(
            self.run_update,
            trigger=IntervalTrigger(hours=interval_hours),
            id='bri_update_job',
            name='BRI Data Update',
            replace_existing=True
        )

    def run_update(self):
        """Run update for all assets and return results"""
        logger.info("=" * 60)
        logger.info("Starting scheduled BRI data update...")
        logger.info("=" * 60)

        results = []
        success_count = 0
        fail_count = 0

        for asset_key, asset_info in BRI_ASSETS.items():
            try:
                logger.info(f"Updating {asset_key}...")

                # Check for updates first
                check_result = self.update_service.check_for_updates(
                    asset_key,
                    asset_info['yahoo_ticker']
                )

                if check_result.get('has_new_data'):
                    # Update asset
                    result = self.update_service.update_asset(
                        asset_key,
                        asset_info['yahoo_ticker']
                    )

                    results.append({
                        'asset': asset_key,
                        'success': result.get('success', False),
                        'new_rows': result.get('new_bri_rows', 0),
                        'message': result.get('message', result.get('error', 'Unknown'))
                    })

                    if result.get('success'):
                        logger.info(f"  ✓ {asset_key}: Updated with {result.get('new_bri_rows', 0)} new rows")
                        success_count += 1
                    else:
                        logger.error(f"  ✗ {asset_key}: {result.get('error', 'Unknown error')}")
                        fail_count += 1
                else:
                    logger.info(f"  - {asset_key}: No new data available")
                    results.append({
                        'asset': asset_key,
                        'success': 'up_to_date',
                        'new_rows': 0,
                        'message': 'Already up to date'
                    })

            except Exception as e:
                logger.error(f"  ✗ {asset_key}: Error - {str(e)}")
                results.append({
                    'asset': asset_key,
                    'success': False,
                    'new_rows': 0,
                    'message': str(e)
                })
                fail_count += 1

        # Log summary
        logger.info("=" * 60)
        logger.info(f"Scheduled update complete: {success_count} succeeded, {fail_count} failed")
        logger.info("=" * 60)

        # Log to database
        self.db.log_update(
            asset_name='SCHEDULER',
            update_type='scheduled_batch',
            status='success' if fail_count == 0 else 'partial',
            rows=success_count,
            message=f"Scheduled update: {success_count} succeeded, {fail_count} failed"
        )

        return {
            'results': results,
            'success_count': success_count,
            'fail_count': fail_count,
            'up_to_date_count': len(results) - success_count - fail_count
        }

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            logger.info(f"Starting BRI background scheduler (every {self.interval_hours} hours)...")
            self.scheduler.start()

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            logger.info("Stopping BRI background scheduler...")
            self.scheduler.shutdown()

    def update_now(self):
        """Trigger an immediate update and return results"""
        logger.info("Manually triggering update...")
        return self.run_update()

    def get_status(self):
        """Get scheduler status"""
        if self.scheduler.running:
            jobs = self.scheduler.get_jobs()
            if jobs:
                job = jobs[0]
                return {
                    'running': True,
                    'next_run': job.next_run_time,
                    'interval_hours': self.interval_hours
                }
        return {'running': False}


# Singleton instance
_scheduler = None


def get_scheduler(db_path='data/bri_data.db', interval_hours=6):
    """Get or create the scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundUpdateScheduler(db_path, interval_hours)
        # Start the scheduler when created
        _scheduler.start()
    return _scheduler
