#!/usr/bin/env python3
# send_order_reminders.py

import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def main():
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Calculate cutoff date (7 days ago)
        cutoff_date = (datetime.now() - timedelta(days=7)).date().isoformat()

        # Define GraphQL query
        query = gql("""
        query GetRecentOrders($cutoff: Date!) {
            orders(orderDate_Gte: $cutoff) {
                id
                customer {
                    email
                }
            }
        }
        """)

        # Execute query
        result = client.execute(query, variable_values={"cutoff": cutoff_date})
        orders = result.get("orders", [])

        # Log each order
        for order in orders:
            order_id = order["id"]
            customer_email = order["customer"]["email"]
            logging.info(f"Reminder -> Order ID: {order_id}, Customer Email: {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error processing reminders: {str(e)}")
        print(f"Failed: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()
