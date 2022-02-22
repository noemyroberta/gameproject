import pygame
from game_data import levels
from util import import_folder
from decoration import Sky
from settings import screen_width, screen_height

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, icon_speed, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_idx = 0
        self.image = self.frames[self.frame_idx]

        self.rect = self.image.get_rect(center=pos)

        self.detection_zone = pygame.Rect(self.rect.centerx - (
            icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)

    def animate(self):
        self.frame_idx += 0.15
        
        if self.frame_idx >= len(self.frames):
            self.frame_idx = 0

        self.image = self.frames[int(self.frame_idx)]

    def update(self):
        self.animate()

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.frames = import_folder('assets/male/dance')
        self.frame_idx = 0
        self.image = self.frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        self.frame_idx += 0.10
        
        if self.frame_idx >= len(self.frames):
            self.frame_idx = 0

        self.image = self.frames[int(self.frame_idx)]

    def update(self):
        self.rect.center = self.pos
        self.animate()

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):

        # setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level
                
        # movement logic
        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8

        self.setup_nodes()
        self.setup_icons()
        self.sky = Sky(8)


    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        for node_data in levels.values():
            node_sprite = Node(node_data['node_pos'], self.speed, node_data['node_graphics'])
            self.nodes.add(node_sprite)

    def setup_icons(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def draw_path(self):
        point = [node['node_pos'] for node in levels.values()]
        pygame.draw.lines(self.display_surface, '#a04f45', False, point, 6)

    def draw_title(self, text, fontSize, pos):
        self.font = pygame.font.Font('assets/graphics/ui/ARCADEPI.ttf', fontSize)
        title = self.font.render(text, False, '#33323d')
        title_rect = title.get_rect(center = pos)
        self.display_surface.blit(title, title_rect)


    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_mvnt_data('next')
                print(self.move_direction)
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_mvnt_data('previous')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0,0)

    def get_mvnt_data(self, target):
        start = pygame.math.Vector2(
            self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def run(self):
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.sky.draw(self.display_surface)
        self.draw_path()
        self.nodes.update()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)
        self.draw_title('Habbo in Mario', 40, (600,200))
        self.draw_title('De volta para o hotel', 19, (600,230))
