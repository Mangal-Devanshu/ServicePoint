from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def home():
    print("hi someone give us a request!!")
    return render_template("./index.html",name="Raju")

if __name__ == '__main__':
    app.run(debug=True)