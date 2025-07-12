import random
import string
from typing import Optional
from app.core.cache import cache

class OTPService:
    def __init__(self):
        self.otp_length = 6
        self.otp_ttl = 300  # 5 minutes
    
    def generate_otp(self, mobile_number: str) -> str:
        otp = ''.join(random.choices(string.digits, k=self.otp_length))
        cache.set(f"otp:{mobile_number}", otp, self.otp_ttl)
        return otp
    
    def verify_otp(self, mobile_number: str, otp: str) -> bool:
        stored_otp = cache.get(f"otp:{mobile_number}")
        if stored_otp and stored_otp == otp:
            cache.delete(f"otp:{mobile_number}")
            return True
        return False

otp_service = OTPService()
