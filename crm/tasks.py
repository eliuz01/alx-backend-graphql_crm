from datetime import datetime
import requests
from celery import shared_task
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

@shared_task
def generate_crm_report():
    """Fetch totals via GraphQL and log a weekly CRM report."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql/",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        {
            totalCustomers
            totalOrders
            totalRevenue
        }
        """)

        result = client.execute(query)

        customers = result.get("totalCustomers", 0)
        orders = result.get("totalOrders", 0)
        revenue = result.get("totalRevenue", 0)

        message = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

    except Exception as e:
        message = f"{timestamp} - Report generation failed: {str(e)}\n"

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(message)
