class WebInterface:
    def __init__(self,game):
        self.inputlabel = None
        self.btnlabel = None
        self.errmsg = None
        self.board = None
        self.game = game
        self.page = None
        self.showerrmsg = 'display:block'
        self.showinput = 'display:block'
        self.showend = 'display:none'
        self.showundo = 'display:none'
        self.endmsg = None
    
    def update(self,page = None):
        if page != None:
            self.page = page

        self.showinput = 'display:block'
        self.showend = 'display:none'
        if self.game.canundo():
            self.showundo = 'display:block'
        else:
            self.showundo = 'display:none'

        self.board = self.game.display()
        self.update_err()

        if self.page == '/play':
            self.inputlabel = f'{self.game.turn} player: '
            self.btnlabel = 'Move'
            
        elif self.page == '/promote':
            self.inputlabel = 'promote pawns to:'
            self.btnlabel = 'PROMOTE'

        elif self.page == '/end':
            self.showinput = 'display:none'
            self.showend = 'display:block'
            self.showundo = 'display:none'
            self.endmsg = f'Game Over. The winner is {self.game.winner}'
        


    def update_err(self,errmsg = None):
        self.errmsg = errmsg
        if self.errmsg == None:
            self.showerrmsg = 'display:none'
        else:
            self.showerrmsg = 'display:block'

class MoveHistory:
    '''MoveHistory works like a CircularStack'''
    def __init__(self, size):
        # Remember to validate input
        self.size = size
        self.__data = [None] * size
        self.head = 0

    def __str__(self):
        output = []
        for i in range(self.head,0,-1):
            output.append(self.__data[i])
        return str(output)
    
    def push(self, move):
        self.head = (self.head + 1) % self.size
        self.__data[self.head] = move
            
    def pop(self):
        # Remember to check if MoveHistory is empty
        move = self.__data[self.head]
        self.__data[self.head] = None
        if self.head == 0:
            self.head = self.size - 1
        else:
            self.head -= 1
        return move


class Move:
    def __init__(self,game,start,end):
        self.start=start
        self.end=end
        self.startpiece = game.get_piece(start)
        self.endpiece = game.get_piece(end)
    def __repr__(self):
        return f'Start:{self.start},{self.startpiece}  End:{self.end},{self.endpiece}'


class MoveError(Exception):
    '''Custom error for invalid moves.'''
    pass


class BasePiece:
    def __init__(self,colour):
        if type(colour) != str:
            raise TypeError('colour argument must be str')
        elif colour.lower() not in {'white','black'}:
            raise ValueError('colour must be {white,black}')
        else:
            self.colour = colour

    def __repr__(self):
        return f'BasePiece({repr(self.colour)})'
    
    def __str__(self):
        try:
            return f'{self.colour} {self.name}'
        except NameError:
            return f'{self.colour} piece'

    @staticmethod
    def vector(start, end):
        x = end[0] - start[0]
        y = end[1] - start[1]
        dist = abs(x) + abs(y)
        return x, y, dist


class King(BasePiece):
    name = 'king'
    symbol = {'white': '♔', 'black': '♚'}
    def __repr__(self):
        return f'King({repr(self.colour)})'
    
    def isvalid(self, start: tuple, end: tuple):
        '''King can move 1 step horizontally or vertically.'''
        x, y, dist = self.vector(start, end)
        return dist == 1


class Queen(BasePiece):
    name = 'queen'
    symbol = {'white': '♕', 'black': '♛'}
    def __repr__(self):
        return f'Queen({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if (x != 0 and y != 0 and abs(x) == abs(y)) \
                or (x == 0 and y != 0) \
                or (y == 0 and x != 0):
            return True
        else:
            return False


class Bishop(BasePiece):
    name = 'bishop'
    symbol = {'white': '♗', 'black': '♝'}
    def __repr__(self):
        return f'Bishop({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if x != 0 and y != 0 and abs(x) == abs(y):
            return True
        else:
            return False


class Knight(BasePiece):
    name = 'knight'
    symbol = {'white': '♘', 'black': '♞'}
    def __repr__(self):
        return f'Knight({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if dist == 3 and 0 < abs(x) < 3 and 0 < abs(y) < 3:
            return True
        else:
            return False


class Rook(BasePiece):
    name = 'rook'
    symbol = {'white': '♖', 'black': '♜'}
    def __repr__(self):
        return f'Rook({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        if kwargs.get('castling', False):
            if self.colour == 'white':
                row = 0
            elif self.colour == 'black':
                row = 7
            if start[1] != end[1] != row:
                return False
            elif not((start[0] == 0 and end[0] == 3)
                   or (start[0] == 7 and end[0] == 5)):
                return False
            else:
                return True
        else:
            if (x == 0 and y != 0) or (y == 0 and x != 0):
                return True
            else:
                return False


