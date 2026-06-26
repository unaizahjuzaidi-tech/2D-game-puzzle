import pygame
import sys
import os

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jungle Adventure: River Crossing Puzzle")

COLOR_TEXT = (255, 255, 255)
COLOR_PANEL = (50, 50, 50)
COLOR_WARN = (220, 20, 60)

LOCALIZATION = {
    "EN": {
        "title": "Jungle River Crossing",
        "start": "Press ENTER to Start Game",
        "instructions_btn": "Press I for Instructions",
        "lang_btn": "Press L to Tukar Bahasa (Malay)",
        "back_main": "Press M for Main Menu",
        "score": "Score",
        "time": "Time Left",
        "paused": "GAME PAUSED",
        "resume": "Press P to Resume",
        "restart": "Press R to Restart",
        "win": "VICTORY! You crossed safely!",
        "instruct_title": "HOW TO PLAY",
        "rule1": "1. The Raft can only hold the Explorer + ONE other entity.",
        "rule2": "2. Click entities to move them onto the raft or land banks.",
        "rule3": "3. Press SPACEBAR to sail the raft across the river.",
        "rule4": "4. Tiger + Monkey left alone without Explorer = Tiger eats Monkey!",
        "rule5": "5. Monkey + Banana left alone without Explorer = Monkey eats Banana!"
    },
    "MY": {
        "title": "Kembara Sungai Rimba",
        "start": "Tekan ENTER untuk Mula Permainan",
        "instructions_btn": "Tekan I untuk Arahan",
        "lang_btn": "Press L to Change Language (English)",
        "back_main": "Tekan M untuk Menu Utama",
        "score": "Markah",
        "time": "Masa Tinggal",
        "paused": "PERMAINAN DIHENTIKAN",
        "resume": "Tekan P untuk Sambung",
        "restart": "Tekan R untuk Mula Semula",
        "win": "TAHNIAH! Anda berjaya menyeberang!",
        "instruct_title": "CARA BERMAIN",
        "rule1": "1. Rakit hanya boleh memnbawa Pengembara + SATU entiti lain.",
        "rule2": "2. Klik entiti hanya mengalihkannya ke rakit atau tebing sungai.",
        "rule3": "3. Tekan SPACEBAR untuk menggerakkan rakit menyeberang.",
        "rule4": "4. Harimau + Monyet ditinggalkan tanpa Pengembara = Harimau makan Monyet!",
        "rule5": "5. Monyet + Pisang ditinggalkan tanpa Pengembara = Monyet makan Pisang!"
    }
}

def scale_keep_ratio(image, max_width, max_height):
    original_w, original_h = image.get_size()
    ratio = min(max_width / original_w, max_height / original_h)
    return pygame.transform.scale(image, (int(original_w * ratio), int(original_h * ratio)))

class GameEntity(pygame.sprite.Sprite):
    """Represents the characters and items in the puzzle."""
    def __init__(self, name, start_side, image_filename, offset_y):
        super().__init__()
        self.name = name
        self.side = start_side
        self.is_on_raft = False

        image_path = os.path.join("assets", "images", image_filename)
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((60, 60))
            self.image.fill((200, 200, 200))

        self.image = scale_keep_ratio(self.image, 60, 60)
        self.rect = self.image.get_rect()

        self.offset_y = offset_y
        self.target_x = 0
        self.target_y = 0
        self.snap_to_initial_position()

    def snap_to_initial_position(self):
        """Sets target coordinates based on bank state configuration."""
        if self.is_on_raft:
            return
        if self.side == "left":
            self.target_x = 100
            self.target_y = self.offset_y
        else:
            self.target_x = 1040
            self.target_y = self.offset_y

    def update(self):
        """Simple Physics Layer: Smooth linear position interpolation (LERP)."""
        self.rect.x += (self.target_x - self.rect.x) * 0.15
        self.rect.y += (self.target_y - self.rect.y) * 0.15

