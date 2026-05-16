# Window

BOARD_SIZE = 9
CELL_SIZE = 60

BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE

SIDEBAR_WIDTH = 300
GAP_SIZE = 40

WINDOW_WIDTH = (
    50
    + BOARD_PIXEL_SIZE
    + GAP_SIZE
    + SIDEBAR_WIDTH
)

WINDOW_HEIGHT = 750


# Board

BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50

WIN_COUNT = 4


# ========================
# Colors — Light Theme
# ========================

# Background & layout
BG_COLOR        = (245, 245, 245)   # main background
SIDEBAR_COLOR   = (225, 225, 225)   # sidebar panel
GRID_COLOR      = (180, 180, 180)   # board grid lines
OVERLAY_COLOR   = (0,   0,   0)     # dim overlay fill (use with set_alpha)

# Text
TEXT_COLOR      = (30,  30,  30)    # primary text
TEXT_DIM        = (100, 100, 100)   # secondary / sub text
TEXT_ACCENT     = (180, 100, 20)    # highlighted text (overlay title)
TEXT_DIALOG     = (50,  50,  120)   # dialog title text
TEXT_DIALOG_SUB = (100, 100, 140)   # dialog subtitle text
TEXT_WINNER     = (200, 140, 20)    # winner label in compare screen

# Pieces
X_COLOR = (220, 50,  50)            # X piece
O_COLOR = (30,  130, 220)           # O piece

# Buttons — general
BUTTON_COLOR    = (190, 190, 190)
BUTTON_HOVER    = (160, 160, 160)

# Buttons — AI selected (home screen)
BTN_AI_DEFAULT  = (90,  90,  90)
BTN_AI_SELECTED = (70,  130, 220)

# Buttons — compare screen (orange)
BTN_COMPARE     = (180, 120, 40)

# Popup / dialog box
POPUP_BG        = (240, 240, 240)   # popup background
POPUP_BORDER    = (180, 180, 180)   # popup border

# Dialog box (order-choice)
DIALOG_BG       = (240, 240, 245)
DIALOG_BORDER   = (160, 160, 200)

# Order-choice buttons
BTN_FIRST_BG        = (50,  120, 75)
BTN_FIRST_HOVER     = (60,  150, 90)
BTN_FIRST_BORDER    = (100, 220, 140)
BTN_SECOND_BG       = (120, 75,  50)
BTN_SECOND_HOVER    = (150, 90,  60)
BTN_SECOND_BORDER   = (220, 140, 100)

# Toggle AI button
BTN_AI_ON   = (60,  140, 80)
BTN_AI_OFF  = (130, 60,  60)

# Start / play button (home screen)
BTN_START   = (60,  140, 80)

# 2-player button (home screen)
BTN_2P      = (80,  80,  180)


# Symbols

EMPTY    = "."
PLAYER_X = "X"
PLAYER_O = "O"


# Game States

HOME_SCREEN    = "HOME"
GAME_SCREEN    = "GAME"
COMPARE_SCREEN = "COMPARE"


# AI Modes

MINIMAX   = "MINIMAX"
ALPHABETA = "ALPHABETA"