from flask import Flask
from flask import render_template, redirect, request
from chess import WebInterface, Board

app = Flask(__name__)
ui = WebInterface()
game = Board()

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/newgame')
def newgame():
    # Note that in Python, objects and variables
    # in the global space are available to
    # top-level functions
    game.start()
    ui.board = game.display()
    ui.inputlabel = f'{game.turn} player: '
    ui.errmsg = None
    ui.btnlabel = 'Move'
    return redirect('/play')

@app.route('/play')
def play():
    # TODO: get player move from GET request object
    move = request.args.get('moves','')
    print(move)
    # TODO: if there is no player move, render the page template
    if move == '':
        return render_template('chess.html', ui=ui)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    elif not game.valid_format(move):
        ui.errmsg = 'Invalid move. Please enter your move in the following format: __ __, _ represents a digit.'
        return render_template('chess.html', ui=ui)
    elif not game.valid_num(move):
        ui.errmsg = 'Invalid move. Move digits should be 0-7.'
        return render_template('chess.html', ui=ui)
    else:
        start, end = game.split_and_convert(move)
        movetype = game.movetype(start, end)
        if movetype is None:
            ui.errmsg = 'Invalid move. Please make a valid move.'
            return render_template('chess.html', ui=ui)
        else:
            game.update(start,end)

    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 
    if game.promotepawns():
        return redirect('/promote')

    

    

@app.route('/promote')
def promote():
    ui.board = game.display()
    ui.inputlabel = 'promote pawns to:'
    ui.btnlabel = 'PROMOTE'
    return render_template('chess.html', ui=ui)

app.run('0.0.0.0')
