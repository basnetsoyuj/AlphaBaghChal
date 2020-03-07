from copy import deepcopy
INF = 1e6


class Engine:

    def __init__(self, depth=5):
        self.depth = depth

    def static_evaluation(self, board):
        end = board.is_game_over()
        if not end:
            return 1.5 * board.baghs_trapped - 1.2 * board.goats_captured
        winner = board.winner()
        if winner == "G":
            return INF
        elif winner == "B":
            return -INF
        else:
            return 0

    def minimax(self, board, depth=0, alpha=-INF, beta=INF, maxPlayer=True):
        if depth == 0 or board.is_game_over():
            return 0, self.static_evaluation(board)

        if maxPlayer:
            maxEval = -INF*10
            best_move = 0
            for move in board.possible_moves():
                b_copy = deepcopy(board)
                b_copy.move(move)
                eval_ = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                if eval_ > maxEval:
                    maxEval = eval_
                    best_move = move
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            return best_move, maxEval
        else:
            minEval = INF*10
            best_move = 0
            move_list = list(board.possible_moves())
            move_list.sort(key=lambda a: 5-len(a))
            for move in move_list:
                b_copy = deepcopy(board)
                b_copy.move(move)
                eval_ = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if eval_ < minEval:
                    minEval = eval_
                    best_move = move
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return best_move, minEval

    def _best_bagh_move(self, board):
        assert not board.is_game_over()
        return self.minimax(board, self.depth, maxPlayer=False)

    def _best_goat_move(self, board):
        assert not board.is_game_over()
        return self.minimax(board, self.depth, maxPlayer=True)

    def get_best_move(self, board):
        if board.next_turn == "G":
            result = self._best_goat_move(board)
        else:
            result = self._best_bagh_move(board)
        return result
