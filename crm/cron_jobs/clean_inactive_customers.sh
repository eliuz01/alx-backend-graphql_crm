#!/bin/bash
# clean_inactive_customers.sh

# Navigate to the project root (adjust path if needed)
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers
deleted_count=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta
cutoff_date = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff_date)
count = qs.count()
qs.delete()
print(count)
")

# Log the result with timestamp
echo \"$(date): Deleted $deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt
