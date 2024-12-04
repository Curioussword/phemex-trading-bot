import time

from enum import Enum



class BotState(Enum):

    SEARCHING = 1

    TRADING = 2



class StateManager:

    def __init__(self, exchange):

        self.exchange = exchange

        self.current_state = BotState.SEARCHING

        self.last_position_check = 0

        self.position_check_interval = 180  # 3 minutes in seconds



    def get_open_positions(self):

        """Fetch and return open positions."""

        try:

            all_positions = self.exchange.fetch_positions(params={'settle': 'USD'})

            open_positions = [p for p in all_positions if float(p['contracts']) > 0]

            return open_positions

        except Exception as e:

            print(f"Error fetching open positions: {e}")

            return []



    def display_open_positions(self):

        try:

            positions = self.get_open_positions()

            print("\nOpen Positions:")

            for position in positions:

                print(f"Symbol: {position['symbol']}, Side: {position['side'].capitalize()}, Amount: {position['contracts']}")

        except Exception as e:

            print(f"Error displaying positions: {e}")



    def check_and_display_positions(self):

        current_time = time.time()

        if current_time - self.last_position_check >= self.position_check_interval:

            self.display_open_positions()

            self.last_position_check = current_time
