import uuid
from django.db import models

class Ticket(models.Model):
    COMPLAIN_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved by HOD', 'Approved by HOD'),
        ('Disapproved by HOD', 'Disapproved by HOD'),
        )

    ticket_number = models.CharField(max_length=10, unique=True, editable=False)
    complaint_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    problem = models.CharField(max_length=255)
    problem_description = models.TextField()

    # officer_in_charge = models.CharField(max_length=100, blank=True, null=True)
    ict_response = models.TextField(blank=True, null=True)
    complain_satisfy = models.CharField(max_length=3, choices=COMPLAIN_CHOICES)
    unsatisfied_reason = models.CharField(max_length=255, blank=True, null=True)
    hod_email = models.EmailField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')


    signed_by_staff = models.BooleanField(default=False)
    signed_by_hod_ict = models.BooleanField(default=False)
    signed_by_head_section = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Ticket #{self.ticket_number}'
