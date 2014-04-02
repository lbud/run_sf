from flask import Flask, render_template, redirect, request, session, url_for
import config
import models

app = Flask(__name__)
app.config.from_object(config)

@app.route("/")
def start():
    return render_template("start.html")

@app.route("/", methods=["POST"])
def find():
    data = request.form
    distance = float(data.get('distance'))
    start_loc = (float(data.get('lat')), float(data.get('lon')))
    print start_loc
    print distance

    rt  = models.Route(start_loc, models.mp)
    route = rt.render
    print rt.gain
    print route


    return route

if __name__ == "__main__":
    app.run(debug=True)