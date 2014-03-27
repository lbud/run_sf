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
    start_loc = request.form.get("start")
    end_loc = request.form.get("end")

    start = models.h
    end = models.vl
    print start
    print end

    rt  = models.Route(models.h, models.vl)
    print rt
    route = rt.render

    return render_template("route.html", route=route)

if __name__ == "__main__":
    app.run(debug=True)