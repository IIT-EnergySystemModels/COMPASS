"""Small Pyomo and HiGHS dispatch example for the COMPASS book."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition
from pyomo.contrib.appsi.solvers import Highs


@dataclass(frozen=True)
class Generator:
    name: str
    marginal_cost: float
    capacity: float

    def __post_init__(self) -> None:
        if self.marginal_cost < 0:
            raise ValueError("marginal_cost must be non-negative")
        if self.capacity < 0:
            raise ValueError("capacity must be non-negative")


def merit_order_dispatch(
    demand: float, generators: Iterable[Generator]
) -> list[tuple[str, float]]:
    if demand < 0:
        raise ValueError("demand must be non-negative")

    demand_value = float(demand)
    items = list(generators)

    if not items:
        if demand_value <= 1e-9:
            return []
        raise ValueError("demand exceeds available capacity")

    names = [generator.name for generator in items]
    if len(set(names)) != len(names):
        raise ValueError("generator names must be unique")

    model = pyo.ConcreteModel()
    model.generators = pyo.Set(initialize=range(len(items)))
    model.output = pyo.Var(
        model.generators,
        within=pyo.NonNegativeReals,
        bounds=lambda _, i: (0.0, items[i].capacity),
    )
    model.demand_balance = pyo.Constraint(
        expr=sum(model.output[i] for i in model.generators) == demand_value
    )
    model.total_cost = pyo.Objective(
        expr=sum(items[i].marginal_cost * model.output[i] for i in model.generators),
        sense=pyo.minimize,
    )

    solver = Highs()
    solver.config.load_solution = False
    results = solver.solve(model)

    if results.termination_condition in {
        TerminationCondition.infeasible,
        TerminationCondition.infeasibleOrUnbounded,
    }:
        raise ValueError("demand exceeds available capacity")
    if results.termination_condition != TerminationCondition.optimal:
        raise RuntimeError(
            "dispatch optimisation failed with status "
            f"{results.termination_condition}"
        )

    solver.load_vars()

    dispatch: list[tuple[str, float]] = []

    for i, generator in enumerate(items):
        output = pyo.value(model.output[i])
        if output > 1e-7:
            dispatch.append((generator.name, output))

    return dispatch


def total_cost(
    dispatch: Iterable[tuple[str, float]], generators: Iterable[Generator]
) -> float:
    costs = {generator.name: generator.marginal_cost for generator in generators}
    return sum(costs[name] * output for name, output in dispatch)


def demo() -> tuple[list[tuple[str, float]], float]:
    generators = [
        Generator("wind", 0.0, 35.0),
        Generator("solar", 3.0, 25.0),
        Generator("gas", 75.0, 60.0),
    ]
    dispatch = merit_order_dispatch(80.0, generators)
    return dispatch, total_cost(dispatch, generators)


if __name__ == "__main__":
    dispatch_result, dispatch_cost = demo()
    print(f"Dispatch: {dispatch_result}")
    print(f"Total cost: {dispatch_cost:.2f}")
