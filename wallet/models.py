from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    # Link each transaction to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Categories for money management
    CATEGORY_CHOICES = [
    ('Shopping', 'Shopping'),
    ('Mortgage', 'Mortgage'),
    ('Restaurants', 'Restaurants'),
    ('Credit Card', 'Credit Card'),
    ('Movies & DVDs', 'Movies & DVDs'),
    ('Home Improvement', 'Home Improvement'),
    ('Utilities', 'Utilities'),
    ('Music', 'Music'),
    ('Mobile Phone', 'Mobile Phone'),
    ('Gas & Fuel', 'Gas & Fuel'),
    ('Groceries', 'Groceries'),
    ('Paycheck', 'Paycheck'),
    ('Fast Food', 'Fast Food'),
    ('Coffee Shops', 'Coffee Shops'),
    ('Internet', 'Internet'),
    ('Transfer', 'Transfer'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    # AI logic fields
    risk_score = models.FloatField(default=0.0)
    is_fraud = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.amount} DH ({self.category})"