#!/usr/bin/python
"""
Originally by Jason Schapiro 2012

# Next steps:
# X 1. Implement game-over evaluation func
# X 2. Alpha-beta search
# X 3. Alpha-beta info
# 4. Starting screen - choose player
# X 5. Double jumps

Modified by M L Walters, 2014
For use with BAxter Robot Draughts Game

"""




# Load Baxter Robot actions
import baxterDo_Dummy as bxd
import copy

BOARD_SIZE = 8
NUM_PLAYERS = 12
depth = 3
# the players array extends to many other arrays in the program
# in these arrays, 0 will refer to black and 1 to white
PLAYERS = ["Black", "White"]
board = [ [[0.0, 0.0]]*8 ] *8 # 2D array, translates game positions for robot

playr = 1 # Human player, default = 1 = Black 

class Game:
    def __init__(self, player=0):
        self.board = Board()
        # refers to how many pieces that play
        self.remaining = [NUM_PLAYERS, NUM_PLAYERS]
        # default player is black
        self.player = player
        self.turn = 0
    
    
    def run(self):
        #Turn cycle
        while not (self.gameOver(self.board)):
            #Initiate turn
            self.initiateTurn()           
            #Human's turn to play
            if (self.turn == self.player):
                self.humanTurn()                                                
            #AI's turn to play
            else:
                self.aiTurn()
            #End turn
            self.endTurn()                        
        #Game over    
        self.gameEnd()
    
    
    
    #Game setups    
    def initiateTurn(self):
        print("Start of turn.")
        print("Current Player: "+PLAYERS[self.turn]+"\n")      
        self.board.drawBoardState()
    
    
    def endTurn(self):
        self.turn = 1-self.turn
        print("  \n")
        print("End of turn.  \n")
        print("  \n")
  
        
    def gameEnd(self):
        print("Game OVER")
        print("Black Captured: "+str(NUM_PLAYERS-self.remaining[1]))
        print("White Captured: "+str(NUM_PLAYERS-self.remaining[0]))
        score = self.calcScore(self.board)
        print("Black Score: "+str(score[0]))
        print("White Score: "+str(score[1]))
        if (score[0] > score[1]):
              print("Black wins!")
        elif (score[1] > score[0]):
              print("White wins!")
        else:
            print("It's a tie!")
    
    
    
    #Game turns
    def humanTurn(self):
        #Function finds possible plays and lets human determine which play to use
        
        legal = self.board.calcLegalMoves(self.turn) #Determine list of possible plays
        
        if (len(legal) > 0):
            #If there is any play possible, let the human choose
            move = self.getMove(legal) #Get human to input its choice  !! COULD CHANGE TO BAXTER_DO !!                  
            self.makeMove(move) #Human moves the piece
            print("HUMAN:", move.start)
        else:
            #If there is not any play available, human input is not needed
            print("No legal moves available, skipping turn...")    
   
        
    def aiTurn(self):
        #Function lets AI choose the best possible play
        
        legal = self.board.calcLegalMoves(self.turn) #Determine list of possible plays
        
        self.listMoves(legal) #Prints out list of possible moves
                          
        if (len(legal)>0):
            # If there is any play possible, let the AI choose
            if (len(legal)==1):
                #If there is only one possible play, AI isn't needed
                move = legal[0] #Make the only play possible 
            else:
                #If there are more than one possible play, AI makes the choice
                state = AB_State(self.board, self.turn, self.turn)
                move = self.minmax(copy.deepcopy(state.board), True, 3)[1]                
                
            self.makeMove(move) #Make the move according to AI's choice
            print("Computer chooses ("+str(move.start)+", "+str(move.end)+")")

            #robot_move(move) # Robot moving routine
         
        else:
            #If there is not any play available, AI input is not needed
            print("No legal moves available, skipping turn...")    

    

    #Game functionalities     
    def listMoves(self, legal):
        #Function prints out legal moves
        
        print("Valid Moves: ")
        
        for i in range(len(legal)):
            #Loop to print out every sublist inside legal
            print (str(i+1)+": ")
            print (str(legal[i].start)+" "+str(legal[i].end))        
        
               
    def makeMove(self, move):
        #Function to make the chosen move
        
        self.board.boardMove(move, self.turn) # Update board according to move chosen
        
        if move.jump:
            #If a jump was made over an enemy's piece
            self.remaining[1-self.turn] -= len(move.jumpOver) #Deduct a piece from the enemy
            print("Removed "+str(len(move.jumpOver))+" "+PLAYERS[1-self.turn]+" pieces")
            
        
    def getMove(self, legal):
        move = -1

        # repeats until player picks move on the list
        while move not in range(len(legal)):
            self.listMoves(legal)                        
            usr_input = input("Pick a move: ") 
                        
            # stops error caused when user inputs nothing
            if (usr_input == ''):
                move = -1 
            else:
                move = int(usr_input)-1            
            #Check move ok
            if move not in range(len(legal)):
                print("Illegal move")

        print("Legal move")
        return (legal[move])
        
    def gameOver(self, board):
        # returns a boolean value determining if game finished

        if (len(board.currPos[0]) + len(board.blackKings) == 0) or (len(board.currPos[1]) + len(board.whiteKings) == 0):
            # all pieces from one side captured
            return True

        elif (len(board.calcLegalMoves(0)) == 0 and len(board.calcLegalMoves(1)) == 0):
            # no legal moves available, stalemate
            return True

        else:
            # continue onwards
            return False
            
    def calcScore(self, board):
    #calculates the final score for the board

        score = [0,0]

        # black pieces
        for cell in range(len(board.currPos[0])):
            # black pieces at end of board - 2 pts
            if (board.currPos[0][cell][0] == 0):
                score[0] += 2
            # black pieces not at end - 1 pt
            else:
                score[0] += 1

        # white pieces
        for cell in range(len(board.currPos[1])):
            # white pieces at end of board - 2 pts
            if (board.currPos[1][cell][0] == BOARD_SIZE-1):
                score[1] += 2
            # white pieces not at end - 1 pt
            else:
                score[1] += 1
        return score



    #Artificial Intelligence        
    
    
    def minmax(self, board, player, depth):
       
        if depth == 0:
            return self.evaluation_function(board, player), board
        
        if player:
            robotEval = float('-inf')
            best_move = None
            for move in board.calcLegalMoves(player):
                copy.deepcopy(board).boardMove(move, player)
                evaluation = self.minmax(copy.deepcopy(board), False, depth-1)[0] 
                if evaluation > robotEval:
                    robotEval = evaluation
                    best_move = move 
                return robotEval, best_move
            
        else:
            humanEval = float('-inf')
            best_move = None
            for move in board.calcLegalMoves(player):
                copy.deepcopy(board).boardMove(move, player)
                evaluation = self.minmax(copy.deepcopy(board), True, depth-1)[0]
                if evaluation > humanEval:
                    humanEval = evaluation 
                    best_move = move 
            return humanEval, best_move

        
    # returns a utility value for a non-terminal node
    # f(x) = 5(player piece in end)+3(player not in end)-7(opp in end)-3(opp not in end)
    def evaluation_function(self, board, currPlayer):
        blk_far, blk_home_half, blk_opp_half = 0,0,0
        wt_far, wt_home_half, wt_opp_half = 0,0,0 
        # black's pieces
        for cell in range(len(board.currPos[0])):
            # player pieces at end of board
            if (board.currPos[0][cell][0] == BOARD_SIZE-1):
                blk_far += 1
            # player pieces in opponents end
            # change to "print 'yes' if 0 < x < 0.5 else 'no'"
            elif (BOARD_SIZE/2 <= board.currPos[0][cell][0] < BOARD_SIZE):
                blk_opp_half += 1
            else:
                blk_home_half += 1
        # white's pieces
        for cell in range(len(board.currPos[1])):
            # opp pieces at end of board 
            if (board.currPos[1][cell][0] == 0):
                wt_far += 1
            # opp pieces not at own end
            elif (0 <= board.currPos[1][cell][0] < BOARD_SIZE/2):
                wt_opp_half += 1
            else:
                wt_home_half += 1
        white_score = (7 * wt_far) + (5 * wt_opp_half)+ (3 * wt_home_half)
        black_score = (7 * blk_far) + (5 * blk_opp_half)+ (3 * blk_home_half)
        if (currPlayer == 0):
            return (black_score - white_score)
        else:
            return (white_score - black_score)       
                 
