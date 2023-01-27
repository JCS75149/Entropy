import math
import pygame
import pymunk
import random
from os import path
# from Import_mod import draw_text, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, pause
from settings import *
from statistics import mean


from pymunk.pygame_util import DrawOptions
pymunk.pygame_util.positive_y_is_up = True


clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
space = pymunk.Space()
draw_options = DrawOptions(screen)
space.gravity = 0, 0
pygame.display.set_caption("Maxwell's Demon, press space bar to mix")
pymunk.pygame_util.DrawOptions(screen)
all_sprites = pygame.sprite.Group()
font_name = pygame.font.match_font('arial')


pygame.mixer.init()
snd_dir = path.join(path.dirname(__file__), 'Sounds')


velocities_list_right = []
velocities_list_left = []

# v_total = ""
v_mean_left = 0
v_mean_right = 0

top = 50
right = 20
bottom = 20
left = 20

box_points = [(left, bottom), (left, HEIGHT - top), (WIDTH - right, HEIGHT - top), (WIDTH - right, bottom)]

partition_points = [(left + (WIDTH - right - left)/2, HEIGHT - top), (left + (WIDTH - right - left)/2, bottom)]
#  This is the partition start point and end point
box_width = WIDTH - left - right
box_height = HEIGHT - top - bottom

# Global variables

partition_present = True
open_partition = pygame.time.get_ticks()
close_it = False
contact_point = (0, 0)
full_partition = True
gap_start_time = 0


def convert(pos):
    x1 = pos[0]
    y1 = screen_size[1]-pos[1]
    c_pos = x1, y1
    return c_pos


def box_to_frame(point):
    pass


def velocities():  # average velocity of balls on one side of box
    velocities_list_right.clear()
    velocities_list_left.clear()
    global close_it
    global contact_point
    global v_mean_right
    global v_mean_left
    global full_partition
    global gap_start_time
    hot = 450
    cold = 450
    # hot = 0
    # cold = 5000

    for ball in space.bodies:
        if ball.position[0] > WIDTH/2:
            v_total_r = math.sqrt(ball.velocity[0]**2 + ball.velocity[1]**2)
            velocities_list_right.append(v_total_r)
        else:
            v_total_l = math.sqrt(ball.velocity[0] ** 2 + ball.velocity[1] ** 2)
            velocities_list_left.append(v_total_l)

        x0 = partition_points[0][0]
        y0 = (partition_points[0][1] + partition_points[1][1])/2
        x1 = ball.position[0]
        y1 = ball.position[1]
        target_direction = math.degrees(math.atan2(y0-y1, x0-x1))

        opp = ball.velocity[1]*(partition_points[0][0] - ball.position[0])/ball.velocity[0]  # Length of large, similar triangle
        actual_y = opp + ball.position[1]  # opp is the distance from ball y value the contact point
        distance = math.sqrt((x1 - partition_points[0][0])**2 + (y1 - actual_y)**2)

        if not close_it:  # this is to only generate a contact point if there isn't an open gap, which confuses the pygame gap
            contact_point = (x0, actual_y)

        v_total = math.sqrt(ball.velocity[0] ** 2 + ball.velocity[1] ** 2)

        if distance < 50 and ball.velocity[0] > 0 and ball.position[0] < x0 and partition_present and v_total > hot:  # open a gap for ball on the left
            partition(True, contact_point)
            if not close_it:
                gap_start_time = pygame.time.get_ticks()
            close_it = True
            full_partition = False

        if distance < 50 and ball.velocity[0] < 0 and ball.position[0] > x0 and partition_present and v_total < cold:  # open a gap for ball on the right
            partition(True, contact_point)
            if not close_it:
                gap_start_time = pygame.time.get_ticks()
            close_it = True
            full_partition = False

    if close_it and pygame.time.get_ticks() > open_partition + 250:  # close the gap, set contact point to (0,0)
        partition(True, (0, 0))
        close_it = False
        full_partition = True
        contact_point = (0, 0)

    if len(velocities_list_left) > 0:
        v_mean_left = mean(velocities_list_left)
    if len(velocities_list_right) > 0:
        v_mean_right = mean(velocities_list_right)


