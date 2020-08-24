from flask import Flask
from flask import render_template, redirect, request
from chess import WebInterface, Board

app = Flask(__name__)
game = Board(endtest=True)
ui = WebInterface(game)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/newgame')
def newgame():
    # Note that in Python, objects and variables
    # in the global space are available to
    # top-level functions
    game.start()
    ui.update('/play')
    return redirect('/play')

@app.route('/play')
def play():
    # TODO: get player move from GET request object
    move = request.args.get('moves','')
    # TODO: if there is no player move, render the page template
    if move == '':
        return render_template('chess.html', ui=ui)
    # TODO: Validate move, redirect player back to /play again if move is invalid
    elif not game.valid_format(move):
        ui.update_err('Invalid move. Please enter your move in the following format: __ __, _ represents a digit.')
        return render_template('chess.html', ui=ui)
    elif not game.valid_num(move):
        ui.update_err('Invalid move. Move digits should be 0-7.')
        return render_template('chess.html', ui=ui)
    else:
        start, end = game.split_and_convert(move)
        movetype = game.movetype(start, end)
        if movetype is None:
            ui.update_err('Invalid move. Please make a valid move.')
            return render_template('chess.html', ui=ui)
        else:
            game.update(start,end)

    # If move is valid, check for pawns to promote
    # Redirect to /promote if there are pawns to promote, otherwise 
    
    if game.checkpromotion():
        ui.update('/promote')    
        return redirect('/promote')
    
    elif game.winner != None:
        ui.update('/end')
        return redirect('/end')
    else:
        game.next_turn()
        ui.update()
        return render_template('chess.html', ui=ui)

@app.route('/promote')
def promote():
    move = request.args.get('moves','')
    if move == '':
        return render_template('chess.html', ui=ui)
    if move not in 'rbqk':
        ui.update_err('Invalid input, the input should be one of rbqk')
        return redirect('/promote')
    else:
        game.promotion(move)
        game.next_turn()
        ui.update('/play')
        return redirect('/play')

@app.route('/end')
def end():    
    return render_template('chess.html', ui=ui)

@app.route('/undo')
def undo():
    game.undo()
    ui.update()
    return redirect('/play')


app.run('0.0.0.0')
