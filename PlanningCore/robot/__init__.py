from PlanningCore.robot.utils import calc_arm_pos, calc_arm_speed, inverse_kinematics


class RobotArm(object):
    def __init__(self, pos):
        self.pos = pos
        self.joints = ['joint1', 'joint2', 'joint3', 'joint4', 'gripper']
        # TODO: Add subscribers to get information from ros topic.

    def __repr__(self):
        return f'RobotArm(pos={self.pos})'

    def hit(self, ball, force):
        print(f'{self} will hit {ball} with {force}')
        # ball_pos = ball.get_pos()
        # target_pos = calc_arm_pos(ball_pos, force.direction)
        # speed = calc_arm_speed(self.pos, target_pos, force.magnitude)
        # joints_angle = inverse_kinematics(self.pos, target_pos)
        # self.move(joints_angle, speed)

    def move(self, joints_angles, speed):
        """Move the arm."""
        print('Robot arm moving to angles=(...) with speed=...')
        pass


class RobotBase(object):
    def __init__(self, pos: tuple[float, float] = (0, 0)) -> None:
        self.pos = pos
        # TODO: Add subscribers to get information from ros topic.

    def __repr__(self):
        return f'RobotBase(pos={self.pos})'

    def move(self, target_pos: tuple[float, float]) -> None:
        """Move to specify position."""
        # TODO: Execute the move through ros topic.
        self.pos = target_pos
        print(f'{self} is moving to {target_pos}')


class Robot(object):
    def __init__(self, arm: RobotArm, base: RobotBase):
        self.arm = arm
        self.base = base
        print(f'{self} initialized')

    def __repr__(self):
        return f'Robot(arm={self.arm}, base={self.base})'

    def hit(self, ball, force):
        self.base.move((ball.x, ball.y))
        self.arm.hit(ball, force)