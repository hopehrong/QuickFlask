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
    # TODO: if there is no player move, render the page template
    print(ui.board)
    return render_template('chess.html', ui=ui)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 
    if game.promotepawns():
        ui.inputlabel = 'promotedpiece'
        ui.btnlabel = 'Promote'
        return redirect('/promote')

@app.route('/promote')
def promote():
    print(ui.board)
    return render_template('chess.html', ui=ui)
    target = request.args['promotedpieces']

app.run('0.0.0.0')
