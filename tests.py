from flask import Flask, request, render_template, redirect, session
# import pymongo



app = Flask(__name__)


# collection = pymongo.MongoClient(
#         'mongodb+srv://MaxTeslya:7887334Mna@melytixdata'
#         '-ryedw.mongodb.net/test?retryWrites=true&w=majority')
# db = collection.MelytixUsers.Users


@app.route('/test', methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        answ = request.form.getlist('Box')
        return redirect('/test2/{}'.format(answ))

    return render_template('connect_sys.html')


@app.route('/bomb', methods=['POST'])
def bomber():
    print(request.get_json())
    return 'Success', 200


@app.route('/tete', methods=['POST', 'GET'])
def tete():
    args = request.args
    keys = args.keys()
    for val in keys:
        print(val, '=', args[val])
    print(args)
    return '{}'.format(args)

@app.route('/test2/<answ>')
def test2(answ):
    return '<p>{}</p>'.format(answ)


# @app.route('/add_user/<email>/<password>')
# def add_user(email: str, password: str) -> None:
#     db.insert_one({
#         'email': email,
#         'password': password
#     })
#     return 'Success', 200


# @app.route('/delete_user/<email>')
# def delete_user(email):
#     db.delete_one({'email': email})
#     return 'Success', 200


# @app.route('/find_user/<email>')
# def find_user(email: str) -> object:
#     user = db.find_one({'email': email})
#     print(user)
#     return 'user: {}'.format(user)


# @app.route('/get_name', methods=['GET', 'POST'])
# def method_name():
#     if request.method == 'POST':
#         print('reached', " ", request.is_json, ' ', request.get_json())
#         return 'Success', 200


if __name__ == '__main__':
    app.run(debug=True)
