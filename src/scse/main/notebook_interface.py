from scse.controller import miniscot as miniSCOT


class miniSCOTnotebook():
    DEFAULT_START_DATE = '2019-01-01'
    DEFAULT_TIME_INCREMENT = 'daily'
    DEFAULT_HORIZON = 100
    DEFAULT_SIMULATION_SEED = 12345
    DEFAULT_ASIN_SELECTION = 1
    DEFAULT_PROFILE = 'power_supply'
    DEFAULT_FLEXIBLE_CAPACITY = 1500000
    DEFAULT_STATIC_CAPACITY = 5500000
    DEFAULT_RENEWABLE_OFFSET = 500000
    DEFAULT_RENEWABLE_SCALE = 2500000
    DEFAULT_STATIC_PRICE = 113
    DEFAULT_FLEXIBLE_PRICE = 45
    DEFAULT_VARIABLE_PRICE = 40
    DEFAULT_MAX_DEMAND = 7000000
    DEFAULT_EXTRA_POWER = 2

    def __init__(self):
        self.start(simulation_seed=self.DEFAULT_SIMULATION_SEED,
                   start_date=self.DEFAULT_START_DATE,
                   time_increment=self.DEFAULT_TIME_INCREMENT,
                   time_horizon=self.DEFAULT_HORIZON,
                   asin_selection=self.DEFAULT_ASIN_SELECTION,
                   flexible_capacity = self.DEFAULT_FLEXIBLE_CAPACITY,
                   static_capacity = self.DEFAULT_STATIC_CAPACITY,
                   renewable_offset = self.DEFAULT_RENEWABLE_OFFSET,
                   renewable_scale = self.DEFAULT_RENEWABLE_SCALE,
                   max_demand = self.DEFAULT_MAX_DEMAND,
                   static_price = self.DEFAULT_STATIC_PRICE,
                   flexible_price = self.DEFAULT_FLEXIBLE_PRICE,
                   variable_price = self.DEFAULT_VARIABLE_PRICE,
                   extra_power = self.DEFAULT_EXTRA_POWER,
                   profile=self.DEFAULT_PROFILE)

    def start(self, **run_parameters):
        self.horizon = run_parameters['time_horizon']
        self.actions = []
        self.breakpoints = []

        self.env = miniSCOT.SupplyChainEnvironment(**run_parameters)

        self.context, self.state = self.env.get_initial_env_values()
        self.env.reset_agents(self.context, self.state)

    def next(self):
        """Execute a single time unit."""
        self.state, self.actions, self.reward = self.env.step(self.state, self.actions)

    def run(self):
        """Run simulation until the first break-point or, if none are enabled, until the end of time (the specified horizon)."""
        for t in range(self.state['clock'], self.horizon):
            if t in self.breakpoints:
                break
            else:
                self.state, self.actions, self.reward = self.env.step(self.state, self.actions)


m = miniSCOTnotebook()

# Can use the following line to step through simulation
# m.next()

# Example below of injecting an action into the simulation.  Note this will raise an error since CHA1 doesn't have 5 units onhand!
# action={"schedule": 0, "type": "inbound_shipment", "asin": "9780465024759", "origin": "Manufacturer", "destination": "Newsvendor", "quantity": 5}
# actions = [action]
# m.env.step(m.state, actions)
