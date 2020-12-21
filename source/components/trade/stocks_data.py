import json


def get_sorted_stocks() -> list:
    with open('stocks.json', 'r') as file:
        max_possible_profits = json.load(file)
        return sorted(list(map(lambda el: (el[1][1],) + (el[0],) + (el[1][0],) + tuple(el[1][2:]),
                               max_possible_profits.items())),
                      key=lambda el: el[2], reverse=True)
