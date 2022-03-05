english_fraction = 0.5

# Taken from https://billiards.colostate.edu/faq/physics/physical-properties/
g = 9.8  # gravitational constant
cue_mass = 0.567  # cue mass
cue_length = 1.4732  # 58 inches
cue_tip_radius = 0.007  # 14mm tip
cue_butt_radius = 0.02
ball_mass = 0.170097  # ball mass
ball_radius = 0.028575  # ball radius
ball_moment_inertia = 2 / 5 * ball_mass * ball_radius ** 2
u_s = 0.2  # sliding friction
u_r = 0.01  # rolling friction
u_sp = 10 * 2 / 5 * ball_radius / 9  # spinning friction
e_c = 0.85  # cushion coefficient of restitution
f_c = 0.2  # cushion coefficient of friction

table_height = 1.9812  # 7-foot table (78x39 in^2 playing surface)
table_width = 1.9812/2  # 7-foot table (78x39 in^2 playing surface)

cushion_width = 2*2.54/100  # 2 inches x 2.54 cm/inch x 1/100 m/cm
cushion_height_fraction = 0.64
cushion_height = cushion_height_fraction * 2 * ball_radius
corner_pocket_width = 0.118
corner_pocket_angle = 5.3  # degrees
corner_pocket_depth = 0.0398
corner_pocket_radius = 0.124/2
corner_jaw_radius = 0.0419/2
side_pocket_width = 0.137
side_pocket_angle = 7.14  # degrees
side_pocket_depth = 0.00437
side_pocket_radius = 0.129 / 2
side_jaw_radius = 0.0159 / 2