'''
FEN -> Similar to Forsyth–Edwards Notation in chess
    Starting fen => "B3B/5/5/5/B3B G 0"
        {"B3B/5/5/5/B3B"(similar to chess,"B" - Bagh, "G" - Goat)}
        {"G" or "B" represents who has next move}
        {"0" number of moves by goat}
PGN -> Portable Game Notation like in chess
        Move to move tracking notation
        <Move number>. G(<old_position>)<new_position> (...B<old_position><new_position>)
        Example : 1.G33 B1122 2.G44
        [ Note: G<new_position> for unplaced piece ]
'''
import re
from collections import Counter
import numpy as np
from lookup_table import bagh_moves_dict,connected_points_dict,action_space

class Board:

    def __init__(self, description=""):
        self.reset()
        if description.strip():
            self.pgn_converter(description.strip())

    def __getitem__(self, index):
        return self.board[index[0] - 1][index[1] - 1]

    def __setitem__(self, index, value):
        self.board[index[0] - 1][index[1] - 1] = value

    @property
    def no_of_moves_made(self):
        return self.no_of_goat_moves + self.no_of_bagh_moves

    def _possible_goat_moves(self):
        # the function is independent of whose turn it is to play, use at your own risk.
        move_list = set()
        if self.no_of_goat_moves < 20:
            return {f'G{x1}{y1}' for x1 in range(1, 6) for y1 in range(1, 6) if
                    (x1, y1) not in self.bagh_points.union(self.goat_points)}
        else:
            for x1, y1 in self.goat_points:
                move_list.update({f'G{x1}{y1}{x2}{y2}' for x2, y2 in self[x1, y1].valid_moves()})
            return move_list

    def _possible_bagh_moves(self):
        # the function is independent of whose turn it is to play, use at your own risk.
        move_list = set()
        for x1, y1 in self.bagh_points:
            move_list.update({f'B{x1}{y1}{x2}{y2}' for x2, y2 in self[x1, y1].valid_non_special_moves()})
            move_list.update({f'Bx{x1}{y1}{x2}{y2}' for x2, y2 in self[x1, y1].valid_bagh_moves()})
        return move_list

    def possible_moves(self):
        if self.is_game_over():
            return 0
        if self.next_turn == "G":
            return self._possible_goat_moves()
        else:
            return self._possible_bagh_moves()

    def possible_moves_vector(self):
        moves_vector = np.zeros(217)
        if self.is_game_over():
            return moves_vector
        if self.next_turn == "G" and self.no_of_goat_moves < 20:
            for x1 in range(1, 6):
                for y1 in range(1, 6):
                    if (x1, y1) not in self.bagh_points.union(self.goat_points):
                        moves_vector[action_space[f'{x1}{y1}']] = 1
        elif self.next_turn == "G" and self.no_of_goat_moves >= 20:
            for x1, y1 in self.goat_points:
                for x2, y2 in self[x1, y1].valid_moves():
                    moves_vector[action_space[f'{x1}{y1}{x2}{y2}']] = 1
        else:
            for x1, y1 in self.bagh_points:
                for x2, y2 in self[x1, y1].valid_moves():
                    moves_vector[action_space[f'{x1}{y1}{x2}{y2}']] = 1
        return moves_vector

    def pgn_converter(self, pgn):
        move_list = re.findall(
            r'[0-9]+\.\s*([G][1-5]{2,4})\s*([B][x]?[1-5]{4})?', pgn)
        for moves in move_list:
            for move in moves:
                if move == "":
                    break
                self.move(move)

    def fen_to_board(self, fen):
        rows = fen.split(" ")[0].split("/")
        for x in range(5):
            counter = 1
            for y in rows[x]:
                if y == "B":
                    Bagh(self, (x + 1, counter))
                    counter += 1
                elif y == "G":
                    Bagh(self, (x + 1, counter))
                    counter += 1
                else:
                    for _ in range(int(y)):
                        counter += 1

    @property
    def baghs_trapped(self):
        counter = 0
        for bagh in self.bagh_points:
            if not self[bagh[0], bagh[1]].valid_moves():
                counter += 1
        return counter

    @property
    def all_goats_trapped(self):
        return self.next_turn == "G" and not self._possible_goat_moves()

    def show_info(func):
        def wrapper(self):
            if self.no_of_moves_made:
                print(f"Last move: {self.moves[-1]}")
            print(
                f"Goats Placed: {self.goats_placed}, Goats Captured: {self.goats_captured}, Baghs Trapped: {self.baghs_trapped}")
            func(self)
            if self.is_game_over():
                print("Game over.")
                if self.winner():
                    print(f"Winner : {self.winner()}")
                else:
                    print(f"The game is a draw.")
                return
            print(f"{self.next_turn} to play.")
            print(f"Possible moves:", end="")
            for move in self.possible_moves():
                print(f" {move}", end="")
            print()
            print()
        return wrapper

    @show_info
    def show_board(self):
        rep1 = ''' ¦ ＼         ¦         ／ ¦ ＼         ¦         ／ ¦    
 ¦   ＼       ¦       ／   ¦   ＼       ¦       ／   ¦    
 ¦     ＼     ¦     ／     ¦     ＼     ¦     ／     ¦    
 ¦       ＼   ¦   ／       ¦       ＼   ¦   ／       ¦    
 ¦         ＼ ¦ ／         ¦         ＼ ¦ ／         ¦    '''
        rep2 = ''' ¦         ／ ¦ ＼         ¦          ／¦ ＼         ¦    
 ¦       ／   ¦   ＼       ¦        ／  ¦   ＼       ¦    
 ¦     ／     ¦     ＼     ¦      ／    ¦     ＼     ¦    
 ¦   ／       ¦       ＼   ¦    ／      ¦       ＼   ¦    
 ¦ ／         ¦         ＼ ¦  ／        ¦         ＼ ¦    '''
        print(
            f"[{self[1,1]}]11--------[{self[1,2]}]12--------[{self[1,3]}]13--------[{self[1,4]}]14--------[{self[1,5]}]15")
        print(rep1)
        print(
            f"[{self[2,1]}]21--------[{self[2,2]}]22--------[{self[2,3]}]23--------[{self[2,4]}]24--------[{self[2,5]}]25")
        print(rep2)
        print(
            f"[{self[3,1]}]31--------[{self[3,2]}]32--------[{self[3,3]}]33--------[{self[3,4]}]34--------[{self[3,5]}]35")
        print(rep1)
        print(
            f"[{self[4,1]}]41--------[{self[4,2]}]42--------[{self[4,3]}]43--------[{self[4,4]}]44--------[{self[4,5]}]45")
        print(rep2)
        print(
            f"[{self[5,1]}]51--------[{self[5,2]}]52--------[{self[5,3]}]53--------[{self[5,4]}]54--------[{self[5,5]}]55")

    def validate_placement(self, move):
        x1, y1 = int(move[1]), int(move[2])
        self.validate_points(move, x1, y1)
        if not self.goats_placed < 20:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} More than 20 goats cannot be placed")
        if self[x1, y1]:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} The coordinate is already occupied.")
        return True

    def validate(self, move):
        if self.is_game_over():
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} The game is already over.")
        move = move.strip()
        if len(move) not in {3, 5, 6}:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Error ! Could not recognise the move.")
        if move[0] != self.next_turn:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Illegal Move.It is other side's turn.")
        if move[:2] == "Bx":
            return self.validate_capture(move)
        if len(move) == 3:
            if self.goats_placed >= 20:
                raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Futher piece cannot be placed.")
            if move[0] == "B":
                raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Further Bagh cannot be placed.")
            return self.validate_placement(move)
        if move[0] == "G" and len(move) == 5 and self.no_of_goat_moves < 20:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} All the goats must be placed first.")
        if move[:2] == "Gx":
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Goats cannot capture.")
        x1, y1, x2, y2 = int(move[1]), int(move[2]), int(move[3]), int(move[4])
        self.validate_points(move, x1, y1, x2, y2)
        self.validate_pp(move, x1, y1, move[0])

        if move[0]=="G":
            if not ((x2, y2) in self[x1, y1].valid_moves()):
                raise Exception(
                f"{(self.no_of_moves_made+2)//2}.{move} is not a valid move.")
        elif move[0]=="B":
            if not ((x2, y2) in self[x1, y1].valid_non_special_moves()):
                raise Exception(
                f"{(self.no_of_moves_made+2)//2}.{move} is not a valid move.")
        return True

    def validate_capture(self, move):
        x1, y1, x2, y2 = int(move[2]), int(move[3]), int(move[4]), int(move[5])
        self.validate_points(move, x1, y1, x2, y2)
        self.validate_pp(move, x1, y1, move[0])
        if not ((x2, y2) in self[x1, y1].valid_bagh_moves()):
            raise Exception(
                f"{(self.no_of_moves_made+2)//2}.{move} is not a valid move.")
        return True

    def validate_points(self, move, x1, y1, x2=1, y2=1):
        if not (0 < x1 < 6 and 0 < y1 < 6 and 0 < x2 < 6 and 0 < y2 < 6):
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Invalid PGN. Coordinates not in range.")

    def validate_pp(self, move, x1, y1, p):
        if not self[x1, y1]:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} ({x1},{y1}) is not occupied.")
        if self[x1, y1].__str__() != p:
            raise Exception(f"{(self.no_of_moves_made+2)//2}.{move} Piece at ({x1},{y1}) is other than specified.")

    def safe_move(self, move):
        if len(move) == 3:
            Goat(self, (int(move[1]), int(move[2])))
            self.no_of_goat_moves += 1
            self.goats_placed += 1
        else:
            if len(move) == 5:
                x1, y1, x2, y2 = int(move[1]), int(
                    move[2]), int(move[3]), int(move[4])
            elif len(move) == 6:
                x1, y1, x2, y2 = int(move[2]), int(
                    move[3]), int(move[4]), int(move[5])
                x3, y3 = (x1 + x2) // 2, (y1 + y2) // 2
                self[x3, y3] = 0
                self.goat_points.remove((x3, y3))
                self.goats_captured += 1
            self[x1, y1] = 0
            if move[0] == "G":
                self.goat_points.remove((x1, y1))
                Goat(self, (x2, y2))
                self.no_of_goat_moves += 1
            elif move[0] == "B":
                self.bagh_points.remove((x1, y1))
                Bagh(self, (x2, y2))
                self.no_of_bagh_moves += 1

        self.moves.append(move)
        pgn_update = ""
        if self.next_turn == "G":
            pgn_update += f"{self.no_of_goat_moves}. "
        pgn_update += move
        self.pgn += " " + pgn_update
        self.next_turn = "G" if self.next_turn == "B" else "B"

        self.fen = self.board_to_fen()
        self.fen_history.append(self.fen)
        if self.no_of_goat_moves >= 20:
            self.fen_count.update([self.fen.split(" ")[0]])

        if self.is_game_over():
            if self.winner() == "B":
                self.pgn += "# 0-1"
            elif self.winner() == "G":
                self.pgn += "# 1-0"
            else:
                self.pgn += "# 1/2-1/2"

    def board_to_fen(self):
        string = ""
        for x in range(1, 6):
            counter = 0
            for y in range(1, 6):
                if self[x, y]:
                    counter = 0
                    string += self[x, y].__str__()
                else:
                    counter += 1
                    if y == 5 or self[x, y + 1] != 0:
                        string += str(counter)
            string += "/"
        return f"{string[:-1]} {self.next_turn} {self.no_of_goat_moves}"

    def move(self, move):
        if self.validate(move):
            self.safe_move(move)

    def pure_move(self,move):
        if len(move) == 2:
            self.move(f"G{move}")
        else:
            x1, y1, x2, y2 = move
            if (int(x1) - int(x2))**2 + (int(y1) - int(y2))**2 <= 2:
                self.move(f"{self.next_turn}{move}")
            else:
                self.move(f'{self.next_turn}x{move}')

    def is_game_over(self):
        if self.goats_captured >= 5 or self.baghs_trapped == 4 or self.check_draw() or self.all_goats_trapped:
            return True
        return False

    def check_draw(self):
        if max(self.fen_count.values()) >= 3:
            return 1
        return 0

    def winner(self):
        if self.goats_captured >= 5 or self.all_goats_trapped:
            return "B"
        if self.baghs_trapped == 4:
            return "G"
        if self.check_draw():
            return 0
        raise Exception("Game is not over yet !")

    def fen_state(self, fen):
        state = np.zeros((2, 5, 5))
        rows = fen.split(" ")[0].split("/")
        for x in range(5):
            counter = 0
            for y in rows[x]:
                if y == "G":
                    state[0, x, counter] = 1
                    counter += 1
                elif y == "B":
                    state[1, x, counter] = 1
                    counter += 1
                else:
                    for _ in range(int(y)):
                        counter += 1
        return state

    def board_repr(self):
        state = np.zeros((5, 5, 5))
        state[[0, 1]] = self.fen_state(self.fen)
        state[2, :, :] = self.goats_captured
        state[3, :, :] = self.baghs_trapped
        if self.next_turn == "G":
            state[4, :, :] = 1
        return state

    def reset(self):
        self.board = [[0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0]]
        self.next_turn = "G"
        self.no_of_goat_moves = 0
        self.no_of_bagh_moves = 0
        self.goats_placed = 0
        self.goats_captured = 0
        self.goat_points = set()
        self.bagh_points = set()
        self.fen = "B3B/5/5/5/B3B G 0"
        self.fen_history = [self.fen]
        self.fen_count = Counter([self.fen.split(" ")[0]])
        self.pgn = ""
        self.moves = list()
        self.fen_to_board(self.fen)

    def recent_player(self):
        return "G" if self.no_of_moves_made % 2 else "B"

    def undo(self, no_of_moves=1):
        if no_of_moves > self.no_of_moves_made:
            raise Exception(
                "The number of moves to undo is greater than the number of moves made in the board.")
        move_list = self.moves
        n = self.no_of_moves_made - no_of_moves
        self.reset()
        for move in move_list:
            if move == "" or n == 0:
                return move_list[-no_of_moves:]
            self.move(move)
            n -= 1

    @show_info
    def lightweight_show_board(self):
        print("-" * 26)
        for row in self.board:
            for x in row:
                if x:
                    print(f"| {x.__str__()} ", end=" ")
                else:
                    print("|   ", end=" ")
            print("|")
            print("-" * 26)


