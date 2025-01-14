from __future__ import print_function
import sys
import argparse
import cmd2
import pprint
import networkx as nx
from scse.controller import miniscot as miniSCOT

class MiniSCOTDebuggerApp(cmd2.Cmd):
    _DEFAULT_START_DATE = '2019-01-01'
    _DEFAULT_TIME_INCREMENT = 'daily'
    _DEFAULT_HORIZON = 100
    _DEFAULT_SIMULATION_SEED = 12345
    _DEFAULT_ASIN_SELECTION = 1 # or use an integer value to select the number of asins
    _DEFAULT_PROFILE = 'power_supply'
    _DEFAULT_FLEXIBLE_CAPACITY = 1500000
    _DEFAULT_STATIC_CAPACITY = 5500000
    _DEFAULT_RENEWABLE_OFFSET = 500000
    _DEFAULT_RENEWABLE_SCALE = 2500000
    _DEFAULT_MAX_DEMAND = 7000000
    _DEFAULT_STATIC_PRICE = 113 # avg coal price US
    _DEFAULT_FLEXIBLE_PRICE = 45 # avg gas price US w/o carbon capture, 70 with
    _DEFAULT_VARIABLE_PRICE = 40 # avg solar price US: 43, avg onshore wind price US: 38
    _DEFAULT_EXTRA_POWER = 2 # 

    def __init__(self, **args):
        super().__init__(args)
        self.intro = self.colorize("Welcome to miniSCOT - your Supply Chain in a bottle.", 'cyan')

        self._start(simulation_seed = self._DEFAULT_SIMULATION_SEED,
                    start_date = self._DEFAULT_START_DATE,
                    time_increment = self._DEFAULT_TIME_INCREMENT,
                    time_horizon = self._DEFAULT_HORIZON,
                    asin_selection = self._DEFAULT_ASIN_SELECTION,
                    flexible_capacity = self._DEFAULT_FLEXIBLE_CAPACITY,
                    static_capacity = self._DEFAULT_STATIC_CAPACITY,
                    max_demand = self._DEFAULT_MAX_DEMAND,
                    renewable_offset = self._DEFAULT_RENEWABLE_OFFSET,
                    renewable_scale = self._DEFAULT_RENEWABLE_SCALE,
                    profile = self._DEFAULT_PROFILE,
                    static_price = self._DEFAULT_STATIC_PRICE,
                    flexible_price = self._DEFAULT_FLEXIBLE_PRICE,
                    variable_price = self._DEFAULT_VARIABLE_PRICE,
                    extra_power = self._DEFAULT_EXTRA_POWER)

        self._set_prompt()

    def _set_prompt(self):
        self.prompt = self.colorize("miniSCOT (t = {!r}) $ ".format(self._state['clock']), 'cyan')

    def postcmd(self, stop, line):
        self._set_prompt()
        return stop

    def _start(self, **run_parameters):     
        self._horizon = run_parameters['time_horizon']
        self._actions = []
        self._breakpoints = []

        self._env = miniSCOT.SupplyChainEnvironment(**run_parameters)

        self._context, self._state = self._env.get_initial_env_values()
        self._env.reset_agents(self._context, self._state)

    param_parser = argparse.ArgumentParser()
    param_parser.add_argument('-start_date', help="simulation will at date 'yyyy-mm-dd' (default 2019-01-01)", type=str, default=_DEFAULT_START_DATE)
    param_parser.add_argument('-time_increment', help="increment time daily or hourly (default 'daily')", type=str, default=_DEFAULT_TIME_INCREMENT)
    param_parser.add_argument('-horizon', help="total time units to simulate (default 100)", type=int, default=_DEFAULT_HORIZON)
    param_parser.add_argument('-seed', help="simulation random seed (default 12345)", type=int, default=_DEFAULT_SIMULATION_SEED)
    param_parser.add_argument('-asin_selection', help="number of ASINs to use (default 10)", type=int, default=_DEFAULT_ASIN_SELECTION)
    param_parser.add_argument('-profile', help="profile (default minimal)", type=str, default=_DEFAULT_PROFILE)
    param_parser.add_argument('-flexible_capacity', help="capacity of the flexible power producers", type=int, default=_DEFAULT_FLEXIBLE_CAPACITY)
    param_parser.add_argument('-static_capacity', help="capacity of the static power producers", type=int, default=_DEFAULT_STATIC_CAPACITY)
    param_parser.add_argument('-max_demand', help="average demand in this market", type=int, default=_DEFAULT_MAX_DEMAND)
    param_parser.add_argument('-static_price', help="static price (e.g. coal)", type=int, default = _DEFAULT_STATIC_PRICE)
    param_parser.add_argument('-flexible_price', help="flexible price (e.g. gas)", type=int, default = _DEFAULT_FLEXIBLE_PRICE)
    param_parser.add_argument('-variable_price', help="variable price (e.g. renewables)", type=int, default = _DEFAULT_VARIABLE_PRICE)
    param_parser.add_argument('-renewable_offset', help="renewable offset", type=float, default=_DEFAULT_RENEWABLE_OFFSET)
    param_parser.add_argument('-renewable_scale', help="renewable scale", type=float, default=_DEFAULT_RENEWABLE_SCALE)
    param_parser.add_argument('-extra_power', help="extra power for backup", type=float, default=_DEFAULT_EXTRA_POWER)


    #param_parser.add_argument('-asin', help="list of ASINs.", action='append', default=_DEFAULT_ASIN_LIST)

    @cmd2.with_argparser(param_parser)
    def do_start(self, args):
        """Start (or restart) environment, resetting all variables and state."""
        self._start(simulation_seed = args.seed,
                    start_date = args.start_date,
                    time_increment = args.time_increment,
                    time_horizon = args.horizon,
                    asin_selection = args.asin_selection,
                    flexible_capacity = args.flexible_capacity,
                    static_capacity = args.static_capacity,
                    max_demand = args.max_demand,
                    static_price = args.static_price,
                    flexible_price = args.flexible_price,
                    variable_price = args.variable_price,
                    renewable_offset = args.renewable_offset,
                    renewable_scale = args.renewable_scale,
                    extra_power = args.extra_power,
                    profile = args.profile)

    def do_next(self, arguments):
        """Execute a single time unit."""
        self._state, self._actions, self._reward = self._env.step(self._state, self._actions)

    def do_run(self, arguments):
        """Run simulation until the first break-point or, if none are enabled, until the end of time (the specified horizon)."""
        for t in range(self._state['clock'], self._horizon):
            if t in self._breakpoints:
                break
            else:
                self._state, self._actions, self._reward = self._env.step(self._state, self._actions)

    def do_print(self, args):
        """Print variables."""
        msg = ""
        if args == 'nodes':
            msg = self._print_nodes()
        elif args == 'edges':
            msg = self._print_edges()
        elif args == 'actions':
            msg = pprint.pformat(self._actions)
        elif args == 'orders':
            msg = pprint.pformat(self._state['customer_orders'])
        elif args == "POs":
            msg = pprint.pformat(self._state['purchase_orders'])
        elif args == "reward":
            msg = pprint.pformat(self._reward)
        else:
            msg = """Valid options are: nodes | edges | actions | orders | POs | reward"""

        self.poutput(msg)

    def _print_nodes(self):
        return pprint.pformat([(node, node_data) for node, node_data in self._state['network'].nodes(data = True)])

    def _print_edges(self):
        return pprint.pformat([(source_node, dest_node, edge_data) for source_node, dest_node, edge_data in self._state["network"].edges(data = True)])

    bp_parser = argparse.ArgumentParser()
    bp_parser.add_argument('time', help='time when to break')

    @cmd2.with_argparser(bp_parser)
    def do_breakpoint(self, args):
        """Set break-point for the specified time-step."""
        self._breakpoints.append(int(args.time))

def main():
    app = MiniSCOTDebuggerApp()
    sys.exit(app.cmdloop())


if __name__ == "__main__":
    main()
