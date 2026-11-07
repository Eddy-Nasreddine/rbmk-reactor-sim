import pygame
import random
import math
from collections import deque
from Moderator import Moderator
from Cell import Cell
from Neutron import Neutron
from Water import Water
from ControlRod import ControlRod
from Button import Button
from Slider import Slider
from IndicatorLight import IndicatorLight
from GeigerCounter import GeigerCounter

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1000

COLUMNS = 56
ROWS = 30
CELL_SIZE = 30
GRID_START_Y = 50

CELL_RADIUS = 10
WATER_SIZE = 26
NEUTRON_RADIUS = 5
NEUTRON_SPEED = 3

ROD_SPACING = 4
ROD_START_COLUMN = 2
MODERATOR_SPACING = 4
MODERATOR_START_COLUMN = 0

ROD_WIDTH = 10
MODERATOR_WIDTH = 10
ROD_MODERATOR_HEIGHT = ROWS * CELL_SIZE - 10
ROD_TOP_Y = GRID_START_Y - 10
GRAPHITE_TIP_HEIGHT = 300
SCRAM_SPEED = 1
ROD_RAISE_LIMIT = ROD_TOP_Y - ROD_MODERATOR_HEIGHT - GRAPHITE_TIP_HEIGHT
ROD_LOWER_LIMIT = ROD_TOP_Y

REACTOR_RIGHT_MARGIN = 5
GRID_START_X = (SCREEN_WIDTH - REACTOR_RIGHT_MARGIN) - (COLUMNS * CELL_SIZE - CELL_SIZE + 2 * MODERATOR_WIDTH)

REFUEL_THRESHOLD = 380
WATER_ABSORPTION_CHANCE = 0.006
CHANNEL_WATER_ABSORPTION_CHANCE = 0.01

PUMP_CAPACITY = 16
DECAY_HEAT = 50
COOLANT_SPEED = 1 / 600

FUEL_HEATING = 0.01
FUEL_TEMPERATURE_LIMIT = 1100
MIN_FISSION_CHANCE = 0.6

FUEL_BASE_TEMPERATURE = 270
FUEL_DEGREES_PER_NEUTRON = 1.5
FUEL_WARNING_TEMPERATURE = 1000

MW_PER_FISSION = 3100
POWER_SMOOTHING = 0.02
NOMINAL_POWER = 3200
TURBINE_EFFICIENCY = 0.31
TURBINE_RATING = 1000
TURBINE_INERTIA = 0.01

GRAPH_SECONDS = 60
GRAPH_AXIS_WIDTH = 38
GRAPH_MIN_SCALE = 100
GRAPH_MAX_TICKS = 5
GRAPH_STEPS = [m * 10 ** e for e in range(1, 10) for m in (1, 2, 5)]

ROD_OFFSET = CELL_SIZE - ROD_WIDTH
MODERATOR_OFFSET = CELL_SIZE - MODERATOR_WIDTH

PANEL_X = 5
PANEL_Y = 20
PANEL_WIDTH = GRID_START_X - 35
PANEL_HEIGHT = SCREEN_HEIGHT - 40
PANEL_PADDING = 20

BUTTON_WIDTH = PANEL_WIDTH - PANEL_PADDING * 2
BUTTON_HEIGHT = 45
BUTTON_SPACING = 15

SLIDER_WIDTH = PANEL_WIDTH - PANEL_PADDING * 2

BACKGROUND_COLOR = (255, 255, 255)
PANEL_COLOR = (235, 235, 240)
PANEL_BORDER_COLOR = (150, 150, 160)
TITLE_COLOR = (30, 30, 30)
TEXT_COLOR = (60, 60, 60)
WARNING_COLOR = (200, 30, 30)
GRAPH_COLOR = (250, 250, 252)
GRAPH_LINE_COLOR = (65, 115, 190)
GRAPH_NOMINAL_COLOR = (150, 150, 160)
GRAPH_GRID_COLOR = (225, 225, 232)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_rect = screen.get_rect()
clock = pygame.time.Clock()
geiger = GeigerCounter()
running = True

neutrons = []
moderators = []
control_rods = []

active_cells = set()
disabled_cells = set()
xenon_cells = set()
hot_tiles = set()

cell_grid = {}
water_grid = {}

for x in range(COLUMNS):
    for y in range(ROWS):
        cell = Cell(GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE, radius=CELL_RADIUS)
        water = Water(GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE, size=WATER_SIZE)
        disabled_cells.add(cell)
        cell_grid[(x, y)] = cell
        water_grid[(x, y)] = water

