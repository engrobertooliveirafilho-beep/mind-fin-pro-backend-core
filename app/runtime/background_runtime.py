from fastapi import BackgroundTasks

def enqueue_semantic_ingestion(background_tasks, fn, *args, **kwargs):
    background_tasks.add_task(fn, *args, **kwargs)
