"""Saddest documentation ever"""

import time
from gdax.authenticated_client import AuthenticatedClient
from gdax import WebsocketClient
from gdax.order_book import OrderBook
from gdax.public_client import PublicClient
import numpy as np
import datetime
import csv





def bid_spread(bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals):
    num_intervals = len(bid_intervals)
    normalized_bids = []
    normalized_asks = []
    for i in range(num_intervals):
        normalized_bid_spread = []
        normalized_ask_spread = []
        for j in range(len(bid_intervals[i])):
            volume = np.sum(bid_depths_intervals[i])
            normalized_bid_spread.append(bid_depths_intervals[i][j]/volume)
        for l in range(len(ask_intervals[i])):
            volume = np.sum(ask_depths_intervals[i])
            normalized_ask_spread.append(ask_depths_intervals[i][l]/volume)
        normalized_bids.append(normalized_bid_spread)
        normalized_asks.append(normalized_ask_spread)
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    for x in range(num_intervals):
        ax.plot(bid_intervals[x], normalized_bids[x])
        ax.plot(ask_intervals[x], normalized_asks[x])
    plt.show()
    return normalized_bids, normalized_asks



def calculate_volume_changes(bid_depths_intervals, ask_depths_intervals):
    """Sums the total volume of bids and asks over all intervals"""
    summed_bid_volume = [float(np.sum(i)) for i in bid_depths_intervals]
    summed_ask_volume = [float(np.sum(i)) for i in ask_depths_intervals]
    return summed_bid_volume, summed_ask_volume


def calculate_asks_and_bids(bid_intervals, ask_intervals):
    """Calculates the average asks and average bids over all intervals"""
    average_bids = []
    average_asks = []
    for bid in bid_intervals:
        if len(bid) > 0:
            average_bids.append(np.sum(bid)/len(bid))
    for ask in ask_intervals:
        if len(ask) > 0:
            average_asks.append(np.sum(ask) / len(ask))
    return average_bids, average_asks


def calculate_deltas(average_bids, average_asks, summed_bid_volume, summed_ask_volume):
    """Calculates changes over multiple intervals"""
    delta_bid_volume = np.diff(summed_bid_volume)
    delta_ask_volume = np.diff(summed_ask_volume)
    delta_bids = np.diff(average_bids)
    delta_asks = np.diff(average_asks)
    return delta_bids, delta_asks, delta_bid_volume, delta_ask_volume


def calc_decision_metrics(bid_intervals, bid_depths_intervals,ask_intervals, ask_depths_intervals):
    """Returns proportion of each category (bids, asks, bid_depths, ask_depths) that are above or
    below threshold"""
    average_bids, average_asks = calculate_asks_and_bids(bid_intervals, ask_intervals)
    summed_bid_volume, summed_ask_volume = calculate_volume_changes(bid_depths_intervals, ask_depths_intervals)

    delta_bids, delta_asks, delta_bid_volume, delta_ask_volume = calculate_deltas(average_bids, average_asks,
                                                                                  summed_bid_volume, summed_ask_volume)
    delta_bids = list(delta_bids)
    delta_asks = list(delta_asks)
    delta_bid_volume = list(delta_bid_volume)
    delta_ask_volume = list(delta_ask_volume)

    bid_decision_vector = []
    ask_decision_vector = []
    bid_depth_decision_vector = []
    ask_depth_decision_vector = []


    for delta_bid in delta_bids:
        if delta_bid > 0:
            bid_decision_vector.append(1)
        elif delta_bid < 0:
            bid_decision_vector.append(-1)
        else:
            bid_decision_vector.append(0)

    for delta_ask in delta_asks:
        if delta_ask > 0:
            ask_decision_vector.append(1)
        elif delta_ask < 0:
            ask_decision_vector.append(-1)
        else:
            ask_decision_vector.append(0)

    for bid_depth in delta_bid_volume:
        if bid_depth > 0:
            bid_depth_decision_vector.append(1)
        elif bid_depth < 0:
            bid_depth_decision_vector.append(-1)
        else:
            bid_depth_decision_vector.append(0)

    for ask_depth in delta_ask_volume:
        if ask_depth > 0:
            ask_depth_decision_vector.append(1)
        elif ask_depth < 0:
            ask_depth_decision_vector.append(-1)
        else:
            ask_depth_decision_vector.append(0)

    bid_volume_count = np.sum(bid_depth_decision_vector)
    ask_volume_count = np.sum(ask_depth_decision_vector)
    bid_count = np.sum(bid_decision_vector)
    ask_count = np.sum(ask_decision_vector)

    return bid_volume_count, ask_volume_count, bid_count, ask_count


