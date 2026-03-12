import pygame, sys, random, json, os, time

pygame.init()
pygame.mixer.init()

WIDTH,HEIGHT=1000,600
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Galactic2D")

clock=pygame.time.Clock()

font=pygame.font.SysFont("arial",26)
big=pygame.font.SysFont("arial",50)

# ---------------- MUSIC ----------------

def play_normal_music():
    pygame.mixer.music.load("assets/song.mp3")
    pygame.mixer.music.play(-1)

def play_boss_music():
    pygame.mixer.music.load("assets/boss.mp3")
    pygame.mixer.music.play(-1)

play_normal_music()

# ---------------- SAVE ----------------

SAVE="save.json"

def save_game():
    data={
        "level":level,
        "coins":coins,
        "speed":speed_upgrade,
        "jump":jump_upgrade,
        "health":health_upgrade
    }

    with open(SAVE,"w") as f:
        json.dump(data,f)

def load_game():

    if os.path.exists(SAVE):

        with open(SAVE) as f:
            d=json.load(f)

            return (
                d["level"],
                d["coins"],
                d["speed"],
                d["jump"],
                d["health"]
            )

    return 1,0,0,0,0

level,coins,speed_upgrade,jump_upgrade,health_upgrade=load_game()

# ---------------- SPRITES ----------------

