def get_percentage_ratio(numerator, denominator):
    return numerator / denominator * 100


def get_percentage_diff(numerator, denominator):
    return abs(100 - get_percentage_ratio(numerator, denominator))


def get_step(max_val, min_val, count):
    return (max_val - min_val) / count


def get_average(val1, val2):
    return (val1 + val2) / 2


def get_proportions_left_nominator(rnumerator, ldenominator, rdenominator):
    return rnumerator * ldenominator / rdenominator
