import copy

# Enum with textual representation
class Color:
  RED = 'r'
  BLACK = 'b'

  @classmethod
  def other(c, s):
    if s == Color.RED:
      return Color.BLACK
    else:
      return Color.RED

# A checker piece. Transparently represented as
# r,b for red,black pieces and R,B for red,black kings
class CheckerPiece:
  def __init__(self, color, king=False):
    self.color = color
    self.king = king
  
  def __repr__(self):
    s = self.color
    if self.king:
      return s.upper()
    return s

  @classmethod
  def fromstring(c, s):
    if(s == Color.RED or s == Color.BLACK):
      return c(s)
    elif(s.lower() == Color.RED or s == Color.BLACK):
      return c(s.lower(), True)
    raise Exception('String does not represent checker piece')

  # What is forwards for this color piece
  def forwards(self):
    if self.color == Color.BLACK:
      return 1
    else:
      return -1

  # Since a CheckerPiece doesn't know it's position, it relies on the 
  # CheckerBoard to add the move_directions to the current position to
  # get the new position. This means this can't actually check if this
  # goes off the board. Note for simplicity black is always starting at
  # the top going down
  def move_directions(self):
    f = self.forwards()
    yield (f, -1)
    yield (f, 1)
    if self.king:
      yield (-f, -1)
      yield (-f, 1)
  
  # doubles all move lengths of move_directions to get jump_directions of
  # the piece
  def jump_directions(self):
    return (tuple(2*x for x in tup) for tup in self.move_directions())