def make_trade_decision(ticker, bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals,
                        vol_measure, vol_confidence, base_size,
                        num_buys, num_sells, av_buy, av_sell):

    print('Making trade decision based on bid/ask volume')
    bid_volume_count, ask_volume_count, av_bid_count, av_ask_count = calc_decision_metrics(bid_intervals, bid_depths_intervals,
                                                                                     ask_intervals,
                                                                                     ask_depths_intervals)

    print( 'bid vol', bid_volume_count, 'av bid', av_bid_count, 'ask vol', ask_volume_count, 'av ask', av_ask_count)
    ticker_price = float(ticker)

    vol_adjust = vol_confidence * vol_measure
    print('vol_adjust', vol_adjust)


    if vol_adjust > 0:
        if bid_volume_count <= 0 and av_bid_count > 0:
            price = ticker_price + vol_adjust
            price = round(price, 2)

            if av_buy < price:
                if num_buys > num_sells:
                    amount = num_buys - num_sells
                else:
                    amount = base_size
            else:
                amount = base_size

            return ['sell', str(price), str(amount)]

        if bid_volume_count >= 0 and av_bid_count > 0:
            price = ticker_price - vol_adjust
            price = round(price,2)
            if av_sell > price:
                if num_sells > num_buys:
                    if (num_sells  - num_buys)*price*0.0025 + price < av_sell:
                        amount = num_sells - num_buys
                    else:
                        amount = base_size
                else:
                    amount = base_size
            else:
                amount = base_size

            fees = price * amount * 0.0025
            if price + fees < ticker_price:
                return ['buy', str(price), str(amount)]
            else:
                return ['hold', None, None]


        if bid_volume_count > 0 and av_bid_count > 0 and ask_volume_count > 0 and av_ask_count > 0:
            price = ticker_price
            price = round(price, 2)
            amount = num_sells
            return ['buy', str(price), str(amount)]

        if bid_volume_count < 0 and av_bid_count < 0 and ask_volume_count < 0 and av_ask_count < 0:
            price = ticker_price
            price = round(price, 2)
            amount = num_buys
            return ['sell', str(price), str(amount)]

        else:
            return ['hold', None, None]


    else:
        return ['hold', None, None]



def sort_messages(ticker, order_book_messages, order_book_skim):
    """Sorts order book output into easily manageable lists"""

    upper = ticker * (1 + order_book_skim)
    lower = ticker * (1 - order_book_skim)

    bid_list = order_book_messages['bids']
    ask_list = order_book_messages['asks']

    float_bids = []
    float_asks = []
    for bid in bid_list:
        float_bids.append([float(bid[0]), float(bid[1])])


    for ask in ask_list:
        float_asks.append([float(ask[0]), float(ask[1])])

    skimmed_bids = []
    for bid in float_bids:
        if bid[0] >= lower and bid[0] <= upper:
            skimmed_bids.append(bid)

    skimmed_asks = []
    for ask in float_asks:
        if ask[0] >= lower and ask[0] <= upper:
            skimmed_asks.append(ask)


    bids = [i[0] for i in skimmed_bids]
    asks = [j[0] for j in skimmed_asks]
    bid_depths = [i[1] for i in skimmed_bids]
    ask_depths = [j[1] for j in skimmed_asks]
    return bids, bid_depths, asks, ask_depths

def check_order_info(bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals):
    if len(bid_intervals) ==0 or len(bid_depths_intervals) ==0 or len(ask_intervals)==0 or ask_depths_intervals == 0:
        return False
    else:
        return True


