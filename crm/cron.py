import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client


def log_crm_heartbeat():
    """Log a heartbeat message every 5 minutes."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

    # Optional: query GraphQL hello endpoint with gql client
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql/",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        result = client.execute(query)

        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL hello: {result}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {str(e)}\n")


def update_low_stock():
    """Run every 12 hours to restock low products via GraphQL mutation."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql/",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        updates = result.get("updateLowStockProducts", {})

        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} Update Result: {updates}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} Update failed: {str(e)}\n")
