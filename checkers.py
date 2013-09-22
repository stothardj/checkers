# Enum with textual representation
class Color:
  RED = 'r'
  BLACK = 'b'

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

def space_pad_front(s, size):
  return ''.join(' ' for i in range(0, size-len(s))) + s

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
      letter = space_pad_front(str(self.size - r), 2)
      rows[r] = letter + '|' + ''.join(rows[r]) + '|'
    oneline = '\n'.join(rows)
    # I FINALLY ACTUALLY WANT TO MULTIPLY A STRING AND GET THIS BEHAVIOR!
    horizontal = '  +' + ('-' * self.size) + '+'
    oneline = horizontal + '\n' + oneline + '\n' + horizontal
    top = '   ' + ''.join(chr(i+ord('a')) for i in range(0,self.size))
    return top + '\n' + oneline

print(CheckerBoard(10,4))

print(CheckerBoard(8,3))