for x in range(ROD_START_COLUMN, COLUMNS, ROD_SPACING):
    control_rod_x = GRID_START_X + x * CELL_SIZE - ROD_OFFSET
    control_rods.append(ControlRod(control_rod_x, ROD_TOP_Y, width=ROD_WIDTH, height=ROD_MODERATOR_HEIGHT, tip_height=GRAPHITE_TIP_HEIGHT))

for x in [*range(MODERATOR_START_COLUMN, COLUMNS, MODERATOR_SPACING), COLUMNS]:
    moderator_x = GRID_START_X + x * CELL_SIZE - MODERATOR_OFFSET
    moderators.append(Moderator(moderator_x, ROD_TOP_Y, width=MODERATOR_WIDTH, height=ROD_MODERATOR_HEIGHT))

even_rods = control_rods[0::2]
odd_rods = control_rods[1::2]


def get_grid_position(rect):
    return (
        (rect.centerx - GRID_START_X + CELL_SIZE // 2) // CELL_SIZE,
        (rect.centery - GRID_START_Y + CELL_SIZE // 2) // CELL_SIZE
    )


def get_nearby_rects(rects):
    nearby_rects = {}
    for x in range(-1, COLUMNS + 1):
        left = GRID_START_X + x * CELL_SIZE - CELL_SIZE // 2 - NEUTRON_RADIUS
        right = left + CELL_SIZE + NEUTRON_RADIUS * 2
        nearby_rects[x] = [rect for rect in rects if rect.left < right and rect.right > left]
    return nearby_rects


nearby_moderators = get_nearby_rects([moderator.rect for moderator in moderators] + [rod.tip_rect for rod in control_rods])
nearby_rods = get_nearby_rects([rod.rect for rod in control_rods])
nearby_tips = get_nearby_rects([rod.tip_rect for rod in control_rods])
nearby_channels = get_nearby_rects([rod.channel_rect for rod in control_rods])

title_font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 24)
graph_font = pygame.font.Font(None, 18)

panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT)

current_y = PANEL_Y + PANEL_PADDING + 40

STAT_LINES = 9
STAT_SPACING = 25

stats_y = current_y
current_y += STAT_LINES * STAT_SPACING + 40

