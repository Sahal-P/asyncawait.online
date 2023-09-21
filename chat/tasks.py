from celery import shared_task

@shared_task
def shared_task():
    for i in range(10):
        print('celery',i)
    return