# wrapper for alpha-beta info
# v = [move_value, move, max tree depth, # child nodes, # max/beta cutoff, # min/alpha cutoff]
class AB_Value:
    def __init__(self, move_value, move, max_depth, child_nodes, max_cutoff, min_cutoff):
        self.move_value = move_value
        self.move = move
        self.max_depth = max_depth
        self.nodes = child_nodes
        self.max_cutoff = max_cutoff
        self.min_cutoff = min_cutoff


# wrapper for state used in alpha-beta
class AB_State:
   def __init__(self, boardState, currPlayer, originalPlayer):
      self.board = boardState
      self.player = currPlayer
      self.origPlayer = originalPlayer
      
class Move:
    def __init__(self, start, end, jump=False):
            self.start = start
            self.end = end # tuple (row, col)
            self.jump = jump # bool
            self.jumpOver = [] # array of pieces jumped over
    
class Board:
    def __init__(self, board=[], currBlack=[], currWhite=[]):
        if (board!=[]):
            self.boardState = board     
        else:
            self.setDefaultBoard()
        self.currPos = [[],[]]
        if (currBlack != []):
            self.currPos[0] = currBlack
        else:
            self.currPos[0] = self.calcPos(0)
        if (currWhite != []):
            self.currPos[1] = currWhite
        else:
            self.currPos[1] = self.calcPos(1)
        self.whiteKings = []
        self.blackKings = []
        
          
            
    def boardMove(self, move_info, currPlayer):
        move = [move_info.start, move_info.end]
        #print("Move:", move)
        #self.drawBoardState()
        
        #remove = move_info.jumpOver
        jump = move_info.jump      
        
        # start by making old space empty
        self.boardState[move[0][0]][move[0][1]] = -1
        # then set the new space to player who moved
        self.boardState[move[1][0]][move[1][1]] = currPlayer
        
        if jump:
            #remove jumped over enemies
            for enemy in move_info.jumpOver:
                self.boardState[enemy[0]][enemy[1]] = -1
        
        # update currPos array        
        # if its jump, the board could be in many configs, just recalc it
        if jump:
            self.currPos[0] = self.calcPos(0)
            self.currPos[1] = self.calcPos(1)
        # otherwise change is predictable, so faster to just set it
        else:
            self.currPos[currPlayer].remove((move[0][0], move[0][1]))
            self.currPos[currPlayer].append((move[1][0], move[1][1]))
        
        #self.checkKing(move[1], currPlayer)

        


    def calcLegalMoves(self, player): # int array  -> [0] reg, [1] jump
        #Creates an array containing all legal moves
        
        legalMoves = []
        hasJumps = False
        
        downwards = 1
        upwards = 0
        
        if player:
        #White    
            if (len(self.currPos[player])>0):
                #Regular pieces - Right
                self.legalMovesRIGHT(self.currPos[player], downwards, legalMoves, hasJumps)
            
                #Regular pieces - Left
                self.legalMovesLEFT(self.currPos[player], downwards, legalMoves, hasJumps)
            
            if (len(self.whiteKings)>0): 
                #King pieces - Down Right
                self.legalMovesRIGHT(self.whiteKings, downwards, legalMoves, hasJumps)
            
                #King pieces - Down Left
                self.legalMovesLEFT(self.whiteKings, downwards, legalMoves, hasJumps)
            
                #King pieces - Up Right
                self.legalMovesRIGHT(self.whiteKings, upwards, legalMoves, hasJumps)
            
                #King pieces - Up Left
                self.legalMovesLEFT(self.whiteKings, upwards, legalMoves, hasJumps)
            
            
        else:
        #Black    
            if (len(self.currPos[player])>0):
                #Regular pieces - Right
                self.legalMovesRIGHT(self.currPos[player], upwards, legalMoves, hasJumps)
            
                #Regular pieces - Left
                self.legalMovesLEFT(self.currPos[player], upwards, legalMoves, hasJumps)
            
            if (len(self.blackKings)>0): 
                #King pieces - Down Right
                self.legalMovesRIGHT(self.blackKings, upwards, legalMoves, hasJumps)
            
                #King pieces - Down Left
                self.legalMovesLEFT(self.blackKings, upwards, legalMoves, hasJumps)
            
                #King pieces - Up Right
                self.legalMovesRIGHT(self.blackKings, downwards, legalMoves, hasJumps)
            
                #King pieces - Up Left
                self.legalMovesLEFT(self.blackKings, downwards, legalMoves, hasJumps)
            
            
        return legalMoves

    
    def legalMovesRIGHT(self, pieces, direction, legalMoves, hasJumps):
        
        if direction:
            #Limit is lower bound == White Player
            boardLimit = BOARD_SIZE-1
        else:
            #Limit is upper bound == Black Player
            boardLimit = 0
        
        if direction:
            #Downwards == White Player
            next = 1
        else:
            #Upwards == Black Player
            next = -1
        
        available_pieces = pieces
        
        for cell in available_pieces:
            if (cell[0] == boardLimit):
                continue
            # diagonal right, only search if not at right edge of board
            if (cell[1]!=BOARD_SIZE-1):
                #empty, regular move
                if (self.boardState[cell[0]+next][cell[1]+1]==-1 and not hasJumps):
                    temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]+1)) 
                    legalMoves.append(temp)
                # has enemy, can jump it?
                elif(self.boardState[cell[0]+next][cell[1]+1]==1-direction):
                    jumps = self.checkJump((cell[0],cell[1]), False, direction)
                    if (len(jumps)!=0):
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        legalMoves.extend(jumps)
    
    
    
    def legalMovesLEFT(self, pieces, direction, legalMoves, hasJumps):
        
        if direction:
            #Limit is lower bound == White Player
            boardLimit = BOARD_SIZE-1
        else:
            #Limit is upper bound == Black Player
            boardLimit = 0
        
        if direction:
            #Downwards == White Player
            next = 1
        else:
            #Upwards == Black Player
            next = -1
        
        available_pieces = pieces
        
        for cell in available_pieces:
            if (cell[0] == boardLimit):
                continue
            # diagonal left, only search if not at left edge of board
            if (cell[1]!=0):
                if(self.boardState[cell[0]+next][cell[1]-1]==-1 and not hasJumps):
                    temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]-1)) 
                    legalMoves.append(temp)                    
                elif(self.boardState[cell[0]+next][cell[1]-1]==1-direction):
                    jumps = self.checkJump((cell[0],cell[1]), True, direction)
                    if (len(jumps)!=0):
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []                        
                        legalMoves.extend(jumps)
    
        
    # enemy in the square we plan to jump over
    def checkJump(self, cell, isLeft, player):
        jumps = []
        next = -1 if player == 0 else 1
        
        # check boundaries!
        if (cell[0]+next == 0 or cell[0]+next == BOARD_SIZE-1):
            return jumps
        
        #check top left
        if (isLeft):
            if (cell[1]>1 and self.boardState[cell[0]+next+next][cell[1]-2]==-1):
                temp = Move(cell, (cell[0]+next+next, cell[1]-2), True)
                temp.jumpOver = [(cell[0]+next,cell[1]-1)]
                # can has double jump?
                if (temp.end[0]+next > 0 and temp.end[0]+next < BOARD_SIZE-1):
                    #enemy in top left of new square?
                    if (temp.end[1]>1 and self.boardState[temp.end[0]+next][temp.end[1]-1]==(1-player)):
                        test = self.checkJump(temp.end, True, player)
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                      
                    # top right?
                    if (temp.end[1]<BOARD_SIZE-2 and self.boardState[temp.end[0]+next][temp.end[1]+1]==(1-player)):
                        test = self.checkJump(temp.end, False, player)                  
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                jumps.append(temp)
        else:
        #check top right
            if (cell[1]<BOARD_SIZE-2 and self.boardState[cell[0]+next+next][cell[1]+2]==-1):
                # ([original cell, new cell], enemy cell])
                temp = Move(cell, (cell[0]+next+next, cell[1]+2), True)
                temp.jumpOver = [(cell[0]+next,cell[1]+1)]
                # can has double jump?
                if (temp.end[0]+next > 0 and temp.end[0]+next < BOARD_SIZE-1):
                    #enemy in top left of new square?
                    if (temp.end[1]>1 and self.boardState[temp.end[0]+next][temp.end[1]-1]==(1-player)):
                        test = self.checkJump(temp.end, True, player)
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                    # top right?
                    if (temp.end[1]<BOARD_SIZE-2 and self.boardState[temp.end[0]+next][temp.end[1]+1]==(1-player)):
                        test = self.checkJump(temp.end, False, player) 
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                jumps.append(temp)                
    # uncomment this when its time to try double jumps
     #   print("Jumps:")
     #   for mov in jumps:
     #       print(str(mov.start)+" "+str(mov.end)+" Jump over: "+str(mov.jumpOver))
        return jumps
    
    
    def checkKing(self, cell, player):
       #cell[row,col]
       boardLimit = 0 if player == 0 else BOARD_SIZE-1
       if cell[0] == boardLimit:
           self.currPos[player].remove(cell)
           if player:
               self.whiteKings.append(cell)
               print("White kings: ", self.whiteKings)
           else:
               self.blackKings.append(cell)
               print("Black kings: ", self.blackKings)
       
    
    def calcPos(self, player):
        pos = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (self.boardState[row][col]==player):
                    pos.append((row,col))
        return pos
         
    def drawBoardState(self):
        """
        Draws and updates board to terminal
        """
        #for colnum in range(BOARD_SIZE):
        #    print str(colnum)+" ",#end="")
        x = 0
        print ("")
        print ("------------------------")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (self.boardState[row][col] == -1):
                    print("+  ", end="", flush=True)
                elif (self.boardState[row][col] == 1):
                    print("W  ", end="", flush=True)
                elif (self.boardState[row][col] == 0):
                    print ("B  ", end="", flush=True)
            print (" |"+str(x))
            x += 1
        print ("------------------------")
        print ("0  1  2  3  4  5  6  7")
        
    def setDefaultBoard(self):
        # reset board
        # -1 = empty, 0=black, 1=white
        self.boardState = [
            [-1,1,-1,1,-1,1,-1,1],
            [1,-1,1,-1,1,-1,1,-1],
            [-1,1,-1,1,-1,1,-1,1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [0,-1,0,-1,0,-1,0,-1],
            [-1,0,-1,0,-1,0,-1,0],
            [0,-1,0,-1,0,-1,0,-1]
        ]
         


## Robot move functions
def robot_move(move):
    global playr
    print ("Player moving = ", playr)
    print ("Robot moving")

    # Translate to robot placenames
    start = "ABCDEFGH"[move.start[1]] + "76543210"[move.start[0]]
    end = "ABCDEFGH"[move.end[1]] + "76543210"[move.end[0]]
    print ([start, end])
    # Send to robot
    bxd.move_piece(start, end)
    if move.jump==True:
        for piece in move.jumpOver:
            takePiece = "ABCDEFGH"[piece[1]] + "76543210"[piece[0]]
            print ("Taking pieces", takePiece)
            bxd.take_piece(takePiece)
    bxd.move_home()
    return


## Callbacks for BaxUI
def setPlayer(selected=0):
    global playr
    print ("set player" , selected)
    #baxterDo.BaxUI.runit=False
    playr = selected

def calibrate_board (selected=0):
    # Dumps the parameter returned by the callback
    # Calls the baxter calibrate routine
    bxd.calibrate_board()
    

playr=0
def main():
    global playr

    bxd.init() # Initialise ROS node - only needs to be done once!
    print ("reset")
    bxd.move_home()
    playr=0

    print ("You are Player", playr)
    print ()
    #while not (playr == 0 or playr == 1):
    #    playr = int(input("Invalid Choice, please try again: "))
    game = Game(playr)
    game.run()
    
main()