raise_all_rods = Button(PANEL_X + PANEL_PADDING, current_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Raise Rods")
current_y += BUTTON_HEIGHT + BUTTON_SPACING

lower_all_rods = Button(PANEL_X + PANEL_PADDING, current_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Lower Rods")
current_y += BUTTON_HEIGHT + BUTTON_SPACING

manual_control = Button(PANEL_X + PANEL_PADDING, current_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Manual Control")
current_y += BUTTON_HEIGHT + BUTTON_SPACING

scram = Button(PANEL_X + PANEL_PADDING, current_y, BUTTON_WIDTH, BUTTON_HEIGHT, "SCRAM")
current_y += BUTTON_HEIGHT + 50

buttons = [raise_all_rods, lower_all_rods, manual_control, scram]

manual_control_enabled = False
scram_active = False
fuel_temperature = 0.0
coolant_level = 1.0
water_line = 0
voided_tiles = 0
thermal_power = 0.0
electric_power = 0.0
frame_count = 0

PUMP_LEVEL = 50
pump_slider = Slider(PANEL_X + PANEL_PADDING, current_y, SLIDER_WIDTH, min_value=0, max_value=100, initial_value=PUMP_LEVEL, label="Pump Level", decimals=0, suffix="%")
current_y += 60

NEUTRON_TARGET = 30
neutron_target_slider = Slider(PANEL_X + PANEL_PADDING, current_y, SLIDER_WIDTH, min_value=0, max_value=200, initial_value=NEUTRON_TARGET, label="Neutron Target", decimals=0)
current_y += 60

VOLUME = 50
volume_slider = Slider(PANEL_X + PANEL_PADDING, current_y, SLIDER_WIDTH, min_value=0, max_value=100, initial_value=VOLUME, label="Volume", decimals=0, suffix="%")
current_y += 50

sliders = [pump_slider, neutron_target_slider, volume_slider]

graph_label_y = current_y
current_y += 25

graph_rect = pygame.Rect(PANEL_X + PANEL_PADDING, current_y, BUTTON_WIDTH, 145)
graph_plot_rect = pygame.Rect(
    graph_rect.left + GRAPH_AXIS_WIDTH,
    graph_rect.top + 8,
    graph_rect.width - GRAPH_AXIS_WIDTH - 6,
    graph_rect.height - 16
)

POWER_HISTORY_INTERVAL = GRAPH_SECONDS * 60 // graph_plot_rect.width
power_history = deque([0.0] * graph_plot_rect.width, maxlen=graph_plot_rect.width)
graph_tick_labels = {}

panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
pygame.draw.rect(panel_surface, PANEL_COLOR, panel_surface.get_rect(), border_radius=10)
pygame.draw.rect(panel_surface, PANEL_BORDER_COLOR, panel_surface.get_rect(), 2, border_radius=10)

title_text = title_font.render("Reactor Control", True, TITLE_COLOR)
panel_surface.blit(title_text, (PANEL_PADDING, PANEL_PADDING))

manual_y = stats_y + STAT_LINES * STAT_SPACING
manual_label = small_font.render("Manual", True, TEXT_COLOR)
panel_surface.blit(manual_label, (PANEL_PADDING, manual_y - PANEL_Y))

manual_control_light = IndicatorLight(
    PANEL_X + PANEL_PADDING + manual_label.get_width() + 16,
    manual_y + manual_label.get_height() // 2,
    radius=8
)

graph_label = small_font.render("Thermal Power (MW)", True, TEXT_COLOR)
panel_surface.blit(graph_label, (PANEL_PADDING, graph_label_y - PANEL_Y))
panel_graph_rect = graph_rect.move(-PANEL_X, -PANEL_Y)
pygame.draw.rect(panel_surface, GRAPH_COLOR, panel_graph_rect)
pygame.draw.rect(panel_surface, PANEL_BORDER_COLOR, panel_graph_rect, 1)
panel_plot_rect = graph_plot_rect.move(-PANEL_X, -PANEL_Y)
pygame.draw.line(panel_surface, PANEL_BORDER_COLOR, panel_plot_rect.topleft, panel_plot_rect.bottomleft)
pygame.draw.line(panel_surface, PANEL_BORDER_COLOR, panel_plot_rect.bottomleft, panel_plot_rect.bottomright)

reactor_surface = pygame.Surface(screen.get_size()).convert()


def draw_reactor():
    reactor_surface.fill(BACKGROUND_COLOR)
    for position, cell in cell_grid.items():
        water_grid[position].draw(reactor_surface)
        cell.draw(reactor_surface)


def redraw_tile(position):
    water = water_grid[position]
    if water.color is None:
        reactor_surface.fill(BACKGROUND_COLOR, water.rect)
    water.draw(reactor_surface)
    cell_grid[position].draw(reactor_surface)


def update_water(cool_rate):
    voided = 0
    for position in list(hot_tiles):
        water = water_grid[position]
        water.update(cool_rate)

        if water.needs_redraw():
            redraw_tile(position)

        if water.is_voided:
            voided += 1

        if water.heat == 0.0:
            hot_tiles.discard(position)
    return voided


def get_coolant_target(pump_level):
    return min(1.0, pump_level * PUMP_CAPACITY / (fuel_temperature + DECAY_HEAT))


def move_water_line(old_line, new_line):
    for y in range(min(old_line, new_line), max(old_line, new_line)):
        for x in range(COLUMNS):
            position = (x, y)
            if y < new_line:
                water_grid[position].drain()
            else:
                water_grid[position].fill()
            hot_tiles.discard(position)
            redraw_tile(position)


def update_cells():
    for cell in list(disabled_cells):
        if cell.decay():
            neutrons.append(Neutron(cell.x, cell.y, radius=NEUTRON_RADIUS, speed=NEUTRON_SPEED))

        if cell.decay_to_xenon():
            disabled_cells.discard(cell)
            xenon_cells.add(cell)
            cell.draw(reactor_surface)

    for cell in list(xenon_cells):
        if cell.xenon_decay():
            xenon_cells.discard(cell)
            disabled_cells.add(cell)
            cell.draw(reactor_surface)


def refuel_cells():
    refuel_count = min(REFUEL_THRESHOLD - len(active_cells), len(disabled_cells))
    if refuel_count <= 0:
        return

    for cell in random.sample(list(disabled_cells), refuel_count):
        cell.refuel()
        disabled_cells.discard(cell)
        active_cells.add(cell)
        cell.draw(reactor_surface)


def get_fission_chance():
    return max(MIN_FISSION_CHANCE, 1 - fuel_temperature / FUEL_TEMPERATURE_LIMIT)


def update_neutrons(neutrons):
    surviving_neutrons = []
    neutron_sprites = []
    fission_chance = get_fission_chance()
    fissions = 0

    for n in neutrons:
        n.update()

        if not screen_rect.colliderect(n.rect):
            continue

        position = get_grid_position(n.rect)

        if position[1] >= water_line:
            water = water_grid.get(position)
            if water and n.rect.colliderect(water.rect):
                water.heat_from_passage()
                hot_tiles.add(position)
                if random.random() < WATER_ABSORPTION_CHANCE and water.rect.collidelist(nearby_tips.get(position[0], ())) == -1:
                    if water.absorb():
                        continue

        if random.random() < CHANNEL_WATER_ABSORPTION_CHANCE and n.rect.collidelist(nearby_channels.get(position[0], ())) != -1:
            continue

        if not n.thermal_n:
            moderator_rects = nearby_moderators.get(position[0], ())
            hit_index = n.rect.collidelist(moderator_rects)
            if hit_index != -1:
                n.moderate(moderator_rects[hit_index])
                position = get_grid_position(n.rect)

        if n.rect.collidelist(nearby_rods.get(position[0], ())) != -1:
            continue

        neutron_sprites.append((n.image, n.rect))
        cell = cell_grid.get(position)

        if n.thermal_n and cell in active_cells and pygame.sprite.collide_circle(n, cell):
            if random.random() < fission_chance:
                surviving_neutrons.extend(cell.hit())
                fissions += 1
                active_cells.discard(cell)
                disabled_cells.add(cell)
                cell.draw(reactor_surface)

        elif n.thermal_n and cell in xenon_cells and pygame.sprite.collide_circle(n, cell):
            if cell.burn_out():
                xenon_cells.discard(cell)
                disabled_cells.add(cell)
                cell.draw(reactor_surface)

        else:
            surviving_neutrons.append(n)

    screen.blits(neutron_sprites, doreturn=False)
    return surviving_neutrons, fissions


def get_graph_scale(peak):
    peak = max(peak, GRAPH_MIN_SCALE)
    for step in GRAPH_STEPS:
        if step * GRAPH_MAX_TICKS >= peak:
            return step, step * math.ceil(peak / step)
    return GRAPH_STEPS[-1], GRAPH_STEPS[-1] * math.ceil(peak / GRAPH_STEPS[-1])


def get_graph_y(value, scale):
    return graph_plot_rect.bottom - 1 - value / scale * (graph_plot_rect.height - 1)


def get_tick_label(value):
    if value not in graph_tick_labels:
        if value >= 1000000:
            text = f"{value / 1000000:g}M"
        elif value >= 10000:
            text = f"{value // 1000}k"
        else:
            text = str(value)
        graph_tick_labels[value] = graph_font.render(text, True, TEXT_COLOR)
    return graph_tick_labels[value]


def draw_power_graph():
    step, scale = get_graph_scale(max(power_history))

    for value in range(0, scale + 1, step):
        y = get_graph_y(value, scale)
        if value > 0:
            pygame.draw.line(screen, GRAPH_GRID_COLOR, (graph_plot_rect.left + 1, y), (graph_plot_rect.right - 1, y))
        pygame.draw.line(screen, PANEL_BORDER_COLOR, (graph_plot_rect.left - 3, y), (graph_plot_rect.left, y))
        label = get_tick_label(value)
        screen.blit(label, label.get_rect(midright=(graph_plot_rect.left - 5, y)))

    if NOMINAL_POWER <= scale:
        nominal_y = get_graph_y(NOMINAL_POWER, scale)
        for x in range(graph_plot_rect.left + 1, graph_plot_rect.right, 8):
            pygame.draw.line(screen, GRAPH_NOMINAL_COLOR, (x, nominal_y), (min(x + 4, graph_plot_rect.right - 1), nominal_y))

    points = [(graph_plot_rect.left + i, get_graph_y(value, scale)) for i, value in enumerate(power_history)]
    pygame.draw.lines(screen, GRAPH_LINE_COLOR, False, points, 2)


def draw_panel():
    screen.blit(panel_surface, panel_rect)

    fuel_celsius = int(FUEL_BASE_TEMPERATURE + fuel_temperature * FUEL_DEGREES_PER_NEUTRON)
    steam = int((voided_tiles + water_line * COLUMNS) / (ROWS * COLUMNS) * 100)
    coolant = int(coolant_level * 100)
    rods_in = int(sum(max(0, rod.rect.bottom - ROD_TOP_Y) for rod in control_rods) / (len(control_rods) * ROD_MODERATOR_HEIGHT) * 100)

    stats = [
        (f"FPS: {int(clock.get_fps())}", False),
        (f"Neutrons: {len(neutrons)}", False),
        (f"Xenon Cells: {len(xenon_cells)}", False),
        (f"Fuel Temp: {fuel_celsius}°C", fuel_celsius > FUEL_WARNING_TEMPERATURE),
        (f"Thermal: {int(thermal_power)} MWt", thermal_power > NOMINAL_POWER * 1.5),
        (f"Electric: {int(electric_power)} MWe", False),
        (f"Coolant: {coolant}%", coolant < 90),
        (f"Steam: {steam}%", steam > 20),
        (f"Rods In: {rods_in}%", False)
    ]
    for i, (text, warning) in enumerate(stats):
        label = small_font.render(text, True, WARNING_COLOR if warning else TEXT_COLOR)
        screen.blit(label, (PANEL_X + PANEL_PADDING, stats_y + i * STAT_SPACING))

    manual_control_light.draw(screen, manual_control_enabled)
    draw_power_graph()

    for button in buttons:
        button.draw(screen)

    for slider in sliders:
        slider.draw(screen)


refuel_cells()
draw_reactor()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if scram.clicked(event.pos):
                scram_active = True

            if manual_control.clicked(event.pos):
                manual_control_enabled = not manual_control_enabled

        for slider in sliders:
            slider.handle_event(event)

    PUMP_LEVEL = pump_slider.value
    COOL_RATE = PUMP_LEVEL / 100
    NEUTRON_TARGET = int(neutron_target_slider.value)
    VOLUME = volume_slider.value
    geiger.volume = VOLUME / 100

    if scram_active:
        for rod in control_rods:
            rod.lower_rod(SCRAM_SPEED)
        scram_active = any(rod.y != ROD_LOWER_LIMIT for rod in control_rods)

    elif manual_control_enabled:
        if raise_all_rods.holding():
            for rod in control_rods:
                rod.raise_rod(1)

        if lower_all_rods.holding():
            for rod in control_rods:
                rod.lower_rod(1)

    elif len(neutrons) < NEUTRON_TARGET:
        if odd_rods[0].y != ROD_RAISE_LIMIT:
            for rod in odd_rods:
                rod.raise_rod(1)
        elif even_rods[0].y != ROD_RAISE_LIMIT:
            for rod in even_rods:
                rod.raise_rod(1)

    elif len(neutrons) > NEUTRON_TARGET:
        if even_rods[0].y != ROD_LOWER_LIMIT:
            for rod in even_rods:
                rod.lower_rod(1)
        elif odd_rods[0].y != ROD_LOWER_LIMIT:
            for rod in odd_rods:
                rod.lower_rod(1)

    coolant_target = get_coolant_target(PUMP_LEVEL)
    coolant_level += max(-COOLANT_SPEED, min(COOLANT_SPEED, coolant_target - coolant_level))

    new_water_line = ROWS - round(coolant_level * ROWS)
    if new_water_line != water_line:
        move_water_line(water_line, new_water_line)
        water_line = new_water_line

    voided_tiles = update_water(COOL_RATE)

    update_cells()
    refuel_cells()

    screen.blit(reactor_surface, (0, 0))

    for rod in control_rods:
        rod.draw_channel(screen)

    for moderator in moderators:
        moderator.draw(screen)

    neutrons, fissions = update_neutrons(neutrons)
    geiger.click(fissions)
    fuel_temperature += (len(neutrons) - fuel_temperature) * FUEL_HEATING

    thermal_power += (fissions * MW_PER_FISSION - thermal_power) * POWER_SMOOTHING
    turbine_power = min(TURBINE_RATING, thermal_power * TURBINE_EFFICIENCY * coolant_level)
    electric_power += (turbine_power - electric_power) * TURBINE_INERTIA

    frame_count += 1
    if frame_count % POWER_HISTORY_INTERVAL == 0:
        power_history.append(thermal_power)

    draw_panel()

    for rod in control_rods:
        rod.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
