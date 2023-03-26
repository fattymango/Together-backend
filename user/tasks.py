from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger

from .util import send_verification_email

logger = get_task_logger(__name__)


@shared_task(name="send_verification_email_task")
def send_verification_email_task(pk, name, email):
	logger.info("Sent review email " + email)
	return send_verification_email(pk, name, email)


@shared_task(name="add")
def add(x, y):
	return x + y
