#!/usr/bin/python
"""
Originally by Jason Schapiro 2012
Modified by M L Walters, 2014
Modified by D A Nobrega, 2021


Basic Functionality:

Program runs with no errors under Python 3 - 5pts
-Print functions were fixed as well other minor Python3 corrections

Appropriate data structure(s) for updating board and player positions - 5pts
-State and Move class were used to update board
-Arrays were used to store this information

MinMax algorithm implemented correctly - 5pts
-New MinMax algorithm was implemented. It currently is set to have a max depth
of 3 but can be changed to a higher depth in the global variables section.
-This function calculates the best outcome the robot will have, in 3 moves time,
by moving each piece.
-Taking into consideration that the robot will assume the human will make the 
best possible move in its turn as well.

Robot actions + user input implemented via baxterDo API functions - 5pts
-Robot makes its own moves, kings its own pieces and removes the needed pieces
-User functionality was not needed for this version as it is not being test in the lab

Total: 20pts


Advanced Functionality:

Kinging implemented and evaluated - 5pts
-Kinging was implemented. When reaching the limit of the board the piece will become a king.
-Afterwards it will be able to move upwards or downwards in the board.
-Kinging was added to the evaluation algorithm. Number of kings will make a difference
when the robot is finding its best move.

MinMax search algorithm optimisation(s) implemented - 5pts
-MinMax algorithm was fully optimised to determine the best move.
-None of the previous code was used, thus, not optimised.
-MinMax algorithm takes into consideration the amount of jumps available. Bigger the amount of jumps,
better it is.

Evaluation function improvements - 5pts
-Evaluation function was changed. Now it takes into consideration the number of pieces,
its positions and the number of kings.

Other useful improvements to Game AI engine or program - 5pts
-Code was improved as much as possible to be simpler. 
-Functions were broken down into different functions to enable future coders to better
understand each part of the functionalities available.

Total: 20pts

Code readability, comments and program structure - 10pts 
-Code is fully commented and structured in different sections to divide functionalities


Program was ran against an AI checkers game and won.
https://www.247checkers.com/


In case there's any error in delivered version please check:
https://github.com/DiogoSilvaa/AI-Checkers

STUDENT ID: 17071828
STUDENT NAME: Diogo ALexandre Da Silva Nobrega
Individual work

For use with BAxter Robot Draughts Game
"""




# Load Baxter Robot actions
import baxterDo_Dummy as bxd
import copy

#Global variables
BOARD_SIZE = 8
NUM_PLAYERS = 12
depth = 3
# the players array extends to many other arrays in the program
# in these arrays, 0 will refer to black and 1 to white
PLAYERS = ["Black", "White"]
board = [ [[0.0, 0.0]]*8 ] *8 # 2D array, translates game positions for robot
playr = 0 # Human player, default = 0 = Black 

