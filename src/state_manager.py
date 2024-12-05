import time

from enum import Enum

import json



class BotState(Enum):

    SEARCHING = 1

    TRADING = 2



class StateManager:

    def __init__(self, exchange):

        self.exchange = exchange

        self.current_state = BotState.SEARCHING

        self.last_position_check = 0

        self.position_check_interval = 180  # 3 minutes in seconds



    def get_account_positions(self, currency='BTC'):

        """Fetch account positions for a given currency."""

        try:

            params = {'currency': currency}

            response = self.exchange.privateGetAccountsAccountPositions(params=params)



            # Ensure response is a dictionary

            if isinstance(response, str):

                response = json.loads(response)



            # Check if 'data' exists in the response and is a dictionary

            if 'data' not in response or not isinstance(response['data'], dict):

                print("Unexpected API response structure: 'data' key not found or not a dictionary")

                return []



            # Access the positions list from the data dictionary

            positions = response['data'].get('positions', [])

            

            # Check if positions is a list

            if not isinstance(positions, list):

                print("Unexpected structure for 'positions'. Expected a list.")

                return []



            return positions

        except json.JSONDecodeError:

            print("Error decoding JSON response")

            return []

        except Exception as e:

            print(f"Error fetching account positions: {e}")

            return []



    def get_open_positions(self, symbol):

        """Extract open positions for a given symbol from account positions."""

        try:

            account_positions = self.get_account_positions()



            if not isinstance(account_positions, list):

                print("Unexpected type for account_positions. Expected list.")

                return []



            open_positions = [

                p for p in account_positions 

                if isinstance(p, dict) and 

                p.get('symbol') == symbol and 

                float(p.get('size', 0)) != 0

            ]

            return open_positions

        except Exception as e:

            print(f"Error extracting open positions: {e}")

            return []



    def display_open_positions(self, symbol):

        """Display open positions for a given symbol along with PnL and leverage."""

        try:

            positions = self.get_open_positions(symbol)

            print("\nOpen Positions:")

            

            if not positions:

                print("No open positions found.")

                return 0

            

            for position in positions:

                pnl = float(position.get('cumClosedPnlEv', 0)) / 1e8  # Adjusting based on expected scale

                leverage = float(position.get('leverage', 0))

                

                print(f"Symbol: {position.get('symbol', 'N/A')}, "

                      f"Side: {'Long' if float(position.get('size', 0)) > 0 else 'Short'}, "

                      f"Size: {abs(float(position.get('size', 0)))}, "

                      f"Entry Price: {position.get('avgEntryPrice', 'N/A')}, "

                      f"PnL: {pnl:.2f}, "

                      f"Leverage: {leverage:.2f}")

            

            return len(positions)

        except Exception as e:

            print(f"Error displaying positions: {e}")

            return 0



    def check_and_display_positions(self, symbol):

        """Check and display open positions at specified intervals."""

        current_time = time.time()

        if current_time - self.last_position_check >= self.position_check_interval:

            open_position_count = self.display_open_positions(symbol)

            if open_position_count >= 5:

                print("Monitoring ongoing due to sufficient open positions.")

                self.current_state = BotState.TRADING

            else:

                print("Fewer than 5 open positions. Looking for new trading opportunities...")

                self.current_state = BotState.SEARCHING

            self.last_position_check = current_time
