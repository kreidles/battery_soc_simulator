"""Apache Beam Pipeline to get estimated capacity using solar_data_tools
"""
import argparse
import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import logging
from typing import Any, Dict, List
from socsim.models.simulation_config import StateOfChargeSimulationConfig
from socsim.transformers.state_of_charge import SimulateStateOfCharge


def cross_join(left, rights):
    for x in rights:
        yield left, x


def run(sim_config_path: str, time_series_path: str, output_path: str, beam_args: List[str] = None) -> None:
    """Simplified pipeline to simulate battery state of charge given a 24 hour PV power time series"""
    options = PipelineOptions(beam_args)

    with beam.Pipeline(options=options) as pipeline:
        # read simulation configuration(s) from JSON
        simulation_configs = (
            pipeline
            | "Read simulation params from JSON" >> beam.io.ReadFromText(file_pattern=sim_config_path)
            | "Parse to sim config object" >> beam.FlatMap(lambda line: StateOfChargeSimulationConfig.from_text_line(line))
        )

        # read PV power time series from JSON, pair with simulation params, and
        (
            pipeline
            | "Read PV power" >> beam.io.ReadFromText(file_pattern=time_series_path)
            | "Parse into list" >> beam.FlatMap(lambda line: json.loads(line))
            | "Cross join with sim config" >> beam.FlatMap(cross_join, rights=beam.pvalue.AsIter(simulation_configs))
            | "Simulate SOC" >> beam.ParDo(SimulateStateOfCharge())
            | "Write results to JSON" >> beam.io.WriteToText(file_path_prefix=output_path)
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_file",
        help="Output file path"
    )
    parser.add_argument(
        "--sim_config_path",
        help="path to simulation config JSON file"
    )
    parser.add_argument(
        "--time_series_path",
        help="path to power time series JSON file"
    )
    args, beam_args = parser.parse_known_args()

    run(
        sim_config_path=args.sim_config_path,
        time_series_path=args.time_series_path,
        output_path=args.output_file,
        beam_args=beam_args,
    )
