from PlanningCore.robot import Robot
from PlanningCore.billiard import Ball, Table
from PlanningCore.core import Force


def search_optimal_strike(table: Table, robot: Robot) -> tuple[Ball, Force]:
    """Search optimal strike."""
    return Ball(1, 'white', is_cue=True), Force(10, 20)