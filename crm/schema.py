import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# ==============================
# Queries
# ==============================
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


# ==============================
# Mutations
# ==============================
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)

    def mutate(self, info, name, email, phone=None):
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)
        total_amount = graphene.Float(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_id, total_amount):
        customer = Customer.objects.get(pk=customer_id)
        product = Product.objects.get(pk=product_id)
        order = Order(customer=customer, product=product, total_amount=total_amount)
        order.save()
        return CreateOrder(order=order)


# ==============================
# New Mutation: Update Low Stock
# ==============================
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        increment = graphene.Int(required=False, default_value=10)

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info, increment):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += increment
            product.save()
            updated.append(product)

        message = f"Updated {len(updated)} products with stock < 10"
        return UpdateLowStockProducts(updated_products=updated, message=message)


# ==============================
# Root Mutation
# ==============================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello World")
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()

    def resolve_total_customers(root, info):
        from crm.models import Customer
        return Customer.objects.count()

    def resolve_total_orders(root, info):
        from crm.models import Order
        return Order.objects.count()

    def resolve_total_revenue(root, info):
        from crm.models import Order
        return sum(order.totalamount for order in Order.objects.all())



schema = graphene.Schema(query=Query, mutation=Mutation)
