from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.data_collector import fetch_and_store_traces_for_all_services

scheduler = AsyncIOScheduler()


def start_scheduler():
    """
    Start the scheduler and schedule the trace fetching job.
    """
    # Schedule the task to run every 30 seconds
    scheduler.add_job(
        fetch_and_store_traces_for_all_services,
        trigger=IntervalTrigger(seconds=60),
        id="trace_fetcher",
        replace_existing=True,
    )

    print("Scheduler started. Fetching traces every 60 seconds.")
    scheduler.start()


def stop_scheduler():
    """
    Stop the scheduler gracefully.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Scheduler stopped.")
    else:
        print("Scheduler was not running.")
