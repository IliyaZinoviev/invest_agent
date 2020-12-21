intervals = ['hour', '30min', '15min', '10min', '5min', '3min', '1min']
intervals_vals_dict = {'hour': 61, '30min': 31, '15min': 16, '10min': 11, '5min': 6, '3min': 4, '1min': 2}
# intervals = ['hour']


def get_fee(buying_price, selling_price):
    fee = + buying_price * 0.0005 + selling_price * 0.0005
    tax = (selling_price - buying_price - fee) * 0.13
    return fee + tax
