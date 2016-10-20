from django.db import models

# Create your models here.
#
STATUS_CHOICES = (
    ('queued', "queued"),
    ('sent', "sent"),
    ('delivered', "delivered")
)


class FailedMessages(models.Model):
    uid = models.CharField(max_length=512)
    status = models.CharField(choices=STATUS_CHOICES, max_length=512)
    message = models.CharField(max_length=1024)
    retries = models.IntegerField()
    callback_url = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    modified_time = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return "%s - %s" % (self.uid, self.massage)

    class Meta:
        db_table = 'failed_messages'