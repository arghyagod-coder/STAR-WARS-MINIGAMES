
while True:
    print('''STAR WARS- minigames

    Hey traveller, you just reached the spaceship A6-2001, We welcome you to an exciting adventure, where you can become the next Luke Skywalker, and defeat the Evil Darth Vader.

    Choose a game by its serial number:

    1. TRAVEL THROUGH SPACE-

    Your spaceship is stuck in an unknown pressure point. Drag yourself out of it, following the pressure-broken areas of the debris, be sure not to go too high or low, and avoid losing in space
    
    2. SHOOT THE STORMTROOPERS

    The Stormtroopers are terrorizing the whole planet, fight them and prevent Mystica from getting destroyed.
    
    WHICH GAME DO YOU WANT TO CHOOSE?''')
    game_input = input()

    if game_input == '2':
        import pygame
        from pygame import mixer
        import os
        import time
        import random
        pygame.font.init()

        # SET THE GAME DEFOS

        WIDTH, HEIGHT = 750, 900
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shoot the Stormtroopers")

        # Load images
        RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load('assets/stormtrooper.png'), (100, 90))
        GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load("assets/stormtrooper.png"), (100,90))
        BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load('assets/stormtrooper.png'), (100, 90))


        # Player /
        LUKE_SKYWALKER = pygame.transform.scale(pygame.image.load("assets/luke_ship.png"), (120,110))

        # Bullets
        RED_BULLET = pygame.image.load("assets/pixel_laser_red.png")
        GREEN_BULLET = pygame.image.load("assets/pixel_laser_green.png")
        BLUE_BULLET = pygame.image.load("assets/pixel_laser_blue.png")
        YELLOW_BULLET = pygame.image.load("assets/pixel_laser_yellow.png")

        # Background
        BG = pygame.transform.scale(pygame.image.load("assets/background_space.png"), (WIDTH, HEIGHT))

        # Using OOPs to make a laser class
        class Laser:

            # first thing it will do
            def __init__(self, x, y, img):
                self.x = x
                self.y = y
                self.img = img
                self.mask = pygame.mask.from_surface(self.img)

            def draw(self, window):
                window.blit(self.img, (self.x, self.y))

            def move(self, vel):
                self.y += vel

            def off_screen(self, height):
                return not(self.y <= height and self.y >= 0)

            def collision(self, obj):
                return collide(self, obj)

        # Ship Class
        class Ship:
            COOLDOWN = 30

            def __init__(self, x, y, health=100):
                self.x = x
                self.y = y
                self.health = health
                self.ship_img = None
                self.laser_img = None
                self.lasers = []
                self.cool_down_counter = 0

            def draw(self, window):
                window.blit(self.ship_img, (self.x, self.y))
                for laser in self.lasers:
                    laser.draw(window)

            def move_BULLETs(self, vel, obj):
                self.cooldown()
                for laser in self.lasers:
                    laser.move(vel)
                    if laser.off_screen(HEIGHT):
                        self.lasers.remove(laser)
                    elif laser.collision(obj):
                        obj.health -= 10
                        self.lasers.remove(laser)

            def cooldown(self):
                if self.cool_down_counter >= self.COOLDOWN:
                    self.cool_down_counter = 0
                elif self.cool_down_counter > 0:
                    self.cool_down_counter += 1

            def shoot(self):
                if self.cool_down_counter == 0:
                    laser = Laser(self.x, self.y, self.laser_img)
                    self.lasers.append(laser)
                    self.cool_down_counter = 1

            def get_width(self):
                return self.ship_img.get_width()

            def get_height(self):
                return self.ship_img.get_height()


        class Player(Ship):
            def __init__(self, x, y, health=100):
                super().__init__(x, y, health)
                self.ship_img = LUKE_SKYWALKER
                self.laser_img = YELLOW_BULLET
                self.mask = pygame.mask.from_surface(self.ship_img)
                self.max_health = health

            def move_BULLETs(self, vel, objs):
                self.cooldown()
                for laser in self.lasers:
                    laser.move(vel)
                    if laser.off_screen(HEIGHT):
                        self.lasers.remove(laser)
                    else:
                        for obj in objs:
                            if laser.collision(obj):
                                objs.remove(obj)
                                if laser in self.lasers:
                                    self.lasers.remove(laser)

            def draw(self, window):
                super().draw(window)
                self.healthbar(window)

            def healthbar(self, window):
                pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
                pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


        class Enemy(Ship):
            COLOR_MAP = {
                        "red": (RED_SPACE_SHIP, RED_BULLET),
                        "green": (GREEN_SPACE_SHIP, GREEN_BULLET),
                        "blue": (BLUE_SPACE_SHIP, BLUE_BULLET)
                        }

            def __init__(self, x, y, color, health=100):
                super().__init__(x, y, health)
                self.ship_img, self.laser_img = self.COLOR_MAP[color]
                self.mask = pygame.mask.from_surface(self.ship_img)

            def move(self, vel):
                self.y += vel

            def shoot(self):
                if self.cool_down_counter == 0:
                    laser = Laser(self.x-20, self.y, self.laser_img)
                    self.lasers.append(laser)
                    self.cool_down_counter = 1


        def collide(obj1, obj2):
            offset_x = obj2.x - obj1.x
            offset_y = obj2.y - obj1.y
            return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

        def main():
            run = True
            FPS = 60
            level = 0
            lives = 5
            main_font = pygame.font.SysFont("comicsans", 50)
            lost_font = pygame.font.SysFont("comicsans", 60)

            enemies = []
            wave_length = 5
            enemy_vel = 1

            player_vel = 5
            laser_vel = 5

            player = Player(300, 630)

            clock = pygame.time.Clock()

            lost = False
            lost_count = 0

            def redraw_window():
                WIN.blit(BG, (0,0))
                # draw text
                lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
                level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

                WIN.blit(lives_label, (10, 10))
                WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

                for enemy in enemies:
                    enemy.draw(WIN)

                player.draw(WIN)

                if lost:
                    lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
                    WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

                pygame.display.update()

            while run:
                clock.tick(FPS)
                redraw_window()

                if lives <= 0 or player.health <= 0:
                    lost = True
                    lost_count += 1

                if lost:
                    if lost_count > FPS * 3:
                        run = False
                    else:
                        continue

                if len(enemies) == 0:
                    level += 1
                    wave_length += 5
                    for i in range(wave_length):
                        enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                        enemies.append(enemy)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_a] and player.x - player_vel > 0: # left
                    player.x -= player_vel
                if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
                    player.x += player_vel
                if keys[pygame.K_w] and player.y - player_vel > 0: # up
                    player.y -= player_vel
                if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
                    player.y += player_vel
                if keys[pygame.K_SPACE]:
                    player.shoot()

                for enemy in enemies[:]:
                    enemy.move(enemy_vel)
                    enemy.move_BULLETs(laser_vel, player)

                    if random.randrange(0, 2*60) == 1:
                        enemy.shoot()

                    if collide(enemy, player):
                        player.health -= 10
                        enemies.remove(enemy)
                    elif enemy.y + enemy.get_height() > HEIGHT:
                        lives -= 1
                        enemies.remove(enemy)

                player.move_BULLETs(-laser_vel, enemies)

        def main_menu():
            title_font = pygame.font.SysFont("Times New Roman", 70)
            run = True
            while run:
                WIN.blit(BG, (0,0))
                title_label = title_font.render("GET READY TO FIGHT!", 1, (255,255,255))
                WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        main()
            pygame.quit()

        if __name__=='__main__':
            main_menu()

    elif game_input == '1':
        import random # For generating random numbers
        import sys # We will use sys.exit to exit the program
        import pygame
        from pygame.locals import * # Basic pygame imports

        # Global Variables for the game
        FPS = 32
        SCREENWIDTH = 289
        SCREENHEIGHT = 511
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        GROUNDY = SCREENHEIGHT * 0.8
        GAME_SPRITES = {}
        GAME_SOUNDS = {}
        PLAYER = '/assets/luke_ship.png'
        BACKGROUND = '/assets/background_space.png'
        PIPE = '/assets/debris.png'

        def welcomeScreen():
            """
            Shows welcome images on the screen
            """

            playerx = int(SCREENWIDTH/5)
            playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
            messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
            messagey = int(SCREENHEIGHT*0.13)
            basex = 0
            while True:
                for event in pygame.event.get():
                    # if user clicks on cross button, close the game
                    if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        sys.exit()

                    # If the user presses space or up key, start the game for them
                    elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                        return
                    else:
                        SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
                        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
                        SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))    
                        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
                        pygame.display.update()
                        FPSCLOCK.tick(FPS)

        def mainGame():
            score = 0
            playerx = int(SCREENWIDTH/5)
            playery = int(SCREENWIDTH/2)
            basex = 0

            # Create 2 pipes for blitting on the screen
            newPipe1 = getRandomPipe()
            newPipe2 = getRandomPipe()

            # my List of upper pipes
            upperPipes = [
                {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
                {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
            ]
            # my List of lower pipes
            lowerPipes = [
                {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
                {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
            ]

            pipeVelX = -4

            playerVelY = -9
            playerMaxVelY = 10
            playerMinVelY = -8
            playerAccY = 1

            playerFlapAccv = -8 # velocity while flapping
            playerFlapped = False # It is true only when the bird is flapping


            while True:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                        if playery > 0:
                            playerVelY = playerFlapAccv
                            playerFlapped = True
                            GAME_SOUNDS['wing'].play()


                crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
                if crashTest:
                    return     

                #check for score
                playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
                for pipe in upperPipes:
                    pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
                    if pipeMidPos<= playerMidPos < pipeMidPos +4:
                        score +=1
                        print(f"Your score is {score}") 
                        GAME_SOUNDS['point'].play()


                if playerVelY <playerMaxVelY and not playerFlapped:
                    playerVelY += playerAccY

                if playerFlapped:
                    playerFlapped = False            
                playerHeight = GAME_SPRITES['player'].get_height()
                playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

                # move pipes to the left
                for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
                    upperPipe['x'] += pipeVelX
                    lowerPipe['x'] += pipeVelX

                # Add a new pipe when the first is about to cross the leftmost part of the screen
                if 0<upperPipes[0]['x']<5:
                    newpipe = getRandomPipe()
                    upperPipes.append(newpipe[0])
                    lowerPipes.append(newpipe[1])

                # if the pipe is out of the screen, remove it
                if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
                    upperPipes.pop(0)
                    lowerPipes.pop(0)
                
                # Lets blit our sprites now
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
                    SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
                    SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                myDigits = [int(x) for x in list(str(score))]
                width = 0
                for digit in myDigits:
                    width += GAME_SPRITES['numbers'][digit].get_width()
                Xoffset = (SCREENWIDTH - width)/2

                for digit in myDigits:
                    SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
                    Xoffset += GAME_SPRITES['numbers'][digit].get_width()
                pygame.display.update()
                FPSCLOCK.tick(FPS)

        def isCollide(playerx, playery, upperPipes, lowerPipes):
            if playery> GROUNDY - 25  or playery<0:
                GAME_SOUNDS['hit'].play()
                return True
            
            for pipe in upperPipes:
                pipeHeight = GAME_SPRITES['pipe'][0].get_height()
                if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
                    GAME_SOUNDS['hit'].play()
                    return True

            for pipe in lowerPipes:
                if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
                    GAME_SOUNDS['hit'].play()
                    return True

            return False

        def getRandomPipe():
            """
            Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
            """
            pipeHeight = GAME_SPRITES['pipe'][0].get_height()
            offset = SCREENHEIGHT/3
            y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
            pipeX = SCREENWIDTH + 10
            y1 = pipeHeight - y2 + offset
            pipe = [
                {'x': pipeX, 'y': -y1}, #upper Pipe
                {'x': pipeX, 'y': y2} #lower Pipe
            ]
            return pipe






        if __name__ == "__main__":
            # This will be the main point from where our game will start
            pygame.init() # Initialize all pygame's modules
            FPSCLOCK = pygame.time.Clock()
            pygame.display.set_caption('ESCAPE THE PRESSURE LOOP')
            GAME_SPRITES['numbers'] = ( 
                pygame.image.load('assets/0.png').convert_alpha(),
                pygame.image.load('assets/1.png').convert_alpha(),
                pygame.image.load('assets/2.png').convert_alpha(),
                pygame.image.load('assets/3.png').convert_alpha(),
                pygame.image.load('assets/4.png').convert_alpha(),
                pygame.image.load('assets/5.png').convert_alpha(),
                pygame.image.load('assets/6.png').convert_alpha(),
                pygame.image.load('assets/7.png').convert_alpha(),
                pygame.image.load('assets/8.png').convert_alpha(),
                pygame.image.load('assets/9.png').convert_alpha(),
            )

            GAME_SPRITES['message'] =pygame.image.load('assets/message.png').convert_alpha()
            GAME_SPRITES['base'] =pygame.image.load('assets/base.png').convert_alpha()
            GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
            pygame.image.load(PIPE).convert_alpha()
            )

            # Game sounds
            GAME_SOUNDS['die'] = pygame.mixer.Sound('assets/die.wav')
            GAME_SOUNDS['hit'] = pygame.mixer.Sound('assets/hit.wav')
            GAME_SOUNDS['point'] = pygame.mixer.Sound('assets/point.wav')
            GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('assets/swoosh.wav')
            GAME_SOUNDS['wing'] = pygame.mixer.Sound('assets/wing.wav')

            GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
            GAME_SPRITES['player'] = pygame.transform.rotate((pygame.image.load(PLAYER).convert_alpha()), 270)

            while True:
                welcomeScreen() # Shows welcome screen to the user until he presses a button
                mainGame() # This is the main game function 

    else:
        print('INVALID INPUT')