# A checker board. Represented internally as a map of positions to pieces
# (0,0) represents top-left. Is (r,c) so (size-1,0) is bottom-left. Can only instantiate
# starting board and then mutate it from there. For simplicy, always puts black at
# the top.
class CheckerBoard:
  def __init__(self, size, startingrows):
    self.size = size
    self.pieces = {}
    # Place black pieces
    for r in range(0, startingrows):
      for c in range(0, size//2):
        self.pieces[(r, c*2 + (1-r%2))] = CheckerPiece(Color.BLACK)
    # Place red pieces
    for r in range(size-startingrows,size):
      for c in range(0, size//2):
        self.pieces[(r, c*2 + (1-r%2))] = CheckerPiece(Color.RED)
  
  def __repr__(self):
    rows = [[' ' for i in range(0, self.size)] for j in range(0, self.size)]
    for k,v in self.pieces.items():
      (r,c) = k
      rows[r][c] = str(v)
    for r in range(0,self.size):
      letter = str(self.size - r).rjust(2)
      rows[r] = letter + '|' + ''.join(rows[r]) + '|'
    oneline = '\n'.join(rows)
    horizontal = '  +' + ('-' * self.size) + '+'
    oneline = horizontal + '\n' + oneline + '\n' + horizontal
    top = '   ' + ''.join(chr(i+ord('a')) for i in range(0,self.size))
    return top + '\n' + oneline

  # Returns true if the move is in a jump direction. Does not check to see if
  # there is actually a piece there to jump or if it lands off the board
  def is_move_jump(self, src, dest):
    (sr,sc) = src
    (dr,dc) = dest
    p = self.pieces[src]
    return (dr-sr,dc-sc) in p.jump_directions()

  # Returns true if the player controlling color pieces has a jump available to her.
  def can_jump(self, color):
    for pos,piece in self.pieces.items():
      if piece.color == color:
        (sr,sc) = pos
        for (mr,mc) in piece.jump_directions():
          dr = sr + mr
          dc = sc + mc
          # Warning: mutual recursion.
          if self.is_valid_move(pos, (dr,dc), color):
            return True
    return False

  # Returns true if the player controlling color piece has a move avaiable to her.
  def can_move(self, color):
    if self.can_jump(color):
      return True
    for pos,piece in self.pieces.items():
      if piece.color == color:
        (sr,sc) = pos
        for (mr,mc) in piece.move_directions():
          dr = sr + mr
          dc = sc + mc
          if self.is_valid_move(pos, (dr,dc), color):
            return True
    return False
  
  # Returns whether moving from src to dest would be a valid move. Does not move.
  # Does not take into account turn order. Board positions should be given as (r,c).
  # For a double jump, is_valid_move needs to be called once for each step. Does
  # enforce necessary to jump if available
  # Pass in the color you are allowed to move.
  def is_valid_move(self, src, dest, color):
    (sr,sc) = src
    (dr,dc) = dest
    # Check if within range position
    if not(all(0 <= i < self.size for i in (sr,sc,dr,dc))):
      return False
    # Assert something at src to move
    if src not in self.pieces:
      return False
    # Cannot move to occupied square
    if dest in self.pieces:
      return False
    # Must move to black square
    # Note a square is black iff exactly one of it's row or column is even
    if 1 != (dr%2) + (dc%2):
      return False
    p = self.pieces[src]
    # Check to make sure not trying to move other player's piece
    if p.color != color:
      return False
    # If we are not trying to jump a piece, this is only valid if we could not jump
    if (dr-sr,dc-sc) in p.move_directions():
      # Warning: mutual recursion. lol
      return not self.can_jump(color)
    # Otherwise check to see if valid jump
    # Is this even somewhere we could jump to
    if not self.is_move_jump(src, dest):
      return False
    jump_pos = (dr+sr)//2,(dc+sc)//2
    # Cannot jump over nothing
    if jump_pos not in self.pieces:
      return False
    jumped = self.pieces[jump_pos]
    # Cannot jump own color
    if jumped.color == color:
      return False
    return True

  # Move piece from src to dest. Does not enforce turn order. Returns false
  # if invalid move (leaving board unchanged) or true if move made. Board positions
  # should be given as (r,c). Pass in the color you are allowed to move.
  def move(self, src, dest, color):
    if not self.is_valid_move(src, dest, color):
      return False
    (sr,sc) = src
    (dr,dc) = dest
    if self.is_move_jump(src, dest):
      del self.pieces[(dr+sr)//2,(dc+sc)//2]
    p = self.pieces[src]
    del self.pieces[src]
    if dr == 0 or dr == self.size - 1:
      p.king = True
    self.pieces[dest] = p
    return True

  # Will transform a8 to (0,0) etc.
  def str_to_boardpos(self, s):
    cl = s[:1]
    rl = s[1:]
    c = ord(cl) - ord('a')
    r = self.size - int(rl)
    return (r,c)

class CheckerGame:
  def __init__(self, board, players):
    self.board = board
    self.players = players
    self.turn = 0

  # Attempts to carry out a full move on board. Board should not
  # be self.board as this can modify board before finding the move
  # to be bad (for example, in the case of double jumps). pos_ls
  # should be a list of positions as (r,c)
  # Returns True if move is accepted.
  # Modifies board in place. If move was rejected consider board to
  # contain garbage.
  def _attempt_move(self, board, turn_color, pos_ls):
    # If there's more than one move, they must all be jumps
    require_jumps = len(pos_ls) > 2
    start_pos = pos_ls[0]
    # If there's no piece here to move, reject move
    if start_pos not in board.pieces:
      return False
    piece = board.pieces[start_pos]
    started_as_king = piece.king
    doing_jumps = board.is_move_jump(pos_ls[0], pos_ls[1])
    if not started_as_king:
      # If you didn't start as a king, you may not move backwards this turn
      # even if there is a backwards jump there
      src = pos_ls[0]
      for dest in pos_ls[1:]:
        sr,_ = src
        dr,_ = dest
        # If moving from src to dest row does not have the same sign as forwards
        # then you are going backwards
        if (dr-sr) / piece.forwards() < 0:
          return False
        src = dest
    # Here we make each move, actually modifying board
    src = pos_ls[0]
    for dest in pos_ls[1:]:
      if require_jumps and not board.is_move_jump(src, dest):
        return False
      elif not board.move(src, dest, turn_color):
        return False
      src = dest
    # Once started, a multiple jump must be carried through to completion. However, if
    # we were promoted during this move you are not requierd or allowed to carry out the
    # backwards jump
    if piece.king and not started_as_king:
      # Promoted this round, don't check to see if can jump
      return True
    if not doing_jumps:
      # We were never doing jumps, so we can't move any more
      return True
    # Otherwise we were doing jumps. Check to see if this piece could jump from last position.
    # If it could we were required to do it, so reject the move.
    (sr,sc) = pos_ls[-1]
    for (mr,mc) in piece.jump_directions():
      dr = mr + sr
      dc = mc + sc
      if board.is_valid_move( (sr,sc), (dr,dc), piece.color ):
        return False
    return True

  # Takes a full turn for one player. Returns True if the game continues
  def take_turn(self):
    player = self.players[self.turn]
    other = self.players[1 - self.turn]
    turn_color = [Color.RED,Color.BLACK][self.turn]

    while 1:
      data = player.get_command()
      if not data:
        other.show_player('GAMOVEOVER:Win')
        return False
      command, details = data
      if command == 'QUIT':
        print('Player forfeits')
        player.show_player('GAMEOVER:Loss')
        other.show_player('GAMEOVER:Win')
        return False
      elif command == 'MOVE':
        pos_ls = [self.board.str_to_boardpos(s) for s in details.split(',')]
        if len(pos_ls) < 2:
          player.show_player('REJECTED:No comma found in move')
        else:
          # Act on a temporary board so only commit if all moves in a double jump are sucessfull
          temp_board = copy.deepcopy(self.board)
          accepted = self._attempt_move(temp_board, turn_color, pos_ls)
          if accepted:
            # Commit board
            self.board = temp_board
            player.show_player('ACCEPTED:Move accepted')
            other.show_player('MOVE:%s' % details)
            break
          else:
            player.show_player('REJECTED:Not a valid checkers move')
      else:
        player.show_player('REJECTED:Not a valid command')

    # Note: if the other player has no more pieces then by definition they
    # cannot move. Also handles them being completely blocked
    if not self.board.can_move(Color.other(turn_color)):
      player.show_player('GAMEOVER:Win')
      other.show_player('GAMEOVER:Loss')
      return False

    self.turn = 1 - self.turn
    return True

  def play(self):
    print(self.board)
    while(self.take_turn()):
      print(self.board)
