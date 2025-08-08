from django.urls import path
from .views import (
    TicketCreateView,
    approve_ticket_preview_view,
    CompleteTicketUpdateView,
    TicketListView,
    TicketDetailView,
    ticket_pdf_view,
    hod_approval_response_view,
    TicketSubmittedView,
    TicketDeleteView
)

urlpatterns = [
    path('create/', TicketCreateView.as_view(), name='ticket-create'),
    path('approve/', approve_ticket_preview_view, name='ticket-approve'),
    path('complete/<int:pk>/', CompleteTicketUpdateView.as_view(), name='ticket-complete'),
    path('', TicketListView.as_view(), name='ticket-list'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('<int:pk>/pdf/', ticket_pdf_view, name='ticket-pdf'),
    path('ticket/approve-response/<uid>/<action>/', hod_approval_response_view, name='ticket-hod-response'),
    path('submitted/', TicketSubmittedView.as_view(), name='ticket-submitted'),
    path('delete/<int:pk>/', TicketDeleteView.as_view(), name='ticket-delete'),

]