#Game
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
            move = self.getMove(legal) #Get human to input its choice
            print("Human chooses:", move.start)
            self.makeMove(move) #Human moves the piece
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
                state = State(self.board, self.turn, self.turn)
                move = self.minmax(copy.deepcopy(state.board), True, 3)[1]
                #Board is deep copied to maintain the state of the current board while
                #AI finds the best move by simulating plays                 
                
            king = self.makeMove(move) #Make the move according to AI's choice
            print("Computer chooses ("+str(move.start)+", "+str(move.end)+")")
            robot_move(move) # Robot moving routine
 
            if king:
                #Translate coordinates to robot coordinates
                end = "ABCDEFGH"[move.end[1]] + "76543210"[move.end[0]]
                #Robot 'kings' its own piece
                bxd.king_piece(end)
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
        #Function to perform the chosen move
        
        king = self.board.boardMove(move, self.turn) # Update board according to move chosen
        
        if move.jump:
            #If a jump was made over an enemy's piece
            self.remaining[1-self.turn] -= len(move.jumpOver) #Deduct a piece from the enemy
            print("Removed "+str(len(move.jumpOver))+" "+PLAYERS[1-self.turn]+" pieces")
        
        return king
            
        
        
    def getMove(self, legal):
        #Function to capture the input of the user (chosen move)
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

        if (len(board.currPos[0])== 0) or (len(board.currPos[1]) == 0):
            # all pieces from one side captured
            return True

        elif (len(board.calcLegalMoves(0)) == 0 and len(board.calcLegalMoves(1)) == 0):
            # no legal moves available
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
    #Function to help determine the best move for the robot to perform   
        
        #Debug:
        #board.drawBoardState()
        
        if depth == 0 or self.gameOver(board):
            #In case a move reaches the maximum depth or the move finishes the game
            #Returns the board score for the move
            return self.evaluation_function(board, player), board
        
        if player:
            #If it is the robot's turn:
            robotEval = float('-inf')
            best_move = None
            #For loop iterates through all legal moves for the current board position
            for move in board.calcLegalMoves(player):
                #Board is deep copied to maintain its state
                simBoard = copy.deepcopy(board)
                #Move are performed in the copied board
                simBoard.boardMove(move, player)
                #Recursion is performed in each move until it reaches max depth
                evaluation = self.minmax(simBoard, False, depth-1)[0] 
                if evaluation > robotEval:
                #Best scored move is kept as the final move 
                    robotEval = evaluation
                    best_move = move 
            return robotEval, best_move
            
        else:
            #If it is the robot's turn:
            humanEval = float('-inf')
            best_move = None
            for move in board.calcLegalMoves(player):
                simBoard = copy.deepcopy(board)
                simBoard.boardMove(move, player)
                evaluation = self.minmax(simBoard, True, depth-1)[0]
                if evaluation > humanEval:
                    humanEval = evaluation 
                    best_move = move 
            return humanEval, best_move


    def evaluation_function(self, board, currPlayer):
    #Function evaluates the board state and returns a score
    #Different weights are given to number of pieces, kings and their positioning
        black_kings, black_home_half, black_opp_half = 0,0,0
        white_kings, white_home_half, white_opp_half = 0,0,0 
        blackAttacks, whiteAttacks = 0,0
        
        #If black pieces have jumps available to make:
        if (board.legalMoves(board.currPos[0], board.Kings[0], 0)[1]):
            #Store amount of jumps in black attacks
            blackAttacks = len(board.legalMoves(board.currPos[0], board.Kings[0], 1)[0])
        
        #If white pieces have jumps available to make:    
        if (board.legalMoves(board.currPos[1], board.Kings[1], 1)[1]):
            #Store amount of jumps in white attacks
            whiteAttacks = len(board.legalMoves(board.currPos[1], board.Kings[1], 1)[0])    
                         
        # Black pieces
        for cell in range(len(board.currPos[0])):  
            #Increments number of kings owned by black player
            if cell in board.Kings[0]:
                black_kings += 1    
            #Increments number of black pieces in own half 
            elif (0 <= board.currPos[0][cell][0] < BOARD_SIZE/2):
                black_home_half += 1
            #Increments number of black pieces in opponent half
            elif (BOARD_SIZE/2 <= board.currPos[0][cell][0] <= BOARD_SIZE - 1):
                black_opp_half += 1
            
        # White pieces
        for cell in range(len(board.currPos[1])):            
            #Increments number of kings owned by white player
            if cell in board.Kings[1]:
                white_kings += 1    
            #Increments number of white pieces in own half 
            elif (BOARD_SIZE - 1 <= board.currPos[1][cell][0] < BOARD_SIZE/2):
                white_home_half += 1
            #Increments number of white pieces in opponent half
            elif (BOARD_SIZE/2 <= board.currPos[1][cell][0] <= 0):
                white_opp_half += 1

        #Calculate final score 
        # Score = (7* Own pieces on opponent end) + (5* Own pieces in own end) + (9*Own king pieces)
        white_score = (1.25 * white_opp_half) + (1 * white_home_half)+ (2 * white_kings) + (3 * whiteAttacks)
        black_score = (1.25 * white_opp_half) + (1 * black_home_half)+ (2 * black_kings) + (3 * blackAttacks)
        
        #Returns the player's respective score
        if (currPlayer == 0):
            return (black_score - white_score)
        else:
            return (white_score - black_score)                        

#Class set to carry board state, current player and original player information
class State:
   def __init__(self, boardState, currPlayer, originalPlayer):
      self.board = boardState
      self.player = currPlayer
      self.origPlayer = originalPlayer

#Class set to carry move information      
class Move:
    def __init__(self, start, end, jump=False):
            self.start = start # tuple (row, col)
            self.end = end # tuple (row, col)
            self.jump = jump # bool
            self.jumpOver = [] # array of pieces jumped over
 
