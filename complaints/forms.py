# forms.py
from django import forms
from .models import Ticket

HOD_EMAIL_CHOICES = [
    ('ailen.japhet@rea.gov.ng', 'HRM - Ag. Director'),
    ('uba.patrick@rea.gov.ng', 'PR&D - Ag. Director'),
    ('muntari.ibrahim@rea.gov.ng', 'PIO - Ag. Director'),
    ('', 'REF - Ag. Director'),
    ('magaji.dambatta@rea.gov.ng', 'Project - Ag. Director'),
    ('bulus.maiyaki@rea.gov.ng', 'Procurement - Director'),
    ('kashim.ibrahim@rea.gov.ng', 'Legal - Director'),
    ('okhareayon.akwe@rea.gov.ng', 'Audit - Ag. Director'),
    ('', 'M&E - Ag. Director'),
    ('ibeh.edith@rea.gov.ng', 'Protocol - HOD'),
    ('eyo.adonis@rea.gov.ng', 'ICT - HOD'),
    ('magaji.abdu@rea.gov.ng', 'Finance & Account - Director'),
    # ('praizjoshua263@gmail.com', 'TESTER'),
]

class InitialTicketForm(forms.ModelForm):
    hod_email = forms.ChoiceField(choices=HOD_EMAIL_CHOICES)

    class Meta:
        model = Ticket
        fields = ['complaint_name', 'department', 'problem', 'problem_description', 'hod_email']



class FullTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ['ticket_number', 'created_at']

    def clean(self):
        cleaned_data = super().clean()
        satisfy = cleaned_data.get('complain_satisfy')
        reason = cleaned_data.get('unsatisfied_reason')

        if satisfy == 'no' and not reason:
            self.add_error('unsatisfied_reason', 'Please provide a reason for dissatisfaction.')

        return cleaned_data


# class TicketForm(forms.ModelForm):
#     class Meta:
#         model = Ticket
#         fields = [
#             'complaint_name', 'department', 'problem',
#             'problem_description', 'ict_response',
#             'complain_satisfy', 'unsatisfied_reason',
#             'signed_by_staff', 'signed_by_hod_ict', 'signed_by_head_section'
#         ]

#     def clean(self):
#         cleaned_data = super().clean()
#         satisfy = cleaned_data.get('complain_satisfy')
#         reason = cleaned_data.get('unsatisfied_reason')

#         if satisfy == 'no' and not reason:
#             self.add_error('unsatisfied_reason', 'Please provide a reason for dissatisfaction.')

#         return cleaned_data
