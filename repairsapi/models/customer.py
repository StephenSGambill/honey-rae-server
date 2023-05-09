from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    # Relationship to the built-in User model which has name and email
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional address field to capture from the client
    address = models.CharField(max_length=155)

    @property
    def full_name(self):
        """
        Property getter method for retrieving the full name of the Customer.
        Concatenates the first name and last name of the associated User object.
        Usage:
            customer = Customer.objects.get(...)
            print(customer.full_name)  # Access the full_name property
        """
        return f"{self.user.first_name} {self.user.last_name}"
