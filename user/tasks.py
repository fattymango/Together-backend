from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger

from .util import send_verification_email, send_validation_volunteer_email

logger = get_task_logger(__name__)


@shared_task(name="task_send_verification_email")
def task_send_verification_email(pk, name, email):
	logger.info("Sent review email " + email)
	return send_verification_email(pk, name, email)


@shared_task(name="task_send_volunteer_validation_email")
def task_send_volunteer_validation_email(pk, name):
	logger.info("Sent validation email " + name)
	return send_validation_volunteer_email(pk, name)


@shared_task(name="add")
def add(x, y):
	return x + y
