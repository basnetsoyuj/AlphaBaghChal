import baghchal
from baghchal.env import Board
import tkinter as tk
import pygame
import os
import threading

pygame.init()

WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
MAROON = (128, 0, 0)
GREEN = (0, 77, 26)

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 700

BOARD_SIZE = (472, 471)
PIECE_SIZE = 59

boardX = (DISPLAY_WIDTH - BOARD_SIZE[0]) / 2.5
boardY = (DISPLAY_HEIGHT - BOARD_SIZE[1]) / 2
BASEDIR = os.path.dirname(baghchal.__file__)
os.chdir(BASEDIR)

board_img = pygame.image.load("images/board.png")
bagh_img = pygame.image.load("images/bagh.png")
goat_img = pygame.image.load("images/goat.png")
dead_goat = pygame.image.load("images/dead_goat.png")
trapped_bagh = pygame.image.load("images/trapped_bagh.png")

CHOICE = [("Human Player", 0), ("AI player", 1)]


class ChoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        tk.Label(self, text="Bagh Chal Game",
                 font='Helvetica 18 bold').grid(row=0, column=2)
        tk.Label(self, text="GOAT", font='Helvetica 12 bold').grid(row=2, column=1)
        self.goat = tk.IntVar()
        self.goat.set(0)
        self.buttons = [self.create_radio(c, self.goat) for c in CHOICE]
        row = 3
        for button in self.buttons:
            button.grid(row=row, column=1, sticky=tk.W, padx=20, pady=10)
            row += 1
        self.bagh = tk.IntVar()
        self.bagh.set(0)
        self.buttons = [self.create_radio(c, self.bagh) for c in CHOICE]
        row = 3
        tk.Label(self, text="BAGH", font='Helvetica 12 bold').grid(row=2, column=5)
        for button in self.buttons:
            button.grid(row=row, column=5, sticky=tk.W, padx=20, pady=10)
            row += 1
        button = tk.Button(self, text="Play", width=10, command=self.storepgn)
        tk.Label(self, text="Enter Game PGN to import Game State (Optional) :").grid(row=5, column=2)
        self.pgn = tk.Text(width=40, height=5)
        self.pgn.grid(row=6, column=2, pady=10)
        button.grid(row=7, column=2, pady=10)
        self.mainloop()

    def storepgn(self):
        self.pgn = self.pgn.get("1.0", 'end-1c')
        self.destroy()

    def create_radio(self, option, variable):
        text, value = option
        return tk.Radiobutton(self, text=text, value=value, variable=variable)

    def return_input(self):
        return self.goat.get(), self.bagh.get(), self.pgn


app = ChoiceApp()
goat_player, bagh_player, pgn = app.return_input()
if goat_player or bagh_player:
    # from player import MCTSPlayer
    from baghchal.engine import Engine

    AI = Engine(4)


    def make_best_move():
        global agent
        board.move(AI.get_best_move(board)[0])
        agent = 0
board = Board(pgn)


class Button:
    def __init__(self, rect, command):
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill((48, 64, 66))
        self.function = command

    def on_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.function()

    def draw(self, surf):
        surf.blit(self.image, self.rect)


dragging = False
game_exit = False
real_dragging = False
recent_pointer = (0, 0)

func = lambda x, y: (round(x / 100) + 1, round(y / 100) + 1)
goat_coordinate = (int(boardX + BOARD_SIZE[0]) + 100, 100)
dict_center = {}
i = 0
for x in range(1, 6):
    j = 0
    for y in range(1, 6):
        dict_center[(y, x)] = (boardX + 30 + i, boardY + 30 + j)
        j += 103
    i += 103
dict_center[1] = goat_coordinate

convert = lambda x: "Bagh" if x == "B" else "Goat"


def coordinate_pointing():
    x, y = pygame.mouse.get_pos()
    if boardX + BOARD_SIZE[0] > x > boardX and boardY + BOARD_SIZE[1] > y > boardY:
        rel_x = (x - boardX - 30)
        rel_y = (y - boardY - 30)
        standardX, standardY = dict_center[func(rel_y, rel_x)]
        if standardX + 30 > x > standardX - 30 and standardY + 30 > y > standardY - 30:
            return func(rel_y, rel_x)
        else:
            return 0
    elif goat_coordinate[0] + 30 > x > goat_coordinate[0] - 30 and goat_coordinate[1] + 30 > y > goat_coordinate[
        1] - 30:
        return 1
    else:
        return 0


def undo():
    try:
        board.undo()
    except:
        pass


screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Bagh Chal')
clock = pygame.time.Clock()
dragblit = 0
font = pygame.font.Font('freesansbold.ttf', 25)
font1 = pygame.font.Font('freesansbold.ttf', 20)
undo_btn = Button(rect=(640, 225, 160, 45), command=undo)
agent = 0