class Pawn(BasePiece):
    name = 'pawn'
    symbol = {'white': '♙', 'black': '♟︎'}
    def __repr__(self):
        return f'Pawn({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        xmove = 1 if kwargs.get('capture', False) else 0
        if x == xmove:
            if self.colour == 'black' and y == -1 \
                    or self.colour == 'white' and y == 1:
                return True
        return False


class Board:
    '''
    ATTRIBUTES

    turn <{'white', 'black'}>
        The current player's colour.
    
    winner <{'white', 'black', None}>
        The winner (if game has ended).
        If game has not ended, returns None

    checkmate <{'white', 'black', None}>
        Whether any player is checkmated.

    METHODS
    
    start()
        Start a game. White goes first.

    display()
        Print the game board.

    prompt(colour)
        Prompt the player for input.

    next_turn()
        Go on to the next player's turn.

    isvalid(start, end)
        Checks if the move (start -> end) is valid for this turn.

    update(start, end)
        Carries out the move (start -> end) and updates the board.
    '''
    
    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        self.promotiontest = kwargs.get('promotiontest', False)
        self.endtest = kwargs.get('endtest', False)
    
    def coords(self):
        return list(self._position.keys())

    def pieces(self):
        return list(self._position.values())

    def add(self, coord: tuple, piece):
        self._position[coord] = piece

    def move(self, start, end):
        piece = self.get_piece(start)
        self.remove(start)
        self.add(end, piece)
        self.get_piece(end).notmoved = False

    def remove(self, pos):
        piece = self.get_piece(pos)
        if piece != None:
            del self._position[pos]

    def castle(self, start, end):
        '''Carry out castling move (assuming move is validated)'''
        self.move(start, end)
        # Move the king
        row = start[1]
        if start[0] == 0:
            self.move((4, row), (2, row))
        elif start[0] == 7:
            self.move((4, row), (6, row))

    def get_piece(self, coord):
        '''
        Retrieves the piece at `coord`.
        `coord` is assumed to be a 2-ple of ints representing
        (col,row).

        Return:
        BasePiece instance
        or None if no piece found
        '''
        return self._position.get(coord, None)

    def alive(self, colour, name):
        for piece in self.pieces():
            if piece.colour == colour and piece.name == name:
                return True
        return False
    
    def checkpromotion(self):
        for coord in self.coords():
            row = coord[1]
            piece = self.get_piece(coord)
            for opprow, colour in zip([0, 7], ['black', 'white']):
                if row == opprow and piece.name == 'pawn' \
                        and piece.colour == colour:
                    self.coord_for_promotion = coord
                    self.promotioncolour = piece.colour
                    return True
        self.coord_for_promotion = None
        self.promotioncolour = None
        return False
                    
    def promotion(self,choice,PieceClass=None):             
        if PieceClass is None:
            PieceClass = self.promoteprompt(choice)
        promoted_piece = PieceClass(self.promotioncolour)
        self.remove(self.coord_for_promotion)
        self.add(self.coord_for_promotion, promoted_piece)

    def king_and_rook_unmoved(self, colour, rook_coord):
        row = rook_coord[1]
        king = self.get_piece((4, row))
        rook = self.get_piece(rook_coord)
        return king.notmoved and rook.notmoved

    def no_pieces_between_king_and_rook(self, colour, rook_coord):
        row = rook_coord[1]
        rook_col = rook_coord[0]
        if rook_col == 0:
            columns = (1, 2, 3)
        elif rook_col == 7:
            columns = (5, 6)
        else:
            raise MoveError('Invalid move: castling from {rook_coord}')
        for col in columns:
            if self.get_piece((col, row)) is not None:
                return False
        return True

    def movetype(self, start, end):
        '''
        Determines the type of board move by:
        1. Checking if the player is moving a piece of their
           own colour
        2. Checking if the piece at `start` and the piece at
           `end` are the same colour
        3. Checking if the move is valid for that piece type

        Returns:
        'move' for normal moves
        'capture' for captures
        'castling' for rook castling
        None for invalid moves
        '''
        if self.debug:
            print(f'== movetype({start}, {end}) ==')
        if start is None or end is None:
            return None
        start_piece = self.get_piece(start)
        end_piece = self.get_piece(end)
        if self.debug:
            print(f'START_PIECE: {start_piece}')
            print(f'END_PIECE: {end_piece}')
        if start_piece is None \
                or start_piece.colour != self.turn:
            return None
        if end_piece is not None:
            if end_piece.colour != start_piece.colour:
                return 'capture'
            # handle special cases
            elif start_piece.name == 'pawn' \
                    and end_piece.colour != start_piece.colour \
                    and start_piece.isvalid(start, end, capture=True):
                return 'capture'
            else:
                return None
        else:  # end piece is None
            if start_piece.name == 'rook' \
                    and start_piece.isvalid(start, end, castling=True) \
                    and self.king_and_rook_unmoved(self.turn, start) \
                    and self.no_pieces_between_king_and_rook(self.turn, start):
                return 'castling'
            elif start_piece.isvalid(start, end):
                return 'move'
            else:
                return None
        return True


    def promoteprompt(self,choice):
        if choice == 'r':
            return Rook
        elif choice == 'k':
            return Knight
        elif choice == 'b':
            return Bishop
        elif choice == 'q':
            return Queen

    def printmove(self, start, end, **kwargs):
        startstr = f'{start[0]}{start[1]}'
        endstr = f'{end[0]}{end[1]}'
        print(f'{self.get_piece(start)} {startstr} -> {endstr}', end='')
        if kwargs.get('capture', False):
            print(f' captures {self.get_piece(end)}')
        elif kwargs.get('castling', False):
            print(f' (castling)')
        else:
            print('')

    def start(self):
        self._position = {}

        colour = 'black'
        self.add((0, 7), Rook(colour))
        self.add((1, 7), Knight(colour))
        self.add((2, 7), Bishop(colour))
        self.add((3, 7), Queen(colour))
        self.add((4, 7), King(colour))
        self.add((5, 7), Bishop(colour))
        self.add((6, 7), Knight(colour))
        self.add((7, 7), Rook(colour))
        for x in range(0, 8):
            self.add((x, 6), Pawn(colour))

        colour = 'white'
        self.add((0, 0), Rook(colour))
        self.add((1, 0), Knight(colour))
        self.add((2, 0), Bishop(colour))
        self.add((3, 0), Queen(colour))
        self.add((4, 0), King(colour))
        self.add((5, 0), Bishop(colour))
        self.add((6, 0), Knight(colour))
        self.add((7, 0), Rook(colour))
        for x in range(0, 8):
            self.add((x, 1), Pawn(colour))

        if self.promotiontest:
            self.remove((0,7))
            self.remove((0,6))
            self.add((0, 6), Pawn('white'))

        if self.endtest:
            self.remove((5,6))
            self.add((7, 4), Queen('white'))

        self.turn = 'white'

        for piece in self.pieces():
            piece.notmoved = True
        
        self.history = MoveHistory(100)
        self.winner = None
        self.checkmate = None
        self.coord_for_promotion = None
        self.promotioncolour = None

    def display(self):
        '''
        Displays the contents of the board.
        Each piece is represented by two letters.
        First letter is the colour (W for white, B for black).
        Second letter is the name (Starting letter for each piece).
        '''
        if self.debug:
            print('== DEBUG MODE ON ==')
        # helper function to generate symbols for piece
        def sym(piece):
            return piece.symbol[piece.colour]

        # Row 7 is at the top, so print in reverse order
        row_ =[]
        row_.append(' ' * 4)
        for x in range(8):
            row_.append(x)
            row_.append('  ')
        whole = [row_]
        for row in range(7, -1, -1):
            row_l = []
            row_l.append((f'{row:2}  '))
            for col in range(8):
                coord = (col, row)  # tuple
                if coord in self.coords():
                    piece = self.get_piece(coord)
                    row_l.append(f'{sym(piece)}')
                else:
                    piece = None
                    row_l.append('  ')
                if col == 7:     # Put line break at the end
                    row_l.append('')
                else:            # Print two spaces between pieces
                    row_l.append('  ')

            whole.append(row_l)
            if self.checkmate is not None:
                print(f'{self.checkmate} is checkmated!')
        return whole


    def valid_format(self,inputstr):
        return len(inputstr) == 5 and inputstr[2] == ' ' \
            and inputstr[0:1].isdigit() \
            and inputstr[3:4].isdigit()

    def valid_num(self,inputstr):
        for char in (inputstr[0:1] + inputstr[3:4]):
            if char not in '01234567':
                return False
        return True

    def split_and_convert(self,inputstr):
        '''Convert 5-char inputstr into start and end tuples.'''
        start, end = inputstr.split(' ')
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))            
        return (start, end)



    def update(self, start, end):
        '''
        Update board according to requested move.
        If an opponent piece is at end, capture it.
        '''
        move = Move(self,start,end)
        self.history.push(move)

        movetype = self.movetype(start, end)
        
        if movetype == 'castling':
            self.castle(start, end)
        elif movetype == 'capture':
            self.remove(end)
            self.move(start, end)
        elif movetype == 'move':
            self.move(start, end)
        else:
            raise MoveError('Unknown error, please report '
                             f'(movetype={repr(movetype)}).')
        if not self.alive('white', 'king'):
            self.winner = 'black'
        elif not self.alive('black', 'king'):
            self.winner = 'white'


    def undo(self):
        move = self.history.pop()
        if move == None:
            return
        else:
            self.remove(move.start)
            self.remove(move.end)
            self.add(move.start,move.startpiece)
            if move.endpiece != None:
                self.add(move.end,move.endpiece)
            self.next_turn()

    def canundo(self):
        move = self.history.pop()
        if move == None:
            return False
        else:
            self.history.push(move)
            return True


    def next_turn(self):
        if self.debug:
            print('== NEXT TURN ==')
        if self.turn == 'white':
            self.turn = 'black'
        elif self.turn == 'black':
            self.turn = 'white'
