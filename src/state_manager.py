import time

from enum import Enum



class BotState(Enum):

    SEARCHING = 1

    TRADING = 2



class StateManager:

    def __init__(self, exchange):

        self.exchange = exchange  # Store the exchange instance

        self.current_state = BotState.SEARCHING

        self.last_position_check = 0

        self.position_check_interval = 180  # 3 minutes in seconds



    def display_open_positions(self):

        try:

            positions = self.exchange.fetch_positions()  # Use the exchange instance to fetch positions

            print("\nOpen Positions:")

            for position in positions:

                if float(position['contracts']) != 0:

                    print(f"Symbol: {position['symbol']}, Side: {'Long' if position['side'] == 'long' else 'Short'}, Amount: {position['contracts']}")

        except Exception as e:

            print(f"Error fetching positions: {e}")



    def check_and_display_positions(self):

        current_time = time.time()

        if current_time - self.last_position_check >= self.position_check_interval:

            self.display_open_positions()

            self.last_position_check = current_time



    def get_open_positions(self):

        """Fetch and return open positions."""

        try:

            return self.exchange.fetch_positions()  # Use the exchange instance

        except Exception as e:

            print(f"Error fetching open positions: {e}")

            return []
