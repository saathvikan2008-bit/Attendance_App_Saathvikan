# Tic Tac Toe Game in Python

# Function to print the game board
def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

# Function to check for a win
def check_winner(board, player):
    # Check rows, columns, and diagonals
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)) or all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

# Function to check if the board is full
def is_draw(board):
    return all(cell != " " for row in board for cell in row)

# Main game function
def tic_tac_toe():
    # Initialize the board
    board = [[" " for _ in range(3)] for _ in range(3)]
    players = ["X", "O"]
    current_player = 0

    print("Welcome to Tic Tac Toe!")
    print_board(board)

    while True:
        # Get the current player's move
        print(f"Player {players[current_player]}'s turn.")
        try:
            row = int(input("Enter row (0, 1, 2): "))
            col = int(input("Enter column (0, 1, 2): "))
            if board[row][col] != " ":
                print("Cell already taken! Try again.")
                continue
        except (ValueError, IndexError):
            print("Invalid input! Please enter numbers between 0 and 2.")
            continue

        # Make the move
        board[row][col] = players[current_player]
        print_board(board)

        # Check for a winner
        if check_winner(board, players[current_player]):
            print(f"Player {players[current_player]} wins!")
            break

        # Check for a draw
        if is_draw(board):
            print("It's a draw!")
            break

        # Switch to the other player
        current_player = 1 - current_player

# Run the game
if __name__ == "__main__":
    tic_tac_toe()
