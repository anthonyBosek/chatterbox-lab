from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route("/messages", methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        all_messages = [
            message.to_dict() for message in Message.query.order_by("created_at").all()
        ]
        return all_messages, 200
    else:
        try:
            req_data = request.get_json()
            message = Message(**req_data)  #! model validations might fails
            db.session.add(message)
            db.session.commit()  #! db constraints might fails
            return message.to_dict(), 201
        except:
            db.session.rollback()
            return {"error": "Something went wrong!"}, 422


@app.route("/messages/<int:id>", methods=["PATCH", "DELETE"])
def messages_by_id(id):
    if request.method == "PATCH":
        try:
            req_data = request.get_json()
            if message := db.session.get(Message, id):
                for k, v in req_data.items():
                    setattr(message, k, v)
                db.session.commit()
                return message.to_dict(), 200
            return {"error": f"No Message by id {id} found"}, 404
        except:
            db.session.rollback()
            return {"error": "Something went wrong!"}, 422
    else:
        try:
            if message := db.session.get(Message, id):
                db.session.delete(message)
                db.session.commit()
                return {}, 204
            return {"error": f"No Message by id {id} found"}, 404
        except:
            db.session.rollback()
            return {"error": f"Could not delete Message with id {id}"}


if __name__ == "__main__":
    app.run(port=5555)
