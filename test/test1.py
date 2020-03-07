'''b=Board("1. G13 B1112 2. G23 B5152 3. G32 B1514 4. G33 B5251 5. G11 B5152 6. G34 B5251 7. G22 B5152 8. G21 B5251 9. G35 B5152 10. G45 B5251 11. G43 B5152 12. G42 B5251 13. G44 B5152 14. G41 B5251 15. G31 B5152 16. G24 B5251 17. G54 B5152 18. G53 B5251 19. G25 B5152 20. G51 B1415 21. G2414 B1524 22. G2515 B2425 23. G3324 Bx5533 24. G5344 Bx3353 25. G4433 B5344 26. G5455 B4443 27. G4253 B4344 28. G3342 B4443 29. G5344 B4353 30. G4433 B5344 31. G4253 B4443 32. G5344 B4353 33. G3342 B5354 34. G4433 B5453 35. G3544 B2535 36. G2425 B5354 37. G1424 B5453 38. G2414 B5354 39. G1424 B5453 40. G2414# 1/2-1/2")
b.lightweight_show_board()
while not b.is_game_over():
    b.move(b.possible_moves().pop())
print(b.pgn)
print(b.board_repr())'''

# mother of luck
# 1. G54 B1112 2. G21 B1213 3. G32 B5152 4. G44 B5253 5. G31 B1324 6. G41 B2423 7. G45 B2324 8. G22 B2423 9. G13 B2324 10. G14 B2423 11. G34 B2324 12. G23 B2425 13. G35 B1524 14. G15 B5343 15. G53 B4342 16. G43 B4233 17. G12 B3342 18. G33 B4252 19. G42 B5251 20. G52# 1-0
import pickle
import numpy as np

with open("data/action_space.pickle", 'rb') as f:
    action_space = pickle.load(f)
reverse_action_space = {value: key for key, value in action_space.items()}
a = np.empty((5, 5), dtype="<U2")
for x in range(1, 6):
    for y in range(1, 6):
        a[x - 1, y - 1] = f'{x}{y}'


def symmetry_board_moves(inputs):
    output=[]
    for board_repr,move_probs,value in inputs:
        moves=[]
        probs=move_probs[move_probs != 0]
        for c in range(217):
            if move_probs[c]:
                moves.append(reverse_action_space[c])
        for i in range(4):
            moves_after = []
            tracker = np.rot90(a, i)
            for move in moves:
                if len(move)==2:
                    l = np.where(tracker == move)
                    moves_after.append(f'{l[0][0]+1}{l[1][0]+1}')
                if len(move)==4:
                    l1 = np.where(tracker == move[:2])
                    l2 = np.where(tracker == move[2:])
                    moves_after.append(f'{l1[0][0]+1}{l1[1][0]+1}{l2[0][0]+1}{l2[1][0]+1}')
            new_l=[action_space[i] for i in moves_after]
            new_move_probs=np.zeros(217)
            new_move_probs[new_l]=probs
            print(moves,moves_after)
            output.append((np.array([np.rot90(board_repr[0],i),np.rot90(board_repr[1],i),*board_repr[2:]]),new_move_probs,value))
        for i in range(4):
            moves_after = []
            tracker = np.fliplr(np.rot90(a, i))
            for move in moves:
                if len(move)==2:
                    l = np.where(tracker == move)
                    moves_after.append(f'{l[0][0]+1}{l[1][0]+1}')
                if len(move)==4:
                    l1 = np.where(tracker == move[:2])
                    l2 = np.where(tracker == move[2:])
                    moves_after.append(f'{l1[0][0]+1}{l1[1][0]+1}{l2[0][0]+1}{l2[1][0]+1}')
            new_l=[action_space[i] for i in moves_after]
            new_move_probs=np.zeros(217)
            new_move_probs[new_l]=probs
            print(moves, moves_after)
            output.append((np.array([np.fliplr(np.rot90(board_repr[0],i)),np.fliplr(np.rot90(board_repr[1],i)),*board_repr[2:]]),new_move_probs,value))
    return output