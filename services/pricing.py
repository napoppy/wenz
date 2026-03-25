from models.data_models import Account
import config


class PricingService:
    def __init__(self, price_coefficient: float = None):
        self.price_coefficient = price_coefficient or config.DEFAULT_PRICE_COEFFICIENT

    def calculate_price(self, estimated_read: float) -> tuple:
        price_min = estimated_read * config.MIN_PRICE_COEFFICIENT
        price_standard = estimated_read * self.price_coefficient
        price_max = estimated_read * config.MAX_PRICE_COEFFICIENT

        return price_min, price_standard, price_max

    def calculate_for_account(self, account: Account) -> Account:
        price_min, price_standard, price_max = \
            self.calculate_price(account.estimated_read)

        account.set_prices(price_min, price_standard, price_max)

        return account

    def calculate_for_accounts(self, accounts: list) -> list:
        for account in accounts:
            self.calculate_for_account(account)
        return accounts


def create_pricing_service(price_coefficient: float = None) -> PricingService:
    return PricingService(price_coefficient=price_coefficient)
