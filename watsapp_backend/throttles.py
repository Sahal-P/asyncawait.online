from rest_framework.throttling import AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    scope = 'login_rate'
    
class RegisterRateThrottle(AnonRateThrottle):
    scope = 'register_rate'
    
