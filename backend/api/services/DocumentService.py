import re
import logging

from django.core.exceptions import ValidationError
from django.db.transaction import on_commit
from minio import Minio

from api.models.DocumentFileAttachment import DocumentFileAttachment
from api.models.DocumentHistory import DocumentHistory
from api.models.Organization import Organization
from api.notifications.notification_types import NotificationType
from api.async_tasks import async_send_notification
from tfrs.settings import MINIO


class DocumentService(object):
    """
    Helper functions for Document Service
    """
    @staticmethod
    def create_history(document):
        """
        Create the Document History
        """
        history = DocumentHistory(
            compliance_period_id=document.compliance_period_id,
            create_user=document.create_user,
            document_id=document.id,
            status_id=document.status.id,
            title=document.title,
            type_id=document.type.id,
            update_user=document.update_user
        )

        # Validate
        try:
            history.full_clean()
        except ValidationError as error:
            raise ValidationError(error)

        history.save()

    @staticmethod
    def delete_attachments(document_id, attachment_ids):
        """
        Sends a request to the minio instance to delete the files associated
        to the DocumentFile records related to the provided parameters
        """
        minio = Minio(MINIO['ENDPOINT'],
                      access_key=MINIO['ACCESS_KEY'],
                      secret_key=MINIO['SECRET_KEY'],
                      secure=MINIO['USE_SSL'])

        attachments = DocumentFileAttachment.objects.filter(
            document_id=document_id,  # additional security
            id__in=attachment_ids
        )

        object_names = map(DocumentService.get_filename, attachments)
        for error in minio.remove_objects(MINIO['BUCKET_NAME'], object_names):
            logging.error(error)

        attachments.update(
            is_removed=True
        )

    @staticmethod
    def remove_orphans():
        """
        Sends a request to the minio instance to delete the files associated
        to the DocumentFile records related to the provided parameters
        """
        minio = Minio(MINIO['ENDPOINT'],
                      access_key=MINIO['ACCESS_KEY'],
                      secret_key=MINIO['SECRET_KEY'],
                      secure=MINIO['USE_SSL'])

        objects = minio.list_objects(MINIO['BUCKET_NAME'], recursive=True)

        attachments = DocumentFileAttachment.objects.filter(
            is_removed=False
        )
        object_names = list(map(DocumentService.get_filename, attachments))
        to_delete = []

        for o in objects:
            if not o.is_dir:
                if o.object_name not in object_names:
                    print('deleting: {} since it is not referenced'.format(o.object_name))
                    to_delete.append(o.object_name)

        for error in minio.remove_objects(MINIO['BUCKET_NAME'], to_delete):
            logging.error(error)

    @staticmethod
    def get_filename(attachment):
        """
        This parses the url from DocumentFile and gets the filename that you
        can send to minio for deletion
        """
        return re.search(r".*/([^\?]+)", attachment.url).group(1)

    @staticmethod
    def validate_status(current_status, next_status):
        """
        This function checks if the next status is actually valid for the
        current status
        """
        if current_status.status in ["Submitted", "Pending Submission"] and \
                next_status.status == "Draft":
            return True

        if current_status.status in ["Archived", "Cancelled"]:
            return False

        if current_status.status == "Received" and \
                next_status.status != "Archived":
            return False

        if current_status.status == "Submitted" and \
                next_status.status != "Received":
            return False

        if current_status.status == "Pending Submission" and \
                next_status.status != "Draft":
            return False

        if current_status.status in ["Security Scan Failed"] and \
                next_status.status not in ["Draft", "Submitted"]:
            return False

        if current_status.status not in [
                "Draft", "Security Scan Failed"]:
            if next_status.status == "Draft":
                return False

        return True

    @staticmethod
    def send_notification(document, originating_user):
        interested_organizations = []

        government = Organization.objects.filter(
            type__type='Government').first()

        user = document.create_user

        notification_type = None

        if document.status.status == "Submitted":
            interested_organizations.extend([government, user.organization])
            notification_type = NotificationType.DOCUMENT_SUBMITTED

        elif document.status.status == "Pending Submission":
            interested_organizations.append(user.organization)
            notification_type = NotificationType.DOCUMENT_PENDING_SUBMISSION

        elif document.status.status == "Received":
            interested_organizations.extend([government, user.organization])
            notification_type = NotificationType.DOCUMENT_RECEIVED

        elif document.status.status == "Archived":
            interested_organizations.extend([government, user.organization])
            notification_type = NotificationType.DOCUMENT_ARCHIVED

        elif document.status.status == "Security Scan Failed":
            interested_organizations.append(user.organization)
            notification_type = NotificationType.DOCUMENT_SCAN_FAILED

        if notification_type:
            for organization in interested_organizations:
                on_commit(
                    lambda: async_send_notification.delay(
                        interested_organization_id=organization.id,
                        message=notification_type.name,
                        notification_type=notification_type.value,
                        originating_user_id=originating_user.id,
                        related_document_id=document.id
                    )
                )
