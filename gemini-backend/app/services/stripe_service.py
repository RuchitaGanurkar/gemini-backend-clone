import stripe
from app.config import settings

stripe.api_key = settings.stripe_secret_key

class StripeService:
    def __init__(self):
        self.pro_price_id = "price_1234567890"  # Replace with actual Stripe price ID
    
    def create_customer(self, email: str, mobile_number: str):
        return stripe.Customer.create(
            email=email,
            metadata={"mobile_number": mobile_number}
        )
    
    def create_checkout_session(self, customer_id: str, success_url: str, cancel_url: str):
        return stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': self.pro_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
        )
    
    def get_subscription(self, subscription_id: str):
        return stripe.Subscription.retrieve(subscription_id)

stripe_service = StripeService()
