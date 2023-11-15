from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route("/messages", methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by("created_at").all()

        return [message.to_dict() for message in messages], 200

    else:
        req_data = request.get_json()
        message = Message(body=req_data["body"], username=req_data["username"])

        db.session.add(message)
        db.session.commit()

        return message.to_dict(), 201


@app.route("/messages/<int:id>", methods=["GET", "PATCH", "DELETE"])
def messages_by_id(id):
    message = db.session.get(Message, id)
    # message = Message.query.filter_by(id=id).first()

    if request.method == "GET":
        return message, 200

    elif request.method == "PATCH":
        req_data = request.get_json()
        for attr in req_data:
            setattr(message, attr, req_data[attr])

        db.session.add(message)
        db.session.commit()

        return message.to_dict(), 200

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()

        return {"message": f"Message id#{message.id} was deleted."}, 200


if __name__ == "__main__":
    app.run(port=5555)
