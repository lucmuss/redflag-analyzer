"""
Zentrale Konfiguration - Alle konfigurierbaren Werte aus .env
"""
import os


class Config:
    """Zentrale Config-Klasse für alle .env Variablen"""
    
    # Pricing & Credits
    FREE_CREDITS_ON_SIGNUP = int(os.getenv('FREE_CREDITS_ON_SIGNUP', '3'))
    ANALYSIS_CREDIT_COST = int(os.getenv('ANALYSIS_CREDIT_COST', '1'))
    FREE_ANALYSES_LIMIT = int(os.getenv('FREE_ANALYSES_LIMIT', '3'))
    
    # Referral System
    REFERRAL_REWARD_INVITER = int(os.getenv('REFERRAL_REWARD_INVITER', '2'))
    REFERRAL_REWARD_INVITED = int(os.getenv('REFERRAL_REWARD_INVITED', '1'))
    REFERRAL_MAX_USES = int(os.getenv('REFERRAL_MAX_USES', '10'))
    REFERRAL_CREDITS_PER_USE = int(os.getenv('REFERRAL_CREDITS_PER_USE', '3'))
    
    # Badge System
    BADGE_DEFAULT_POINTS = int(os.getenv('BADGE_DEFAULT_POINTS', '10'))
    BADGE_FIRST_ANALYSIS_POINTS = int(os.getenv('BADGE_FIRST_ANALYSIS_POINTS', '50'))
    BADGE_POWER_USER_POINTS = int(os.getenv('BADGE_POWER_USER_POINTS', '100'))
    
    # Pagination
    PAGINATION_ANALYSES_LIST = int(os.getenv('PAGINATION_ANALYSES_LIST', '20'))
    PAGINATION_BLOG_POSTS = int(os.getenv('PAGINATION_BLOG_POSTS', '12'))
    PAGINATION_SUBSCRIBERS = int(os.getenv('PAGINATION_SUBSCRIBERS', '50'))
    PAGINATION_RANKINGS = int(os.getenv('PAGINATION_RANKINGS', '100'))
    
    # Credit Packages (float da Preise)
    CREDITS_5_PRICE = float(os.getenv('CREDITS_5_PRICE', '4.99'))
    CREDITS_10_PRICE = float(os.getenv('CREDITS_10_PRICE', '8.99'))
    CREDITS_25_PRICE = float(os.getenv('CREDITS_25_PRICE', '19.99'))
    CREDITS_50_PRICE = float(os.getenv('CREDITS_50_PRICE', '34.99'))
    CREDITS_100_PRICE = float(os.getenv('CREDITS_100_PRICE', '59.99'))
    
    # Premium Subscription
    PREMIUM_MONTHLY_PRICE = float(os.getenv('PREMIUM_MONTHLY_PRICE', '9.99'))
    PREMIUM_UNLIMITED_ANALYSES = os.getenv('PREMIUM_UNLIMITED_ANALYSES', 'True') == 'True'
    PREMIUM_PRIORITY_SUPPORT = os.getenv('PREMIUM_PRIORITY_SUPPORT', 'True') == 'True'
    
    @classmethod
    def get_credit_packages(cls):
        """Gibt alle Credit-Pakete zurück"""
        return {
            5: cls.CREDITS_5_PRICE,
            10: cls.CREDITS_10_PRICE,
            25: cls.CREDITS_25_PRICE,
            50: cls.CREDITS_50_PRICE,
            100: cls.CREDITS_100_PRICE,
        }
