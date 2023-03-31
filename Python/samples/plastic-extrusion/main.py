import json
import os
import random

from bonsai_common import SimulatorSession, Schema
import dotenv
from microsoft_bonsai_api.simulator.client import BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import SimulatorInterface

from sim import extrusion_model as em
from sim import units

import argparse
import datetime
import pathlib

# time step (seconds) between state updates
Δt = 1

LOG_PATH = "logs"


def ensure_log_dir(log_full_path):
    """
    Ensure the directory for logs exists — create if needed.
    """
    print(f"logfile: {log_full_path}")
    logs_directory = pathlib.Path(log_full_path).parent.absolute()
    print(f"Checking {logs_directory}")
    if not pathlib.Path(logs_directory).exists():
        print(
            "Directory does not exist at {0}, creating now...".format(
                str(logs_directory)
            )
        )
        logs_directory.mkdir(parents=True, exist_ok=True)


class ExtruderSimulation(SimulatorSession):
    def __init__(self, config, log_data: bool = False, log_file_name: str = None):
        super().__init__(config)
        self.log_data = log_data
        if not log_file_name and log_data:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            log_file_name = current_time + "_extrusion_log.csv"

        self.log_full_path = os.path.join(LOG_PATH, log_file_name)
        ensure_log_dir(self.log_full_path)

    def reset(
        self,
        ω0_s: float = 1e-6,
        Δω0_s: float = 0,
        f0_c: float = 1e-6,
        Δf0_c: float = 0,
        T: float = units.celsius_to_kelvin(190),
        L0: float = 1 * 12 * units.METERS_PER_INCH,
        ε: float = 0.1 * units.METERS_PER_INCH,
    ):
        """
        Extruder model for simulation.

        Parameters
        ----------
        ω0_s : float, optional
            Initial screw angular speed (radians / second).
        Δω0_s : float, optional
            Initial change in screw angular speed (radians / second^2).
        f0_c : float, optional
            Initial cutter frequency (hertz).
        Δf0_c : float, optional
            Initial change in cutter frequency (1 / second^2).
        T : float, optional
            Initial temperature (Kelvin).
        L0 : float, optional
            Initial product length (meters).
        ε : float, optional
            Product tolerance (meters).
        """

        # angular speed of the extruder screw (radians / second)
        self.ω_s = ω0_s

        # change in angular speed of the extruder screw (radians / second^2)
        self.Δω_s = Δω0_s
        self.Δω_eff = self.Δω_s

        # frequency of the cutter (hertz)
        self.f_c = f0_c

        # change in cutter frequency (1 / second^2)
        self.Δf_c = Δf0_c
        self.Δf_eff = self.Δf_c

        # temperature (Kelvin)
        self.T = T

        self.L0 = L0
        self.ε = ε

        model = em.ExtrusionModel(
            ω=self.ω_s, Δω=self.Δω_s, f_c=self.f_c, T=self.T, Δt=Δt
        )

        self.T += model.ΔT

        # material flow rate (meters^3 / second)
        self.Q = model.Q_op

        # product length (meters)
        self.L = model.L

        # manufacturing yield, defined as the number of good parts
        # per iteration (dimensionless)
        self.yield_ = model.yield_

    def episode_start(self, config: Schema) -> None:
        self.reset(
            ω0_s=config.get("initial_screw_angular_speed"),
            Δω0_s=config.get("initial_screw_angular_acceleration"),
            f0_c=config.get("initial_cutter_frequency"),
            Δf0_c=config.get("initial_cutter_acceleration"),
            T=config.get("initial_temperature"),
        )

    def step(self):

        # add a small amount of random noise to the actions to avoid
        # the trivial solution of simply applying zero acceleration
        # on each iteration
        σ_max = 0.0001
        σ_s = random.uniform(-σ_max, σ_max)
        σ_c = random.uniform(-σ_max, σ_max)

        self.Δω_eff = self.Δω_s * (1 + σ_s)
        self.ω_s += Δt * self.Δω_eff

        self.Δf_eff = self.Δf_c * (1 + σ_c)
        self.f_c += Δt * self.Δf_eff

        model = em.ExtrusionModel(
            ω=self.ω_s, Δω=self.Δω_eff, f_c=self.f_c, T=self.T, Δt=Δt
        )

        self.T += model.ΔT

        # material flow rate (meters^3 / second)
        self.Q = model.Q_op

        # product length (meters)
        self.L = model.L

        # manufacturing yield, defined as the number of good parts
        # per iteration (dimensionless)
        self.yield_ = model.yield_

    def episode_step(self, action: Schema) -> None:
        self.Δω_s = action.get("screw_angular_acceleration")
        self.Δf_c = action.get("cutter_acceleration")

        self.step()

    def get_state(self):
        return {
            "screw_angular_speed": self.ω_s,
            "screw_angular_acceleration": self.Δω_eff,
            "cutter_frequency": self.f_c,
            "cutter_acceleration": self.Δf_eff,
            "temperature": self.T,
            "product_length": self.L,
            "flow_rate": self.Q,
            "yield": self.yield_,
        }

    def halted(self) -> bool:
        return False

    def get_interface(self) -> SimulatorInterface:
        """Register sim interface."""

        with open("interface.json", "r") as infile:
            interface = json.load(infile)

        return SimulatorInterface(
            name=interface["name"],
            timeout=interface["timeout"],
            simulator_context=self.get_simulator_context(),
            description=interface["description"],
        )

    def log_iterations(
        self, state, action, config, episode: int = 0, iteration: int = 1
    ):
        """Log iterations during training to a CSV.

        Parameters
        ----------
        state : Dict
        action : Dict
        episode : int, optional
        iteration : int, optional
        """

        import pandas as pd

        def add_prefixes(d, prefix: str):
            return {f"{prefix}_{k}": v for k, v in d.items()}

        state = add_prefixes(state, "state")
        action = add_prefixes(action, "action")
        config = add_prefixes(config, "config")
        data = {**state, **action, **config}
        data["episode"] = episode
        data["iteration"] = iteration
        log_df = pd.DataFrame(data, index=[0])

        if os.path.exists(self.log_full_path):
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="a", header=False, index=False
            )
        else:
            log_df.to_csv(
                path_or_buf=self.log_full_path, mode="w", header=True, index=False
            )


