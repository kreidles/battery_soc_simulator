"""Apache Beam Pipeline to get estimated capacity using solar_data_tools
"""
import argparse
import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import logging
from typing import Any, Dict, List
from socsim.models.simulation_config import StateOfChargeSimulationConfig, simulation_config_from_text_line
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
            | "Parse to sim config object" >> beam.FlatMap(simulation_config_from_text_line)
        )

        # read PV power time series from JSON, pair with simulation params, and
        (
            pipeline
            | "Read PV power" >> beam.io.ReadFromText(file_pattern=time_series_path)
            | "Parse into list" >> beam.Map(json.loads)
            | "Cross join with sim config" >> beam.FlatMap(cross_join, rights=beam.pvalue.AsIter(simulation_configs))
            | "Simulate SOC" >> beam.ParDo(SimulateStateOfCharge())
            | "Write results to JSON" >> beam.io.WriteToText(file_path_prefix=output_path)
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_file",
        help="Output file path",
        default="../../tests/data/results.json"
    )
    parser.add_argument(
        "--sim_config_path",
        help="path to simulation config JSON file",
        default="../../tests/data/simulation_config.ndjson"
    )
    parser.add_argument(
        "--time_series_path",
        help="path to power time series JSON file",
        default="../../tests/data/power_ts.ndjson"
    )
    args, beam_args = parser.parse_known_args()

    run(
        sim_config_path=args.sim_config_path,
        time_series_path=args.time_series_path,
        output_path=args.output_file,
        beam_args=beam_args,
    )
