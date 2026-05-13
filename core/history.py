class MoveHistory:

    def __init__(self):

        self.undo_stack = []
        self.redo_stack = []

    def add_move(self, row, col, player):

        self.undo_stack.append(
            (row, col, player)
        )

        self.redo_stack.clear()

    def undo(self, board):

        if not self.undo_stack:
            return None

        row, col, player = self.undo_stack.pop()

        board[row][col] = "."

        self.redo_stack.append(
            (row, col, player)
        )

        return player

    def redo(self, board):

        if not self.redo_stack:
            return None

        row, col, player = self.redo_stack.pop()

        board[row][col] = player

        self.undo_stack.append(
            (row, col, player)
        )

        return player