def load_frames(path,w,h):

    sheet=pygame.image.load(path).convert_alpha()
    frames=[]

    for i in range(sheet.get_width()//w):
        frames.append(sheet.subsurface(pygame.Rect(i*w,0,w,h)))

    return frames

idle_frames=load_frames("assets/Idle.png",128,128)
run_frames=load_frames("assets/Run.png",128,128)

block=pygame.image.load("assets/2_Idle.png").convert_alpha()

# ---------------- PLAYER ----------------

class Player:

    def __init__(self):

        self.rect=pygame.Rect(100,450,64,64)

        self.velx=0
        self.vely=0

        self.speed=6+(speed_upgrade*1.5)
        self.jump=-15-(jump_upgrade*2)

        self.gravity=0.8

        self.jumps=0
        self.max_jumps=2

        self.frame=0
        self.facing=True

        self.hp=3+health_upgrade

    def jump_now(self):

        if self.jumps<self.max_jumps:
            self.vely=self.jump
            self.jumps+=1

    def update(self,platforms):

        keys=pygame.key.get_pressed()
        self.velx=0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velx=-self.speed
            self.facing=False

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velx=self.speed
            self.facing=True

        self.rect.x+=self.velx

        for p in platforms:

            if self.rect.colliderect(p):

                if self.velx>0:self.rect.right=p.left
                if self.velx<0:self.rect.left=p.right

        self.vely+=self.gravity
        self.rect.y+=self.vely

        for p in platforms:

            if self.rect.colliderect(p):

                if self.vely>0:
                    self.rect.bottom=p.top
                    self.vely=0
                    self.jumps=0

                if self.vely<0:
                    self.rect.top=p.bottom
                    self.vely=0

        if self.rect.top>HEIGHT:
            self.hp-=1
            self.rect.topleft=(100,450)

    def draw(self):

        frames=run_frames if abs(self.velx)>0 else idle_frames

        self.frame=(self.frame+0.2)%len(frames)

        img=pygame.transform.scale(frames[int(self.frame)],(64,64))

        if not self.facing:
            img=pygame.transform.flip(img,True,False)

        screen.blit(img,self.rect)

# ---------------- LEVEL ----------------

def generate_level(lvl):

    platforms=[pygame.Rect(0,560,1000,40)]
    coins_list=[]

    for i in range(5+lvl):

        x=random.randint(100,850)
        y=random.randint(200,500)

        platforms.append(pygame.Rect(x,y,140,25))
        coins_list.append(pygame.Rect(x+60,y-30,20,20))

    goal=pygame.Rect(940,480,50,80)

    return platforms,coins_list,goal

def draw_block(rect):

    for x in range(rect.x,rect.x+rect.width,32):
        for y in range(rect.y,rect.y+rect.height,32):
            screen.blit(block,(x,y))

# ---------------- HEALTH ----------------

def draw_health(hp):

    for i in range(hp):
        pygame.draw.rect(screen,(255,0,0),(20+i*40,60,30,20))

# ---------------- SHOP ----------------

def shop():

    global coins,speed_upgrade,jump_upgrade,health_upgrade

    while True:

        screen.fill((30,40,30))

        screen.blit(big.render("SHOP",True,(255,255,255)),(420,120))

        screen.blit(font.render("1 +1 Health (50)",True,(255,255,255)),(400,260))
        screen.blit(font.render("2 Speed Up (75)",True,(255,255,255)),(400,300))
        screen.blit(font.render("3 Jump Boost (75)",True,(255,255,255)),(400,340))
        screen.blit(font.render("ESC Exit",True,(255,255,255)),(430,420))

        screen.blit(font.render(f"Coins {coins}",True,(255,255,0)),(430,380))

        pygame.display.flip()

        for e in pygame.event.get():

            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

            if e.type==pygame.KEYDOWN:

                if e.key==pygame.K_ESCAPE:
                    save_game()
                    return

                if e.key==pygame.K_1 and coins>=50:
                    coins-=50
                    health_upgrade+=1

                if e.key==pygame.K_2 and coins>=75:
                    coins-=75
                    speed_upgrade+=1

                if e.key==pygame.K_3 and coins>=75:
                    coins-=75
                    jump_upgrade+=1

# ---------------- COUNTDOWN ----------------

def countdown():

    for i in [3,2,1]:

        start=time.time()

        while time.time()-start<1:

            screen.fill((0,0,0))
            txt=big.render(str(i),True,(255,255,255))
            screen.blit(txt,(480,260))
            pygame.display.flip()

# ---------------- BOSSES ----------------

def boss1():

    play_boss_music()

    player=pygame.Rect(480,520,40,30)
    bullets=[]
    enemies=[pygame.Rect(120+x*90,80+y*60,40,30) for y in range(3) for x in range(6)]

    while True:

        screen.fill((10,10,30))

        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()

        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:player.x-=7
        if keys[pygame.K_RIGHT]:player.x+=7

        if keys[pygame.K_SPACE]:
            bullets.append(pygame.Rect(player.centerx,player.y,5,12))

        for b in bullets[:]:
            b.y-=10
            if b.y<0:bullets.remove(b)

        for b in bullets[:]:
            for e in enemies[:]:

                if b.colliderect(e):
                    bullets.remove(b)
                    enemies.remove(e)
                    break

        if not enemies:
            play_normal_music()
            return True

        pygame.draw.rect(screen,(0,255,200),player)

        for e in enemies:
            pygame.draw.rect(screen,(255,80,80),e)

        for b in bullets:
            pygame.draw.rect(screen,(255,255,0),b)

        pygame.display.flip()
        clock.tick(60)

def boss2():

    play_boss_music()

    boss=pygame.Rect(400,100,200,120)
    hp=40

    player=pygame.Rect(480,520,40,30)
    bullets=[]

    while True:

        screen.fill((20,0,30))

        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()

        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:player.x-=7
        if keys[pygame.K_RIGHT]:player.x+=7

        if keys[pygame.K_SPACE]:
            bullets.append(pygame.Rect(player.centerx,player.y,5,12))

        for b in bullets[:]:

            b.y-=10

            if b.colliderect(boss):
                bullets.remove(b)
                hp-=1

        if hp<=0:
            play_normal_music()
            return True

        pygame.draw.rect(screen,(200,50,200),boss)
        pygame.draw.rect(screen,(0,255,200),player)

        pygame.draw.rect(screen,(255,0,0),(300,40,400,20))
        pygame.draw.rect(screen,(0,255,0),(300,40,400*(hp/40),20))

        pygame.display.flip()
        clock.tick(60)

def boss3():

    play_boss_music()

    boss=pygame.Rect(450,80,100,80)
    hp=60

    player=pygame.Rect(480,520,40,30)

    bullets=[]
    enemy=[]

    while True:

        screen.fill((0,0,20))

        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()

        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:player.x-=7
        if keys[pygame.K_RIGHT]:player.x+=7

        if keys[pygame.K_SPACE]:
            bullets.append(pygame.Rect(player.centerx,player.y,5,12))

        if random.random()<0.05:
            enemy.append(pygame.Rect(boss.centerx,boss.bottom,6,14))

        for b in enemy[:]:
            b.y+=7
            if b.colliderect(player):
                return False

        for b in bullets[:]:

            b.y-=10

            if b.colliderect(boss):
                bullets.remove(b)
                hp-=1

        if hp<=0:
            play_normal_music()
            return True

        pygame.draw.rect(screen,(255,0,120),boss)
        pygame.draw.rect(screen,(0,255,200),player)

        for b in bullets:
            pygame.draw.rect(screen,(255,255,0),b)

        for b in enemy:
            pygame.draw.rect(screen,(255,80,0),b)

        pygame.display.flip()
        clock.tick(60)

# ---------------- LEVEL ----------------

def play_level(lvl):

    global coins

    player=Player()

    platforms,coinlist,goal=generate_level(lvl)

    while True:

        screen.fill((30,30,70))

        for e in pygame.event.get():

            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

            if e.type==pygame.KEYDOWN:
                if e.key in [pygame.K_SPACE,pygame.K_UP,pygame.K_w]:
                    player.jump_now()

        player.update(platforms)

        if player.hp<=0:
            return "DEAD"

        for p in platforms:
            draw_block(p)

        for c in coinlist[:]:

            pygame.draw.ellipse(screen,(255,215,0),c)

            if player.rect.colliderect(c):
                coins+=5
                coinlist.remove(c)

        pygame.draw.rect(screen,(0,255,150),goal)

        if player.rect.colliderect(goal):
            return "WIN"

        player.draw()

        draw_health(player.hp)

        screen.blit(font.render(f"Level {lvl}",True,(255,255,255)),(20,20))
        screen.blit(font.render(f"Coins {coins}",True,(255,255,0)),(20,90))

        pygame.display.flip()
        clock.tick(60)

# ---------------- MAIN ----------------

def main():

    global level,coins

    while True:

        result=play_level(level)

        if result=="WIN":

            level+=1
            save_game()

            if level%5==0:
                shop()

            if level==10:
                countdown()
                if not boss1(): level=1

            if level==15:
                countdown()
                if not boss2(): level=1

            if level==20:
                countdown()
                if not boss3(): level=1

        if result=="DEAD":

            level=1
            coins=0
            save_game()

main()