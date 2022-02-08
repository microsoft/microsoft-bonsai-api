#!/usr/bin/env python3

from microsoft_bonsai_api.simulator.client import BonsaiConnector
from sim.simulator_model import SimulatorModel


def main():
    """
    Creates a Bonsai simulator session and executes Bonsai episodes.
    """
    bonsai_conn = BonsaiConnector(SimulatorModel())
    bonsai_conn.event_loop()


if __name__ == "__main__":
    main()
