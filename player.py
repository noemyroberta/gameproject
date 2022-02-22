import pygame
from math import sin

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, change_health):
        super().__init__()

        self.import_char()
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations['idle right']
        
        self.rect = self.image.get_rect(topleft = pos)

        self.direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -16
        self.collision_rect = pygame.Rect(self.rect.topleft, (49, self.rect.height))

        self.status = 'idle right'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False

        self.change_health = change_health

        self.invincible = False
        self.invincibility_duration = 500
        self.hurt_time = 0

    def import_char(self):
        path = 'assets/male/'

        self.animations = {
            'walk right': [pygame.image.load(f'{path}male_wlk_side{x}.png').convert_alpha() for x in range(1, 5)],
            'walk behind': [pygame.image.load(f'{path}male_wlk_behind{x}.png').convert_alpha() for x in range(1, 5)],
            'dance' : [pygame.image.load(f'{path}/dance/male_dance{x}.png').convert_alpha() for x in range(1, 6)],
            'jump' : pygame.image.load(f'{path}male_jump2.png').convert_alpha(),
            'fall' : pygame.image.load(f'{path}male_fall.png').convert_alpha(),
            'idle right' : pygame.image.load(f'{path}male_stand.png').convert_alpha(),
            'idle behind' : pygame.image.load(f'{path}male_stand_behind.png').convert_alpha(), 
        }

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if isinstance(animation, list) == True:
            if self.frame_index >= len(animation):
                self.frame_index = 0
        
            image = animation[int(self.frame_index)]
            if self.facing_right:
                self.image = image
                self.rect.bottomleft = self.collision_rect.bottomleft
            else:
                flipped_image = pygame.transform.flip(image, True, False)
                self.image = flipped_image
                self.rect.bottomright = self.collision_rect.bottomright
        else:
            if self.facing_right:
                self.image = animation
                self.rect.bottomleft = self.collision_rect.bottomleft
            else:
                image = animation
                flipped_image = pygame.transform.flip(image, True, False)
                self.image = flipped_image
                self.rect.bottomright = self.collision_rect.bottomright

        if self.invincible: 
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        self.rect = self.image.get_rect(midbottom = self.rect.midbottom,)


    # Get direction
    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()


    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'walk right'
            else:
                self.status = 'idle right'


    def get_damage(self):
        if not self.invincible:
            self.change_health(-10)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()

    def invicible_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.collision_rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    # Define walk
    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        self.invicible_timer()
        