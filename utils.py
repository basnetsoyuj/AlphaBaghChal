import numpy as np
import pickle


def softmax(x):
    arr=np.exp(x)
    print(arr)
    return arr/sum(arr)


def mask_illegal(policy_vector, possible_moves):
    # returns new softmax
    valid_policy_vector = policy_vector * possible_moves

    # if all legal positions are masked, return equal prob for all possible moves
    if not valid_policy_vector.any():
        return possible_moves/np.sum(possible_moves)

    return softmax(np.log(valid_policy_vector+1e-10))


def symmetry_board_moves(inputs):
    ''' input -> [(board_repr(5,5,5),pi_vector,value),......]
    output - > [(board_repr(5,5,5),pi_vector,value),......]
    Each input has 8 symmetries including the given input i.e. rotation(0,90,180,270)+flip_horizontal(rotation(0,90,180,270))
    These 8 output for single input encapsulates all rotation and flip horizontally or vertically.
    '''
    from lookup_table import action_space,reversed_action_space
    a = np.empty((5, 5), dtype="<U2")
    for x in range(1, 6):
        for y in range(1, 6):
            a[x - 1, y - 1] = f'{x}{y}'
    output = []
    for board_repr, move_probs, value in inputs:
        moves = []
        probs = move_probs[move_probs != 0]
        for c in range(217):
            if move_probs[c]:
                moves.append(reversed_action_space[c])
        for i in range(4):
            moves_after = []
            tracker = np.rot90(a, i)
            for move in moves:
                if len(move) == 2:
                    l = np.where(tracker == move)
                    moves_after.append(f'{l[0][0]+1}{l[1][0]+1}')
                if len(move) == 4:
                    l1 = np.where(tracker == move[:2])
                    l2 = np.where(tracker == move[2:])
                    moves_after.append(f'{l1[0][0]+1}{l1[1][0]+1}{l2[0][0]+1}{l2[1][0]+1}')
            new_l = [action_space[i] for i in moves_after]
            new_move_probs = np.zeros(217)
            new_move_probs[new_l] = probs
            output.append((np.array([np.rot90(board_repr[0], i), np.rot90(board_repr[1], i), *board_repr[2:]]),
                           new_move_probs, value))
        for i in range(4):
            moves_after = []
            tracker = np.fliplr(np.rot90(a, i))
            for move in moves:
                if len(move) == 2:
                    l = np.where(tracker == move)
                    moves_after.append(f'{l[0][0]+1}{l[1][0]+1}')
                if len(move) == 4:
                    l1 = np.where(tracker == move[:2])
                    l2 = np.where(tracker == move[2:])
                    moves_after.append(f'{l1[0][0]+1}{l1[1][0]+1}{l2[0][0]+1}{l2[1][0]+1}')
            new_l = [action_space[i] for i in moves_after]
            new_move_probs = np.zeros(217)
            new_move_probs[new_l] = probs
            output.append((np.array(
                [np.fliplr(np.rot90(board_repr[0], i)), np.fliplr(np.rot90(board_repr[1], i)), *board_repr[2:]]),
                           new_move_probs, value))
    return output