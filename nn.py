import random
import torch as tr
import numpy as np
import ChessMain as cm
import numpy as np
import csv
import ChessEngine
from sklearn.linear_model import LinearRegression

pieceScore = {"K": 1, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 2}
pieces = ['bK','bQ','bR','bB','bN','bp','wK','wQ','wR','wB','wN','wp','--']
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
states = []
win = 0
brd = []
hotencode_1 = []
final=[]
nb_classes = 13
state_log = []
training_data = []
testing_data = []
net = tr.nn.Linear(0,0)



# training_data,testing_data = ChessMain.read_from_csv()




def baseline_error():
    _, utilities = cm.state_log
    baseline_error =sum((u-0)**2 for u in utilities) / len(utilities)
    print(utilities)
    print(baseline_error)

class LinNet(tr.nn.Module):
    def __init__(self, size, hid_features):
        super(LinNet, self).__init__()
        self.to_hidden = tr.nn.Linear(13*size**2, hid_features)
        self.to_output = tr.nn.Linear(hid_features, 1)
    def forward(self, x):
        h = tr.relu(self.to_hidden(x.reshape(x.shape[0],-1)))
        y = tr.tanh(self.to_output(h))
        return y

def encode(gs):
    # Convert an iterable of indices to one-hot encoded labels.
    board = gs.board
    print(len(board))
    print(len(board[0]))
    for j in range(len(pieces)):
        for k in board:
            for l in k:
                if (l == pieces[j]):
                    brd.append(1)
                else:
                    brd.append(0)
    # targets = np.array(hotencode).reshape(-1)
    # array_he = np.eye(nb_classes)[targets]
    # hotencode = [[i for i in j] for j in array_he]
    hotencode_list = np.array(brd)
    brd_state = hotencode_list.reshape(13,8,8)
    print(brd_state)
    # print(len(hot_arr))
    # return hot_arr
    # symbols = tr.tensor(['bK','bQ','bR','bB','bN','bp','wK','wQ','wR','wB','wN','wp','--']).reshape(-1,2,1)
    # symbols = tr.tensor([0,1,2,3,4,5,6,7,8,9,10,11,12]).reshape(-1,1,1)
    # onehot = (symbols == brd_state).float()
    return brd_state


def example_error(net, example):
    state, utility = example
    x = encode(state).unsqueeze(0)
    y = net(x)
    e = (y - utility)**2
    return e

def batch_error(net, batch):
    states, utilities = batch
    u = utilities.reshape(-1,1).float()
    y = net(states)
    e = tr.sum((y - u)**2) / utilities.shape[0]
    return e


def training():
    

    # Make the network and optimizer
    # Arpit approach for Neural Network
    net = LinNet(size=8, hid_features=16)
    optimizer = tr.optim.SGD(net.parameters(), lr=0.001)


    file = open("training_dataset.csv", "r", newline='')
    with file:
        reader = csv.reader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            state_log.append((row[0], row[1]))
    file.close()
    print(state_log[0])
    training_data = state_log[:500]
    testing_data = state_log[500:1000]
    print(len(training_data))
    training_gs = []
    testing_gs = []
    for i in range(500):    
        
        states,utilities = training_data[i]
        states.split('\n')
        s = states.replace('[','').replace(']','').replace("'", '').split('\n')
        board = [i.split() for i in s]
        gs1 = ChessEngine.GameState((-1,-1),board)
        training_gs.append(gs1)
        np.array(board,str)
    
        states, utilities = testing_data[i]
        states.split('\n')
        s = states.replace('[','').replace(']','').split('\n')
        board = [i.split() for i in s]
        gs2 = ChessEngine.GameState((-1,-1),board)
        testing_gs.append(gs2)
        np.array(board,str)
    
    training_batch = tr.stack(tuple(map(encode, training_gs))), tr.tensor(utilities)
    testing_batch = tr.stack(tuple(map(encode, testing_gs))), tr.tensor(utilities)

        
    curves = [], []
    for epoch in range(50000):
        
            
        optimizer.zero_grad()

           
        if not batched:
    
            training_error, testing_error = 0, 0

            for n, example in enumerate(zip(*training_data)):
                e = example_error(net, example)
                e.backward()
                training_error += e.item()
            training_error /= len(training_data)

            with tr.no_grad(): # less computationally expensive
                for n, example in enumerate(zip(*testing_data)):
                    e = example_error(net, example)
                    testing_error += e.item()
                testing_error /= len(testing_data)

            # batch version (fast)
        if batched:
            e = batch_error(net, training_batch)
            e.backward()
            training_error = e.item()

            with tr.no_grad():
                e = batch_error(net, testing_batch)
                testing_error = e.item()

            # take the next optimization step
        optimizer.step()    
            
            # print/save training progress
        if epoch % 1000 == 0:
            print("%d: %f, %f" % (epoch, training_error, testing_error))
        curves[0].append(training_error)
        curves[1].append(testing_error)

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove_nn(gs, validMoves):
    # print(states)
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta_nn(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    # if (gs.checkMate == True or gs.staleMate == True or gs.drawGame == True):
    #     checkRemPieces(gs,gs.board)
    #     print(len(states))
    #     indices_to_one_hot(states)
    return nextMove

def findMoveNegaMax_nn(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax_nn(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta_nn(gs, validMoves, depth, alpha, beta, turnMultiplier):
    training()
    global nextMove
    if depth == 0:
        x = encode(gs).unsqueeze(0)
        u = net(x)
        return turnMultiplier * u

    maxScore = -CHECKMATE
    for move in validMoves:
        # print(move.pieceMoved)
        # print((move.startRow, move.startCol))
        # print((move.endRow, move.endCol))
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta_nn(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0

    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score
