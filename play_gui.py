import baghchal
from baghchal.env import Board
from player import MCTSPlayer
import tkinter as tk
import pygame
import os

pygame.init()

WHITE = (255, 255, 255)
GRAY = (90, 90, 90)

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

board = Board(pgn)

dragging = False
game_exit = False

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
dict_center[(-1, -1)] = goat_coordinate


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


screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Bagh Chal')
clock = pygame.time.Clock()


def gameloop():
    for x in range(1, 6):
        for y in range(1, 6):
            if (x, y) == recent_pointer and dragging:
                pass
            piece = board[x, y]
            if piece:
                if board[x, y].__str__() == "B":
                    screen.blit(bagh_img, (piece.x - 29, piece.y - 29))
                else:
                    screen.blit(goat_img, (piece.x - 30, piece.y - 30))


while not game_exit:
    clock.tick(60)

    screen.fill(WHITE)
    pygame.draw.line(screen, GRAY, (boardX + BOARD_SIZE[0] + 10, 0), (boardX + BOARD_SIZE[0] + 10, DISPLAY_HEIGHT), 4)
    screen.blit(board_img, (boardX, boardY))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            recent_pointer = coordinate_pointing()
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            latest_pointer = coordinate_pointing()
            if recent_pointer and latest_pointer:
                if recent_pointer == 1 and latest_pointer:
                    if latest_pointer != 1:
                        try:
                            board.move(f"G{latest_pointer[0]}{latest_pointer[1]}")
                        except:
                            pass
                else:
                    piece_ = board[recent_pointer[0], recent_pointer[1]]
                    try:
                        board.pure_move(f"{recent_pointer[0]}{recent_pointer[1]}{latest_pointer[0]}{latest_pointer[1]}")
                    except:
                        piece_.x,piece_.y = dict_center[recent_pointer]
            elif recent_pointer or latest_pointer:
                pass
            else:
                piece_=board[recent_pointer[0],recent_pointer[1]]
                piece_.x, piece_.y = dict_center[recent_pointer]
                # if latest_pointer and (latest_pointer not in board.board_dict):
                #     if piece_.__class__==NascentGoat:
                #         goats_placed+=1
                #         if goats_placed==20:
                #             del board.board_dict[recent_pointer]
                #     else:
                #         del board.board_dict[recent_pointer]
                #     board.board_dict[latest_pointer] = piece_
                #     piece_.x, piece_.y = dict_center[latest_pointer]
                #     piece_.coordinate = latest_pointer
                # else:
                #     piece_.x, piece_.y = dict_center[recent_pointer]
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mousex, mousey = pygame.mouse.get_pos()
                try:
                    piece_ = board[recent_pointer[0], recent_pointer[1]]
                    piece_.x = mousex
                    piece_.y = mousey
                except:
                    pass
    pygame.draw.circle(screen, GRAY, goat_coordinate, 30)
    gameloop()
    pygame.display.update()

pygame.quit()
quit()