def change_color(vel):
    max_v = 700
    min_v = 200
    v_total = math.sqrt(vel[0] ** 2 + vel[1] ** 2)
    if v_total > max_v:
        v_total = max_v
    if v_total < min_v:
        v_total = min_v
    range_v = max_v - min_v
    step = 510 * (v_total - min_v)/range_v  # There are 510 "steps" between RGB red and RGB blue, this interpolates

    g = 0

    if step < 255:
        r = step
    else:
        r = 255
    if step < 255:
        b = 255
    else:
        b = 510 - step
    new_color = r, g, b
    return new_color


def partition(present=True, point=(0, 0)):
    gap_width = 80
    global contact_point
    global full_partition

    if present and point == (0, 0):
        seg = pymunk.Segment(space.static_body, partition_points[0], partition_points[1], 10)
        seg.elasticity = 1
        seg.friction = 0
        seg.ID = "partition"
        space.add(seg)

    if not present or (present and point != (0, 0)):
        for shape in space.shapes:
            if shape.ID == "partition":
                space.remove(shape)

    if present and point != (0, 0):
        x, y = point
        seg1 = pymunk.Segment(space.static_body, partition_points[0], (x, y + gap_width/2), 10)
        seg2 = pymunk.Segment(space.static_body, partition_points[1], (x, y - gap_width / 2), 10)
        seg1.elasticity = 1
        seg1.friction = 0
        seg1.ID = "partition"
        seg2.elasticity = 1
        seg2.friction = 0
        seg2.ID = "partition"
        space.add(seg1, seg2)
        # print("open")
        global open_partition
        open_partition = pygame.time.get_ticks()
        sword_sound.play()


class Box:
    def __init__(self, p0=(left, bottom), p1=(WIDTH - right, HEIGHT - top)):
        x0, y0 = p0
        x1, y1 = p1
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for b in range(4):
            segment = pymunk.Segment(space.static_body, pts[b], pts[(b+1) % 4], 10)
            segment.elasticity = 1
            segment.friction = 0
            segment.ID = "wall"
            space.add(segment)


class Balls(pygame.sprite.Sprite):
    def __init__(self, pos, color, temp):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 20
        self.image = pygame.Surface([self.radius*2, self.radius*2])
        # self.image = pygame.Surface([self.radius*4, self.radius*4])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = convert(pos)
        self.temp = temp
        self.color = color

        # all_sprites.add(self)

        self.time = pygame.time.get_ticks()
        self.time1 = pygame.time.get_ticks()
        self.hyp = 5
        # pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        # Pymunk object:

        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.density = .1
        self.shape.elasticity = 1
        self.shape.ID = "ball"
        self.body.radius = self.radius
        space.add(self.body, self.shape)
        all_sprites.add(self)


        force = 1000
        if temp == "hot":
            force *= 15
        if temp == "cold":
            force *= .5

        # Original code
        x_direction = random.randint(-10, 10)
        y_direction = random.randint(-10, 10)

        # x_direction = 20
        # y_direction = 20

        if x_direction == 0:  # this is to reduce the likelihood of getting a zero x velocity which gives an error
            x_direction = 3
        # x_direction = 20
        # y_direction = 0

        self.body.apply_impulse_at_local_point((x_direction * force, y_direction * force), pos)

    def update(self):
        self.rect.center = convert(self.body.position)
        self.color = change_color(self.body.velocity)

        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)


        #  NEW STUFF #
        angle = math.degrees(math.atan2(self.body.velocity[1], self.body.velocity[0]))
        if pygame.time.get_ticks() > self.time + 1000:
            self.hyp += 5
            self.time = pygame.time.get_ticks()

        # x = math.sin(math.radians(angle_01))
        # y = math.cos(math.radians(angle_01))
        x = 1
        y = 1
        new_x = x + self.body.position.x
        new_y = x + self.body.position.y
        # if pygame.time.get_ticks() < self.time1 + 2000:
        #     pygame.draw.circle(self.image, RED, (self.radius*2 + x*self.hyp, self.radius*2 + y*self.hyp), 10)
            # print(pygame.time.get_ticks(), self.time1 + 2000)
        # else:
        #     print("Done")
        # print(x, y)
        # print(angle_01)


