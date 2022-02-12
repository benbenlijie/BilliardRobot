from PlanningCore.robot import Robot
from PlanningCore.billiard import Ball, Table


class Force(object):
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def __repr__(self):
        return f'Force(magnitude={self.magnitude}, direction={self.direction})'


def search_optimal_strike(table: Table, robot: Robot) -> tuple[Ball, Force]:
    """Search optimal strike."""
    return Ball(1, 'white', is_cue=True), Force(10, 20)