def render_text(font, text, color, bgcolor, x, y):
    texts = font.render(text, True, color, bgcolor)
    rect = texts.get_rect()
    rect.center = (x, y)
    screen.blit(texts, rect)


def blit_piece(piece, position):
    if piece == "B":
        screen.blit(bagh_img, position)
    else:
        screen.blit(goat_img, position)


def infoblit():
    screen.blit(trapped_bagh, (15, 5))
    render_text(font, f'Baghs Trapped: {board.baghs_trapped}', (17, 17, 17), WHITE, 180, 30)
    render_text(font, f'Goats Captured: {board.goats_captured}', (17, 17, 17), WHITE, 505, 30)
    render_text(font, f'{20-board.goats_placed}', (17, 17, 17), WHITE, 705, 50)
    screen.blit(dead_goat, (330, 8))
    if board.is_game_over():
        render_text(font, f" Game Over! ", WHITE, MAROON, 720, 175)
        winner = convert(board.winner())
        if board.winner():
            render_text(font1, f" Winner: {winner} ", GRAY, WHITE, 720, 200)
        else:
            render_text(font1, f" Draw: 1/2-1/2 ", GRAY, WHITE, 720, 200)
    else:
        render_text(font, f" {convert(board.next_turn)}'s Turn ", WHITE, GRAY, 720, 200)
    if board.moves:
        render_text(font1, board.pgn[-70:], (17, 17, 17), WHITE, 400, 620)
    undo_btn.draw(screen)
    render_text(font, "UNDO", WHITE, (48, 64, 66), 720, 250)


def gameloop():
    for x in range(1, 6):
        for y in range(1, 6):
            if (x, y) == recent_pointer and real_dragging:
                continue
            piece = board[x, y]
            if piece:
                if board[x, y].__str__() == "B":
                    screen.blit(bagh_img, (piece.x - 29, piece.y - 29))
                else:
                    screen.blit(goat_img, (piece.x - 30, piece.y - 30))
    if board.goats_placed < 20:
        screen.blit(goat_img, (goat_coordinate[0] - 30, goat_coordinate[1] - 30))
    if dragblit:
        blit_piece(dragblit[0], dragblit[1])


while not game_exit:
    clock.tick(60)

    screen.fill(WHITE)
    pygame.draw.line(screen, GRAY, (boardX + BOARD_SIZE[0] + 35, 0), (boardX + BOARD_SIZE[0] + 35, 595), 4)
    pygame.draw.line(screen, GRAY, (0, 595), (DISPLAY_WIDTH, 595), 4)
    screen.blit(board_img, (boardX, boardY))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            recent_pointer = coordinate_pointing()
            if recent_pointer:
                dragging = True
                x, y = dict_center[recent_pointer]
                x, y = x - 29, y - 29
                if recent_pointer == 1:
                    blit_piece("G", (x, y))
                else:
                    piece = board[recent_pointer[0], recent_pointer[1]]
                    if piece:
                        blit_piece(piece.__str__(), (x, y))
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            real_dragging = False
            dragblit = 0
            latest_pointer = coordinate_pointing()
            if (goat_player == 0 and board.next_turn=="G") or (bagh_player == 0 and board.next_turn=="B"):
                if recent_pointer == 1:
                    try:
                        board.move(f'G{latest_pointer[0]}{latest_pointer[1]}')
                    except:
                        pass
                else:
                    try:
                        board.pure_move(f'{recent_pointer[0]}{recent_pointer[1]}{latest_pointer[0]}{latest_pointer[1]}')
                    except:
                        pass
            undo_btn.on_click(event)
        elif event.type == pygame.MOUSEMOTION:
            if dragging and recent_pointer:
                real_dragging = True
                mousex, mousey = pygame.mouse.get_pos()
                if recent_pointer == 1:
                    dragblit = ("G", (mousex - 29, mousey - 29))
                else:
                    piece = board[recent_pointer[0], recent_pointer[1]]
                    if piece:
                        dragblit = (piece.__str__(), (mousex - 30, mousey - 30))
    pygame.draw.circle(screen, GRAY, goat_coordinate, 28)
    infoblit()
    gameloop()
    if ((goat_player and board.next_turn == "G") or (
            bagh_player and board.next_turn == "B")) and not board.is_game_over() and not agent:
        try:
            agent = threading.Thread(target=make_best_move)
            agent.start()
        except:
            pass
    pygame.display.update()

pygame.quit()
print(board.pgn)
quit()
#1. G53 B5545 2. G54 B4555 3. G31 B5545 4. G55 B1524 5. G15 B2414 6. G21 B1413 7. G12 B1322 8. G13 B2223 9. G14 B4544 10. G45 B4435 11. G44 B5152 12. G43 B5251 13. G52 B3534 14. G35 B1122 15. G11 B3433 16. G25 B2324 17. G23 B3334 18. G41 B5142 19. G51 B2232 20. G33 Bx2422 21. G1524 B2223 22. G1122# 1-0