def draw_trailers(b):  # b is the pymunk body of the ball
    alpha = 30
    hyp = 10  # distance between trailer balls
    factor = 150
    velocity = math.sqrt(b.velocity[0] ** 2 + b.velocity[1] ** 2)
    count = math.floor(velocity/factor)
    angle = math.degrees(math.atan2(b.velocity[1], b.velocity[0]))

    for duplicates in range(count):
        x = b.position[0] - math.cos(math.radians(angle)) * hyp * (duplicates+1)
        y = b.position[1] - math.sin(math.radians(angle)) * hyp * (duplicates+1)

        surface = pygame.Surface((b.radius * 2, b.radius * 2))
        surface.set_alpha(alpha)  # Possibly something like alpha - 10*duplicates to reduce transparency for each successive duplicate

        # surface.set_colorkey(BLACK)
        # surface.fill(RED)
        color = change_color(b.velocity)
        pygame.draw.circle(surface, color, (b.radius, b.radius), b.radius)

        x = x - b.radius
        y = y + b.radius

        screen.blit(surface, convert((x, y)))

    # print(surface_rect.center)


def pygame_box():
    for p in range(4):
        pygame.draw.line(screen, GREEN, convert(box_points[p]), convert(box_points[(p+1) % 4]), 4)


def pygame_partition(present, point=(0, 0)):
    global close_it
    global full_partition
    gap_width = 80
    x0 = left + (WIDTH - right - left) / 2
    y0 = HEIGHT - top
    x1 = x0
    y1 = bottom
    if present:
        pygame.draw.line(screen, GREEN, convert((x0, y0)), convert((x1, y1)), 4)

    # if present and close_it:
    #     pygame.draw.line(screen, BLACK, convert((point[0], point[1] - gap_width/2)), convert((point[0], point[1] + gap_width/2)), 4)

    door_length = (pygame.time.get_ticks() - gap_start_time)/3  # reduce the denominator to speed the door.
    if present and close_it:
        ticks = pygame.time.get_ticks() - gap_start_time
        if door_length < gap_width:
            pygame.draw.line(screen, BLACK, convert((point[0], point[1] + gap_width/2)), convert((point[0], point[1] - door_length/2)), 4)
            # print(door_length)
        else:
            pygame.draw.line(screen, BLACK, convert((point[0], point[1] - gap_width/2)), convert((point[0], point[1] + gap_width/2)), 4)


pygame_box()
Box()
ball_count = 10

whoosh_sound = pygame.mixer.Sound(path.join(snd_dir, 'whoosh.wav'))
sword_sound = pygame.mixer.Sound(path.join(snd_dir, 'sword sound.wav'))
pygame.mixer.Sound.set_volume(sword_sound, .06)


for ball in range(ball_count):
    Balls((WIDTH/3 + random.randint(-20, 20), HEIGHT/2), BLUE, "cold")
for ball in range(ball_count):
    Balls((2*WIDTH/3 + random.randint(-20, 20), HEIGHT/2), BLUE, "hot")

partition(True)


running = True

while running:
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():
        # check for closing screen
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause()
            if event.key == pygame.K_SPACE:
                # partition(False)
                sword_sound.play()
                if partition_present:
                    partition_present = False
                    partition(False)
                else:
                    partition_present = True
                    partition(True)
            if event.key == pygame.K_z:
                partition(True, (partition_points[0][0], 350))

    all_sprites.update()



    # Draw / render
    screen.fill(BLACK)
    velocities()
    # space.debug_draw(draw_options)

    draw_text(screen, str(round(v_mean_left)), 24, 30, 10, RED)
    draw_text(screen, str(round(v_mean_right)), 24, 800, 10, RED)
    pygame_box()
    pygame_partition(partition_present, contact_point)

    for body in space.bodies:
        # print(body.position)
        draw_trailers(body)


    all_sprites.draw(screen)




    space.step(1 / FPS)
    pygame.display.flip()

pygame.quit()