class Raft(pygame.sprite.Sprite):
    """Represents the transport vechile navigating the river bounds."""
    def __init__(self):
        super().__init__()
        self.side = "left"

        image_path = os.path.join("assets", "images", "raft.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((140, 160))
            self.image.fill((139, 69, 19))
        
        self.image = scale_keep_ratio(self.image, 140, 160)
        self.rect = self.image.get_rect()

        self.target_x = 520
        self.target_y = 250
        
        self.rect.center = (self.target_x, self.target_y)

        self.passengers = []
        self.is_moving = False
        self.speed = 6

    def switch_side(self):
        self.is_moving = True
        if self.side == "left":
            self.side = "right"
            self.target_x = 640
        else:
            self.side = "left"
            self.target_x = 420

    def update(self):
        self.rect.x += (self.target_x - self.rect.x) * 0.08
        self.rect.y = self.target_y

        for i, passenger in enumerate(self.passengers):
            passenger.target_x = self.rect.x + 20 + (i * 60)
            passenger.target_y = self.rect.y - 30

        if abs(self.rect.x - self.target_x) < 2:
            self.rect.x = self.target_x
            if self.is_moving:
                self.is_moving = False
                return True 
        return False

class GameManager:
    """Manages Game Loops, Global States, Validation Logic, Rules, and Drawing."""
    def __init__(self):
        self.state = "MENU"
        self.lang = "EN"
        self.font_large = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)

        bg_path = os.path.join("assets", "images", "background.png")
        try:
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(
    self.bg_image,
    (SCREEN_WIDTH, SCREEN_HEIGHT - 100)
)
        except pygame.error:
            self.bg_image = None

        try:
            pygame.mixer.music.load(os.path.join("assets", "sounds", "background.mp3"))
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Background music file not found")

        self.sound_sail = None
        self.sound_win = None
        self.sound_lose = None

        try:
            self.sound_sail = pygame.mixer.Sound(os.path.join("assets", "sounds", "sail.wav"))
            self.sound_win = pygame.mixer.Sound(os.path.join("assets", "sounds", "win.wav"))
            self.sound_lose =  pygame.mixer.Sound(os.path.join("assets", "sounds", "lose.wav"))
        except pygame.error:
            print("Some sound effects not found")

        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.time_left = 60.0
        self.fail_reason = ""

        self.raft = Raft()
        self.explorer = GameEntity("Explorer", "left", "explorer.png", 100)
        self.tiger = GameEntity("Tiger", "left", "tiger.png", 200)
        self.monkey = GameEntity("Monkey", "left", "monkey.png", 300)
        self.banana = GameEntity("Banana", "left", "banana.png", 400)

        self.entities = pygame.sprite.Group(self.explorer, self.tiger, self.monkey, self.banana)

    def handle_click(self, mouse_pos):
        """Move entities between shore and raft — drop to current raft side"""
        if self.state != "PLAYING" or self.raft.is_moving:
            return
        
        for entity in self.entities:
            if entity.rect.collidepoint(mouse_pos):
                if entity.is_on_raft:
                    entity.is_on_raft = False
                    self.raft.passengers.remove(entity)
                    entity.side = self.raft.side   # <-- uses raft's current side
                    entity.snap_to_initial_position()  # places them on the bank
                else:
                    # Board only if same side and raft has space
                    if entity.side == self.raft.side and len(self.raft.passengers) < 2:
                        entity.is_on_raft = True
                        self.raft.passengers.append(entity)
                    
    def trigger_raft_move(self):
        """Sails raft to opposite side if driving criteria checks pass."""
        if self.state != "PLAYING":
            return
        if self.raft.is_moving:
            return
        
        if self.explorer in self.raft.passengers:
            self.raft.switch_side()
            self.score += 100
            if self.sound_sail:
                self.sound_sail.play()

        for e in self.raft.passengers:
            e.side = "raft"

    def check_bank_safety(self):
        """Evaluates puzzle state rules and determines fail conditions."""
        left_shore = [e.name for e in self.entities if e.side == "left" and not e.is_on_raft]
        right_shore = [e.name for e in self.entities if e.side == "right" and not e.is_on_raft]

        for shore in [left_shore, right_shore]:
            if "Explorer" not in shore:
                if "Tiger" in shore and "Monkey" in shore:
                    self.state = "GAME_OVER"
                    self.fail_reason = "Tiger ate the Monkey!" if self.lang == "EN" else "Harimau makan Monyet!"
                    if self.sound_lose:
                        self.sound_lose.play()
                    return
                if "Monkey" in shore and "Banana" in shore:
                    self.state = "GAME_OVER"
                    self.fail_reason = "Monkey ate the Bananas!" if self.lang == "EN" else "Monyet makan Pisang!"
                    return

        if len(right_shore) == 4:
            self.state = "WIN"
            if self.sound_win:
                self.sound_win.play()

    def update(self):
        """Updates physics ticks, core systems, and runtime timers."""
        if self.state == "PLAYING":
            self.time_left -= 1 / 60
            if self.time_left <= 0:
                self.time_left = 0
                self.state = "GAME_OVER"
                self.fail_reason = "Time Out!" if self.lang == "EN" else "Masa Tamat!"
                if self.sound_lose:
                    self.sound_lose.play()

            for e in self.raft.passengers:
                e.side = self.raft.side
            
            previous_side = self.raft.side
            self.raft.update()
            if previous_side != self.raft.side:
                for passenger in self.raft.passengers:
                    passenger.side = self.raft.side
                
                self.check_bank_safety()
            self.entities.update()

    def draw(self):
        """Renders backgrounds, UI text overlays, assets, panels and game states."""

        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill((34, 139, 34))
            pygame.draw.rect(screen, (30, 144, 255), (250, 0, 500, 500))

        screen.blit(self.raft.image, self.raft.rect)

        if self.state != "MENU":
         self.entities.draw(screen)

        pygame.draw.rect(screen, COLOR_PANEL, (0, 600, SCREEN_WIDTH, 100))
        txt = LOCALIZATION[self.lang]

        score_lbl = self.font_medium.render(f"{txt['score']}: {self.score}", True, COLOR_TEXT)
        timer_lbl = self.font_medium.render(f"{txt['time']}: {int(self.time_left)}s", True, COLOR_TEXT)
        control_lbl = self.font_small.render("[SPACE] Sail Raft | [P] Pause Game | [R] Reset Game", True, COLOR_TEXT)
        
        screen.blit(score_lbl, (40, 615))
        screen.blit(timer_lbl, (40, 650))
        screen.blit(control_lbl, (650, 635))

        # 3. Game State Menu Overlays
        if self.state == "MENU":
            self.draw_overlay_panel()
            title = self.font_large.render(txt["title"], True, COLOR_TEXT)
            start = self.font_medium.render(txt["start"], True, COLOR_TEXT)
            inst = self.font_medium.render(txt["instructions_btn"], True, COLOR_TEXT)
            lang = self.font_small.render(txt["lang_btn"], True, COLOR_TEXT)
            
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
            screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 260))
            screen.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, 320))
            screen.blit(lang, (SCREEN_WIDTH//2 - lang.get_width()//2, 400))

        elif self.state == "INSTRUCTIONS":
            self.draw_overlay_panel()
            title = self.font_large.render(txt["instruct_title"], True, COLOR_TEXT)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            
            for i in range(1, 6):
                line = self.font_small.render(txt[f"rule{i}"], True, COLOR_TEXT)
                screen.blit(line, (150, 160 + (i * 40)))
                
            back = self.font_medium.render(txt["back_main"], True, COLOR_TEXT)
            screen.blit(back, (SCREEN_WIDTH//2 - back.get_width()//2, 420))

        elif self.state == "PAUSED":
            self.draw_overlay_panel()
            p_lbl = self.font_large.render(txt["paused"], True, COLOR_TEXT)
            r_lbl = self.font_medium.render(txt["resume"], True, COLOR_TEXT)
            screen.blit(p_lbl, (SCREEN_WIDTH//2 - p_lbl.get_width()//2, 200))
            screen.blit(r_lbl, (SCREEN_WIDTH//2 - r_lbl.get_width()//2, 280))

        elif self.state == "GAME_OVER":
            self.draw_overlay_panel()
            go_lbl = self.font_large.render("GAME OVER", True, COLOR_WARN)
            reason_lbl = self.font_medium.render(self.fail_reason, True, COLOR_TEXT)
            retry_lbl = self.font_small.render(txt["restart"], True, COLOR_TEXT)
            
            screen.blit(go_lbl, (SCREEN_WIDTH//2 - go_lbl.get_width()//2, 180))
            screen.blit(reason_lbl, (SCREEN_WIDTH//2 - reason_lbl.get_width()//2, 250))
            screen.blit(retry_lbl, (SCREEN_WIDTH//2 - retry_lbl.get_width()//2, 330))

        elif self.state == "WIN":
            self.draw_overlay_panel()
            win_lbl = self.font_large.render(txt["win"], True, COLOR_TEXT)
            fin_score = self.font_medium.render(f"{txt['score']}: {self.score}", True, COLOR_TEXT)
            retry_lbl = self.font_small.render(txt["restart"], True, COLOR_TEXT)
            
            screen.blit(win_lbl, (SCREEN_WIDTH//2 - win_lbl.get_width()//2, 180))
            screen.blit(fin_score, (SCREEN_WIDTH//2 - fin_score.get_width()//2, 250))
            screen.blit(retry_lbl, (SCREEN_WIDTH//2 - retry_lbl.get_width()//2, 330))

        pygame.display.flip()

    def draw_overlay_panel(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        screen.blit(overlay, (0, 0))


# --- RUNTIME ENTRY ---
if __name__ == "__main__":
    game = GameManager()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "PLAYING":
                    game.handle_click(event.pos)
                    
            elif event.type == pygame.KEYDOWN:
                if game.state == "MENU":
                    if event.key == pygame.K_RETURN:
                        game.state = "PLAYING"
                    elif event.key == pygame.K_i:
                        game.state = "INSTRUCTIONS"
                    elif event.key == pygame.K_l:
                        game.lang = "MY" if game.lang == "EN" else "EN"
                        
                elif game.state == "INSTRUCTIONS":
                    if event.key == pygame.K_m:
                        game.state = "MENU"
                        
                elif game.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        game.trigger_raft_move()
                    elif event.key == pygame.K_p:
                        game.state = "PAUSED"
                    elif event.key == pygame.K_r:
                        game.reset_game()
                        
                elif game.state == "PAUSED":
                    if event.key == pygame.K_p:
                        game.state = "PLAYING"
                        
                elif game.state in ["GAME_OVER", "WIN"]:
                    if event.key == pygame.K_r:
                        game.reset_game()
                        game.state = "PLAYING"

        game.update()
        game.draw()
        game.clock.tick(60)