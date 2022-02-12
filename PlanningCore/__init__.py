from PlanningCore.core import Force, search_optimal_strike
from PlanningCore.robot import Robot, RobotArm, RobotBase
from PlanningCore.billiard import Ball, Pocket, Table


BALL_COLOR = ['white', 'black', 'blue', 'red']


class Manager(object):
    def __init__(
        self,
        table: Table,
        robot: Robot,
        topics=None,
        sensor_info=None,
        robot_info=None,
    ):
        self.table = table
        self.robot = robot
        self.init_ros(topics)
        self.init_table(sensor_info)
        self.init_robot(robot_info)

    def __repr__(self):
        return f'Manager(table={self.table}, robot={self.robot})'

    def init_ros(self, topics):
        """Subscribe ros topic."""
        print(f'{self} subscribed ROS topics')

    def init_table(self, sensor_info):
        """Initial table (location of balls) from camera sensor."""
        print(f'{self} initialized table={self.table}')

    def init_robot(self, robot_info):
        """Initial robot (location of robot arm and base)."""
        print(f'{self} initialized robot={self.robot}')

    def update_table(self, sensor_info):
        """Update table (location of balls) from camera sensor."""
        print(f'{self} updated table={self.table}')

    def update_robot(self, robot_info):
        """Update robot (location of robot arm and base)."""
        print(f'{self} initialized robot={self.robot}')

    def execute_optimal_strike(self):
        """Search and execute optimal strike."""
        ball, force = search_optimal_strike(self.table, self.robot)
        print(f'{self} found optimal strike: hit {ball} with {force}')
        self.robot.hit(ball, force)


if __name__ == '__main__':
    toy_example = {
        'robot': {
            'arm': {
                'pos': (0, 0, 0)
            },
            'base': {
                'pos': {10, 5}
            },
        },
        'table': {
            'width': 660,
            'height': 360,
            'margin': 30,
            'friction': 0.005,
            'balls': [Ball(i, color, (i, i), color == 'white') for i, color in enumerate(BALL_COLOR)],
            'pockets': [Pocket(i, i, i) for i in range(1, 7)],
        },
    }

    robot = Robot(RobotArm(**toy_example['robot']['arm']), RobotBase(**toy_example['robot']['base']))
    table = Table(**toy_example['table'])
    manager = Manager(table, robot)
    manager.execute_optimal_strike()