def main():

    parser = argparse.ArgumentParser(description="Bonsai and Simulator Integration...")

    parser.add_argument(
        "--log-iterations",
        action="store_true",
        default=False,
        help="Log iterations during training",
    )

    args = parser.parse_args()

    workspace = os.getenv("SIM_WORKSPACE")
    access_key = os.getenv("SIM_ACCESS_KEY")

    # values in `.env`, if they exist, take priority over environment variables
    dotenv.load_dotenv(".env", override=True)

    if workspace is None:
        raise ValueError("The Bonsai workspace ID is not set.")
    if access_key is None:
        raise ValueError("The access key for the Bonsai workspace is not set.")

    config = BonsaiClientConfig(workspace=workspace, access_key=access_key)
    extruder_sim = ExtruderSimulation(config=config, log_data=args.log_iterations)

    extruder_sim.reset()

    episode = 0
    iteration = 0
    config = None
    while extruder_sim.run():
        event = extruder_sim._last_event
        if event is None:
            continue

        if extruder_sim.log_data:
            if event.type == "EpisodeStart":
                episode += 1
                config = event.episode_start.config

            elif event.type == "EpisodeStep":
                iteration += 1
                extruder_sim.log_iterations(
                    state=extruder_sim.get_state(),
                    action=event.episode_step.action,
                    config=config,
                    episode=episode,
                    iteration=iteration,
                )

            elif event.type == "EpisodeFinish":
                iteration = 0


if __name__ == "__main__":
    main()