#Class set to carry board information    
class Board:
    def __init__(self, board=[], currBlack=[], currWhite=[], kingBlack=[], kingWhite=[]):
        if (board!=[]):
            self.boardState = board     
        else:
            self.setDefaultBoard()
        self.currPos = [[],[]]  #Array to hold black's pieces [0] and white's [1]
        if (currBlack != []): 
            self.currPos[0] = currBlack
        else:
            self.currPos[0] = self.calcPos(0)
        if (currWhite != []):
            self.currPos[1] = currWhite
        else:
            self.currPos[1] = self.calcPos(1)
        self.Kings = [[],[]] #Array to hold black's kings [0] and white's [1]
        if (kingBlack != 0):
            self.Kings[0] = kingBlack 
        if (kingWhite != 0):
            self.Kings[1] = kingWhite
                      
    def boardMove(self, move_info, currPlayer):
        move = [move_info.start, move_info.end]
        
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
                             
        #Update kings according to the move performed       
        king = self.checkKing(move, currPlayer)
        
        return king 
        


    def calcLegalMoves(self, player): 
        #Creates an array containing all legal moves and returns it
        
        legalMoves = []
        
        #Moves direction (Down the board = 1) (Up the board = 0)
        downwards = 1
        upwards = 0
        
        if player:
        #White    
            if (len(self.currPos[player])>0):
                #Calculates legal moves if there's pieces left in player's possession
                legalMoves = self.legalMoves(self.currPos[player], self.Kings[player], downwards)[0]                    
                
        else:
        #Black    
            if (len(self.currPos[player])>0):
                #Calculates legal moves if there's pieces left in player's possession
                legalMoves = self.legalMoves(self.currPos[player], self.Kings[player], upwards)[0]
                
            
        return legalMoves

    
    def legalMoves(self, pieces, kings, direction):
    #Function determines the legal moves and returns it in an array
    
        legalMoves = []
        
        hasJumps = False

        #If direction being calculated is downwards
        if direction:
            boardLimit = BOARD_SIZE -1 
            next = 1
            enemy = 1
        #If direction being calculated is upwards
        else:
            boardLimit = 0
            next = -1
            enemy = 0 
        
        # cell refers to a position tuple (row, col)
        for cell in pieces:
            #If cell is in the board limit, cell is skipped
            if (cell[0] == boardLimit): 
                continue
            # diagonal right, only search if not at right edge of board
            if (cell[1]!=BOARD_SIZE-1):
                #empty, regular move
                if (self.boardState[cell[0]+next][cell[1]+1]==-1 and not hasJumps):
                    #If cell on top right is empty and a jump hasn't been recorded:
                    temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]+1)) 
                    #Move is legal and is added to the 'legalMoves' array
                    legalMoves.append(temp)
                #cell on top right has an enemy, can the piece jump it?
                elif(self.boardState[cell[0]+next][cell[1]+1]==1-enemy):
                    #Function check.jump is called to verify if the jump is possible
                    jumps = self.checkJump((cell[0],cell[1]), False, direction, enemy) 
                    if (len(jumps)!=0):
                    #If there is legal jumps:    
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        #Jumps' array items are added to the legalMoves array    
                        legalMoves.extend(jumps)
            # diagonal left, only search if not at left edge of board
            if (cell[1]!=0):
                if(self.boardState[cell[0]+next][cell[1]-1]==-1 and not hasJumps):
                    #If cell on top left is empty and a jump hasn't been recorded:
                    temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]-1)) 
                    legalMoves.append(temp)                    
                #cell on top left has an enemy, can the piece jump it?
                elif(self.boardState[cell[0]+next][cell[1]-1]==1-enemy):
                    #Function check.jump is called to verify if the jump is possible
                    jumps = self.checkJump((cell[0],cell[1]), True, direction, enemy)
                    if (len(jumps)!=0):
                    #If there is legal jumps:    
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []                        
                        legalMoves.extend(jumps)
            
       
            
            #Kings' legal moves: 
        
        #If direction was set downards previously, it is changed upwards
        #All the parameters influenced by the direction are changed accordingly        
        if direction == 1:
            direction = 0
            boardLimit = 0
            next = -1
        else: 
            direction = 1
            boardLimit = BOARD_SIZE-1
            next = 1
                
        for cell in pieces:
            if cell in kings:  
            #If cell is in the board limit, cell is skipped                
                if (cell[0] == boardLimit):
                    continue
                # diagonal right, only search if not at right edge of board
                if (cell[1]!=BOARD_SIZE-1):
                    #empty, regular move
                    if (self.boardState[cell[0]+next][cell[1]+1]==-1 and not hasJumps):
                    #If cell on top right is empty and a jump hasn't been recorded:                        
                        temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]+1)) 
                        #Move is legal and is added to the 'legalMoves' array                        
                        legalMoves.append(temp)
                    #cell on top right has an enemy, can the piece jump it?
                    elif(self.boardState[cell[0]+next][cell[1]+1]==1-enemy):
                        #Function check.jump is called to verify if the jump is possible                        
                        jumps = self.checkJump((cell[0],cell[1]), False, direction, enemy)
                        if (len(jumps)!=0):
                        #If there is legal jumps:    
                            # if first jump, clear out regular moves
                            if not hasJumps:
                                hasJumps = True
                                legalMoves = []
                            #Jumps' array items are added to the legalMoves array                                    
                            legalMoves.extend(jumps)
                # diagonal left, only search if not at left edge of board
                if (cell[1]!=0):
                    if(self.boardState[cell[0]+next][cell[1]-1]==-1 and not hasJumps):
                        #If cell on top left is empty and a jump hasn't been recorded:                        
                        temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]-1)) 
                        legalMoves.append(temp) 
                    #cell on top left has an enemy, can the piece jump it?                        
                    elif(self.boardState[cell[0]+next][cell[1]-1]==1-enemy):
                        #Function check.jump is called to verify if the jump is possible                        
                        jumps = self.checkJump((cell[0],cell[1]), True, direction, enemy)
                        if (len(jumps)!=0):
                        #If there is legal jumps:    
                            # if first jump, clear out regular moves                            
                            if not hasJumps:
                                hasJumps = True
                                legalMoves = []                        
                            legalMoves.extend(jumps)
        
        return legalMoves, hasJumps
    
        
    
    
    
    def checkJump(self, cell, isLeft, direction, enemy):
    #Function determines the jumps legal to be made by a piece and returns it
    #in an array
    
        jumps = []
        next = -1 if direction == 0 else 1
        
        # checks cell boundaries to confirm a jump would leave the piece inside the board
        if (cell[0]+next == 0 or cell[0]+next == BOARD_SIZE-1):
            return jumps
        
        #If enemy is on the left 
        if (isLeft):
            #If cell has atleast another cell to the left and the cell after the jump is empty:
            if (cell[1]>1 and self.boardState[cell[0]+next+next][cell[1]-2]==-1):
                temp = Move(cell, (cell[0]+next+next, cell[1]-2), True)
                temp.jumpOver = [(cell[0]+next,cell[1]-1)]
                # Can the piece make another jump from its new position?
                if (temp.end[0]+next > 0 and temp.end[0]+next < BOARD_SIZE-1):
                    #Checks if enemy is on top left
                    if (temp.end[1]>1 and self.boardState[temp.end[0]+next][temp.end[1]-1]==(1-enemy)):
                        test = self.checkJump(temp.end, True, direction, enemy)
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            #Legal double jumps are appended to the jumps array
                            jumps.append(dbl_temp)                      
                    #Checks if enemy is on top right
                    if (temp.end[1]<BOARD_SIZE-2 and self.boardState[temp.end[0]+next][temp.end[1]+1]==(1-enemy)):
                        test = self.checkJump(temp.end, False, direction, enemy)                  
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            #Legal double jumps are appended to the jumps array
                            jumps.append(dbl_temp)                              
                #Legal jumps found are appended to the jumps array 
                jumps.append(temp)
        else:
        #enemy is on the right 
            if (cell[1]<BOARD_SIZE-2 and self.boardState[cell[0]+next+next][cell[1]+2]==-1):
                # ([original cell, new cell], enemy cell])
                temp = Move(cell, (cell[0]+next+next, cell[1]+2), True)
                temp.jumpOver = [(cell[0]+next,cell[1]+1)]
                # Can the piece make another jump from its new position?
                if (temp.end[0]+next > 0 and temp.end[0]+next < BOARD_SIZE-1):
                    #Checks if enemy is on top left
                    if (temp.end[1]>1 and self.boardState[temp.end[0]+next][temp.end[1]-1]==(1-enemy)):
                        test = self.checkJump(temp.end, True, direction, enemy)
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            #Legal double jumps are appended to the jumps array
                            jumps.append(dbl_temp)                              
                    #Checks if enemy is on top right
                    if (temp.end[1]<BOARD_SIZE-2 and self.boardState[temp.end[0]+next][temp.end[1]+1]==(1-enemy)):
                        test = self.checkJump(temp.end, False, direction, enemy) 
                        if (test != []):
                            dbl_temp = copy.deepcopy(temp)
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            #Legal double jumps are appended to the jumps array
                            jumps.append(dbl_temp)                              
                #Legal jumps found are appended to the jumps array 
                jumps.append(temp)
    
        return jumps                          
    
    
    def checkKing(self, move, player):
    #Function sets and carries king status of pieces   
       #cell[row,col]
       
       #Determines player's board limit
       boardLimit = 0 if player == 0 else BOARD_SIZE-1       
       
       #If the performed move will move the piece into the board limit:
       if move[1][0] == boardLimit:
           #Piece becomes a king, and is appended to Kings[player] array
           self.Kings[player].append(move[1])
           if player:
               return True
       #If the piece present in the move is a king already, king status is given to the piece
       #In the new location
       elif move[0] in self.Kings[player]:
           #Older king's position is removed from the array
           self.Kings[player].remove(move[0])
           #Newer King's position is appended to the array
           self.Kings[player].append(move[1])
           return False
       return False
    
   
    def calcPos(self, player):
    #Function scans through the board and returns all the pieces belonging to the player
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
    

def main():
    global playr

    bxd.init() # Initialise ROS node - only needs to be done once!
    print ("reset")
    bxd.move_home()
    playr=0

    print ("You are Player", playr)
    
    game = Game(playr)
    game.run()
    
main()