class Bot(object):


    def __init__(self, key, secret, passphrase, product):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.product = product
        self.websocket_client = WebsocketClient()
        self.order_book = OrderBook(product_id=product)
        self.auth_client = AuthenticatedClient(key, secret, passphrase)
        self.public_client = PublicClient()
        self.sells = []
        self.buys = []
        self.sell_tracker = 0
        self.buy_tracker = 0
        self.sell_fees = 0
        self.buy_fees = 0
        self.num_buys = 0
        self.num_sells = 0
        self.av_sell = 0
        self.av_buy = 0
        self.last_buy = 0
        self.last_sell = 0
        self.current_balance = 0
        self.ticker_tracker = []


    def get_order_info(self, ticker, number_measures, length_measures, order_book_skim):

        bid_intervals = []
        bid_depths_intervals = []
        ask_intervals = []
        ask_depths_intervals = []
        count = 1
        while count <= number_measures:
            print('Volume check %s' % count)
            time.sleep(length_measures)
            current_order_book = self.order_book.get_current_book()
            bids, bid_depths, asks, ask_depths = sort_messages(ticker, current_order_book, order_book_skim)
            bid_intervals.append(bids)
            ask_intervals.append(asks)
            bid_depths_intervals.append(bid_depths)
            ask_depths_intervals.append(ask_depths)
            count += 1

        return bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals


    def check_volatility(self, volatility_interval, num_volatility_measures):
        if len(self.ticker_tracker) > num_volatility_measures + 1:
            delta_price = np.diff(self.ticker_tracker)
            vol_measure = np.average(delta_price[-num_volatility_measures:])

        else:
            vol_measure = 0

        return abs(vol_measure)


    def start_order_book(self):
        self.order_book.start()


    def order_book_repeat_sample(self, duration, order_book_skim):

        with open('crypto_data.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter='\t', lineterminator='\n', )
            header = ['datetime', 'ticker price', 'average bid', 'average ask', 'bid volume', 'ask volume']
            writer.writerow(header)
            while True:
                ticker = float(self.public_client.get_product_ticker(self.product)['price'])
                current_order_book = self.order_book.get_current_book()
                bids, bid_depths, asks, ask_depths = sort_messages(ticker, current_order_book, order_book_skim)

                if len(bids) != 0 and len(asks)!= 0 and len(bid_depths)!= 0 and len(ask_depths) != 0:
                    print(bids[1])
                    print(bids[2])
                    av_bid = np.average(bids)
                    av_ask = np.average(asks)
                    total_bids = np.sum(bid_depths)
                    total_asks = np.sum(ask_depths)
                else:
                    av_bid = 'N/A'
                    av_ask = 'N/A'
                    total_bids = 'N/A'
                    total_asks = 'N/A'
                print('Average bid', av_bid)
                print('Average ask', av_ask)
                print('total bid volume', total_bids)
                print('total ask volume', total_asks)
                data = [datetime.datetime.now(), ticker, av_bid, av_ask, total_bids, total_asks]
                writer.writerow(data)
                time.sleep(duration)




    def track_performance(self, string_id, transaction):

        if 'side' in transaction.keys():
            if transaction['side'] == 'sell':
                self.sells.append(transaction['id'])
            if transaction['side'] == 'buy':
                self.buys.append(transaction['id'])


    def evaluate_performance(self):

        print('Current sell orders:')
        for sell in self.sells:
            order = self.auth_client.get_order(sell)

            if 'message' in order.keys():
                self.sells.remove(sell)

            else:
                print('price:', order['price'], 'size:', order['size'])

                if order['settled'] == True:
                    self.sell_tracker += float(order['size']) * float(order['price'])
                    self.sell_fees += float(order['fill_fees'])
                    self.num_sells += float(order['size'])
                    self.sells.remove(sell)

        print('Current buy orders:')
        for buy in self.buys:
            order = self.auth_client.get_order(buy)

            if 'message' in order.keys():
                self.buys.remove(buy)

            else:

                print('price:', order['price'], 'size:', order['size'])
                if order['settled'] == True:
                    self.buy_tracker += float(order['size']) * float(order['price'])
                    self.buy_fees += float(order['fill_fees'])
                    self.num_buys += float(order['size'])
                    self.buys.remove(buy)

        if self.num_buys > 0:
            self.av_buy = self.buy_tracker/self.num_buys

        if self.num_sells > 0:
            self.av_sell = self.sell_tracker/self.num_sells

        print('Number of buys:', self.num_buys)
        print('Buy USD volume:', self.buy_tracker)
        print('Number of sells:', self.num_sells)
        print('Sell USD volume:', self.sell_tracker)
        print('Net fees:', self.sell_fees + self.buy_fees)
        print('Net USD profit:', self.sell_tracker - self.buy_tracker - self.sell_fees - self.buy_fees)
        print('Av sell:', self.av_sell)
        print('Av buy:', self.av_buy)


    def check_existing_sells(self, current_order_price, current_order_size, vol_measure):

        new_average = (self.sell_tracker  + current_order_price * current_order_size) / (self.num_sells + current_order_size)


        print('new av', new_average)

        if len(self.sells) > 0:

            if new_average > self.av_buy:

                if self.num_buys > 0 :

                    for sell in self.sells:

                        order = self.auth_client.get_order(sell)
                        order_price = float(order['price'])

                        if 'message' in order.keys():
                            self.buys.remove(sell)
                            return 'keep'

                        else:
                            if self.av_buy < current_order_price:

                                if order_price < current_order_price - vol_measure:
                                    self.buys.remove(sell)
                                    self.auth_client.cancel_order(order['id'])
                                    return 'keep'

                                else:
                                    return 'abandon'

                            else:
                                return 'abandon'

                else:

                    if current_order_price > self.last_buy:

                        return 'keep'

                    else:
                        return 'abandon'


            else:
                return 'abandon'

        else:
            return 'keep'


    def check_existing_buys(self, current_order_price, current_order_size, vol_measure):

        fees = 0.0025 * (current_order_price * current_order_size)

        current_plus_fees = current_order_price + fees

        new_average = (self.buy_tracker  + current_order_price * current_order_size + fees) / (self.num_buys + current_order_size)


        if len(self.buys) > 0:

            if new_average < self.av_sell:

                if self.num_sells > 0:

                    for buy in self.buys:

                        order = self.auth_client.get_order(buy)

                        order_plus_fees = float(order['price']) + 0.0025 * float(order['price']) * float(order['size'])

                        if 'message' in order.keys():
                            self.buys.remove(buy)
                            return 'keep'

                        else:
                            if self.av_sell > order_plus_fees :

                                if order_plus_fees > current_plus_fees + vol_measure :
                                    self.buys.remove(buy)
                                    self.auth_client.cancel_order(order['id'])
                                    return 'keep'


                                else:
                                    return 'abandon'


                            else:
                                return 'abandon'

                else:

                    if current_order_price < self.last_sell:

                        return 'keep'


                    else:

                        return 'abandon'

            else:
                return 'abandon'

        else:
            return 'keep'




    def execute_volume_strategy(self, number_measures, length_measures, order_book_skim, base_size, volatility_interval,
                                num_volatility_measures, vol_confidence, run_minutes):

        t_end = time.time() + 60 * run_minutes
        while time.time() < t_end:
            print('time remaining', t_end - time.time())
#
#        while True:
            vol_measure = self.check_volatility(volatility_interval, num_volatility_measures)

    #        accounts = self.auth_client.get_accounts()

    #        balance = 0

       #     for account in accounts:
       #         if account['currency'] == self.product:
       #             balance = account['balance']


        #    print('balance', balance)



            ticker = float(self.public_client.get_product_ticker(self.product)['price'])


            bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals = self.get_order_info(ticker,
                                                                                                      number_measures,
                                                                                                      length_measures,
                                                                                                      order_book_skim)

            while check_order_info(bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals) == False:
                time.sleep(10)
                bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals = self.get_order_info(ticker,
                                                                                                          number_measures,
                                                                                                          length_measures,
                                                                                                          order_book_skim)




            ticker = float(self.public_client.get_product_ticker(self.product)['price'])
            self.ticker_tracker.append(ticker)
            self.check_volatility(volatility_interval, num_volatility_measures)

            decision = make_trade_decision(ticker, bid_intervals, bid_depths_intervals, ask_intervals, ask_depths_intervals,
                                           vol_measure, vol_confidence, base_size,
                                           self.num_buys, self.num_sells, self.av_buy, self.av_sell)


            if decision[0] == 'buy':
                place_decision = self.check_existing_buys(float(decision[1]), float(decision[2]), vol_measure)
                if place_decision == 'keep':

                    print('Placing buy order...')
                    print('price', decision[1], 'size', decision[2])
                    buy = self.auth_client.buy(price= decision[1], size= decision[2],product_id=self.product)
                    self.last_buy = float(decision[1])
                    self.track_performance('buy', buy)
                    time.sleep(10)

                if place_decision == 'abandon':
                    'Waiting on existing trades'

            elif decision[0] == 'sell':
                place_decision = self.check_existing_sells(float(decision[1]), float(decision[2]), vol_measure)
                if place_decision == 'keep':

                    print('Placing sell order...')
                    print('price', decision[1], 'size', decision[2])
                    sell = self.auth_client.sell(price= decision[1], size=decision[2], product_id=self.product)
                    self.last_sell = float(decision[1])
                    self.track_performance('sell', sell)
                    time.sleep(10)

                if place_decision == 'abandon':
                    'Waiting on existing trades'


            elif decision[0] == 'hold':
                print('Holding...')


            else:
                print('Problem...')

            self.evaluate_performance()

        print('test complete')
        print()
self.evaluate_performance()