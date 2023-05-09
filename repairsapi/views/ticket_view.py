"""View module for handling requests for employee data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer
from django.db.models import Q


class TicketView(ViewSet):
    """Honey Rae API tickets view"""

    def destroy(self, request, pk=None):
        """Handle DELETE requests for service tickets
        Returns:
            Response: None with 204 status code
        """
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data["description"]
        new_ticket.emergency = request.data["emergency"]
        new_ticket.save()

        serialized = TicketSerializer(new_ticket)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests to get all tickets
        Returns:
            Response == JSON serialized list of tickets
        """
        service_tickets = []

        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params["status"] == "done":
                    service_tickets = service_tickets.filter(
                        date_completed__isnull=False
                    )

                elif request.query_params["status"] == "all":
                    service_tickets = ServiceTicket.objects.all()
                elif request.query_params["status"] == "unclaimed":
                    service_tickets = service_tickets.filter(employee__isnull=True)
                elif request.query_params["status"] == "inprogress":
                    service_tickets = service_tickets.filter(
                        employee__isnull=False, date_completed__isnull=True
                    )
            elif "description" in request.query_params:
                print("hit")
                service_tickets = service_tickets.filter(
                    description__contains=request.query_params["description"]
                )

        else:
            service_tickets = ServiceTicket.objects.filter(
                customer__user=request.auth.user
            )

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single ticket

        Returns:
            Response -- JSON serialized ticket record
        """

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Hand PUT requests for single customer

        Returns:
            Response -- No response body. Just 204 status cod.
        """
        # Select the targeted ticket using pk
        ticket = ServiceTicket.objects.get(pk=pk)

        # Get the employee id from the client request
        employee_id = request.data["employee"]

        # Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)

        # Assign that Employee instance to the employee property of the ticket
        ticket.employee = assigned_employee

        ticket.date_completed = request.data["date_completed"]

        # Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "specialty", "full_name")


class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "full_name", "address")


class TicketSerializer(serializers.ModelSerializer):
    """JSON serializer for tickets"""

    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = (
            "id",
            "description",
            "emergency",
            "date_completed",
            "customer",
            "employee",
        )
        depth = 1