class Piece:

    def __init__(self, board, position=0):
        if position:
            if not (1, 1) <= position <= (5, 5):
                raise Exception(f"Invalid Coordinate for {self.__repr__()} - {position}")
            if board[position[0], position[1]]:
                raise Exception(
                    f"Cannot place {self.__repr__()} at coordinate {position} occupied by {board[position[0],position[1]].__repr__()}")
        self.position = position
        self.board = board
        self.board[position[0], position[1]] = self

    def connected_points(self):
        if self.position:
            return connected_points_dict[self.position]
        else:
            return 0

    def valid_moves(self):
        return {x for x in self.connected_points()
                if not self.board[x[0], x[1]]}


class Bagh(Piece):

    def __init__(self, board, position):
        super(Bagh, self).__init__(board, position)
        self.board.bagh_points.add(position)

    def __str__(self):
        return "B"

    def __repr__(self):
        return "Bagh"

    def special_connected_points(self):
        return bagh_moves_dict[self.position]

    def valid_bagh_moves(self):
        return {x for x in self.special_connected_points()
                if (not self.board[x[0], x[1]]) and self.board[
                    (x[0] + self.position[0]) // 2, (x[1] + self.position[1]) // 2].__class__ == Goat}

    def valid_moves(self):
        return super(Bagh, self).valid_moves().union(self.valid_bagh_moves())

    def valid_non_special_moves(self):
        return super(Bagh, self).valid_moves()


class Goat(Piece):

    def __init__(self, board, position):
        super(Goat, self).__init__(board, position)
        self.board.goat_points.add(position)

    def __str__(self):
        return "G"

    def __repr__(self):
        return "Goat"
