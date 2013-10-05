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

  # Since a CheckerPiece doesn't know it's position, it relies on the 
  # CheckerBoard to add the move_directions to the current position to
  # get the new position. This means this can't actually check if this
  # goes off the board. Note for simplicity black is always starting at
  # the top going down
  def move_directions(self):
    if self.color == Color.BLACK:
      forwards = 1
    else:
      forwards = -1
    yield (forwards, -1)
    yield (forwards, 1)
    if self.king:
      yield (-forwards, -1)
      yield (-forwards, 1)
  
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
      # Warning: mutual recursion.
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

  # Returns true if either player has been eliminated from the board
  def player_eliminated(self):
    has_red = False
    has_black = False
    for piece in self.pieces.values():
      if piece.color == Color.RED:
        has_red = True
      else:
        has_black = True
      if has_red and has_black:
        return False
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

  # Takes a full turn for one player. Returns True if the game continues
  def take_turn(self):
    player = self.players[self.turn]
    other = self.players[1 - self.turn]

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
        # Act on a temporary board so only commit if all moves in a double jump are sucessfull
        temp_board = copy.deepcopy(self.board)
        pos_ls = details.split(',')
        if len(pos_ls) < 2:
          player.show_player('REJECTED:No comma found in move')
        else:
          # If there's more than one move, they must all be jumps
          require_jumps = len(pos_ls) > 2
          any_rejections = False
          ps = temp_board.str_to_boardpos(pos_ls[0])
          for dest in pos_ls[1:]:
            pd = temp_board.str_to_boardpos(dest)
            if require_jumps and not temp_board.is_move_jump(ps, pd):
              any_rejections = True
              player.show_player('REJECTED:All moves must be a jump if more than one move')
              break
            elif not temp_board.move(ps, pd, player.color):
              any_rejections = True
              player.show_player('REJECTED:Not a valid checkers move')
              break
            ps = pd
          if not any_rejections:
            # Commit board
            self.board = temp_board
            player.show_player('ACCEPTED:Move accepted')
            other.show_player('MOVE:%s' % details)
            break
      else:
        player.show_player('REJECTED:Not a valid command')

    if self.board.player_eliminated():
      player.show_player('GAMEOVER:Win')
      other.show_player('GAMEOVER:Loss')
      return False

    self.turn = 1 - self.turn
    return True

  def play(self):
    print(self.board)
    while(self.take_turn()):
      print(self.board)
