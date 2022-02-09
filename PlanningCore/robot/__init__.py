def inverse_kinematics(curr_pos, target_pos) -> list[float]:
    """Calculate the angle using Inverse Kinematics."""
    pass


def calc_arm_pos(ball_pos, direction) -> tuple[float, float, float]:
    """Calculate the target position of robot arm depends on the position of the ball and force direction."""
    pass


def calc_arm_speed(curr_pos, target_pos, force_magnitude) -> float:
    """Calculate the move speed of robot arm depends on the force magnitude."""
    pass


class RobotArm(object):
    def __init__(self, pos):
        self.pos = pos
        self.joints = ['joint1', 'joint2', 'joint3', 'joint4', 'gripper']
        # TODO: Add subscribers to get information from ros topic.

    def hit(self, ball, force):
        ball_pos = ball.get_pos()
        target_pos = calc_arm_pos(ball_pos, force.direction)
        speed = calc_arm_speed(self.pos, target_pos, force.magnitude)
        joints_angle = inverse_kinematics(self.pos, target_pos)
        self.move(joints_angle, speed)

    def move(self, joints_angles, speed):
        """Move the arm."""
        pass


class RobotBase(object):
    def __init__(self, pos):
        self.pos = pos
        # TODO: Add subscribers to get information from ros topic.

    def move(self, target_pos):
        """Move to specify position."""
        # TODO: Execute the move through ros topic.
        self.pos = target_pos


class Robot(object):
    def __init__(self, arm: RobotArm, base: RobotBase):
        self.arm = arm
        self.base = base