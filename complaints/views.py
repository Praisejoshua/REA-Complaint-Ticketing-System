from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import get_template, render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.views import View 
from xhtml2pdf import pisa

from .models import Ticket
from .forms import InitialTicketForm, FullTicketForm


class TicketCreateView(View):
    template_name = 'tickets/ticket_form_initial.html'

    def get(self, request, *args, **kwargs):
        form = InitialTicketForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = InitialTicketForm(request.POST)
        if form.is_valid():
            request.session['pending_ticket_data'] = form.cleaned_data
            messages.success(request, "Please review your ticket before final submission.")
            return redirect('ticket-approve')
        else:
            messages.error(request, "There were errors in your submission. Please correct them.")
        return render(request, self.template_name, {'form': form})


def approve_ticket_preview_view(request):
    form_data = request.session.get('pending_ticket_data')
    if not form_data:
        messages.error(request, "No ticket data found for approval.")
        return redirect('ticket-create')

    if request.method == 'POST':
        if 'approve' in request.POST:
            form = InitialTicketForm(form_data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.hod_email = form.cleaned_data['hod_email']
                ticket.status = "Pending HOD Approval"
                ticket.save()

                uid = urlsafe_base64_encode(force_bytes(ticket.pk))
                approve_url = request.build_absolute_uri(
                    reverse('ticket-hod-response', kwargs={'uid': uid, 'action': 'approve'})
                )
                decline_url = request.build_absolute_uri(
                    reverse('ticket-hod-response', kwargs={'uid': uid, 'action': 'decline'})
                )

                subject = "New Complaint Submitted for Approval"
                message = (
                    f"A new complaint has been submitted for your approval.\n\n"
                    f"Ticket Number: {ticket.ticket_number}\n"
                    f"Complaint Name: {ticket.complaint_name}\n"
                    f"Department: {ticket.department}\n"
                    f"Problem: {ticket.problem}\n"
                    f"Description: {ticket.problem_description}\n\n"
                    f"Please choose an action below:\n"
                    f"✅ Approve: {approve_url}\n"
                    f"❌ Decline: {decline_url}"
                )
                from_email = settings.DEFAULT_FROM_EMAIL

                EmailMultiAlternatives(
                    subject, message, from_email, [ticket.hod_email]
                ).send()

                request.session.pop('pending_ticket_data', None)
                return redirect('ticket-submitted')

        elif 'cancel' in request.POST or 'decline' in request.POST:
            request.session.pop('pending_ticket_data', None)
            messages.info(request, "Ticket submission cancelled.")
            return redirect('ticket-list')

    return render(request, 'tickets/approve_preview.html', {'form_data': form_data})


class TicketSubmittedView(TemplateView):
    template_name = 'tickets/ticket_submitted.html'


def hod_approval_response_view(request, uid, action):
    try:
        ticket_id = force_str(urlsafe_base64_decode(uid))
        ticket = get_object_or_404(Ticket, pk=ticket_id)
    except:
        messages.error(request, "Invalid approval link.")
        return redirect('ticket-list')

    if action == 'approve':
        ticket.status = 'Approved by HOD'
        ticket.save()

        full_response_link = request.build_absolute_uri(
            reverse('ticket-complete', kwargs={'pk': ticket.pk})
        )

        subject = f"[ACTION REQUIRED] New Complaint Approved – ICT Response Needed"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = ['eyo.adonis@rea.gov.ng']

        context = {
            'ticket': ticket,
            'form_link': full_response_link,
        }

        html_message = render_to_string('tickets/ticket_to_solveproblems.html', context)
        plain_message = (
            f"A complaint has been approved by the HOD and now requires ICT response.\n\n"
            f"Complaint: {ticket.complaint_name}\n"
            f"Department: {ticket.department}\n"
            f"Problem: {ticket.problem}\n"
            f"Description: {ticket.problem_description}\n\n"
            f"Respond here: {full_response_link}"
        )

        email = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
        email.attach_alternative(html_message, "text/html")
        email.send()

        message = "✅ Ticket has been approved successfully."
    elif action == 'decline':
        ticket.status = 'Declined by HOD'
        ticket.save()
        message = "❌ Ticket has been declined."
    else:
        message = "Invalid action."

    return render(request, 'tickets/hod_response_result.html', {'ticket': ticket, 'message': message})


class CompleteTicketUpdateView(UpdateView):
    model = Ticket
    form_class = FullTicketForm
    template_name = 'tickets/ticket_form_continue.html'
    success_url = reverse_lazy('ticket-list')


class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'


class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'


def ticket_pdf_view(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    template = get_template('tickets/ticket_pdf.html')
    html = template.render({'ticket': ticket})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with PDF generation <pre>' + html + '</pre>')
    return response
