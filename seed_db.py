# seed_db.py
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product

def run():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    customers = [
        ("Alice", "alice@example.com", "+1234567890"),
        ("Bob", "bob@example.com", "123-456-7890"),
    ]
    for name, email, phone in customers:
        Customer.objects.create(name=name, email=email, phone=phone)

    products = [
        ("Laptop", 999.99, 10),
        ("Phone", 499.99, 20),
    ]
    for name, price, stock in products:
        Product.objects.create(name=name, price=price, stock=stock)

    print("Database seeded successfully!")

if __name__ == "__main__":
    run()
