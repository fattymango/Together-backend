from celery import shared_task
from celery.utils.log import get_task_logger

from .util import send_request_to_volunteer

logger = get_task_logger(__name__)

@shared_task(name="task_send_request")
def task_send_request(request):
	logger.info("Sent request " + str(request["id"]))

	return send_request_to_volunteer(request)
