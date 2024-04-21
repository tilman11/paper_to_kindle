# install python
apt update
apt get install python3 python3-pip python3-venv
# setup venv
python -m venv .venv
## activate venv
. .venv/bin/activate


# run flask: 1. set env variable
export FLASK_APP=some_flask_app.python
# --host 0.0.0.0: public for local network
# --debug: restart server after every change
# -p 4000: port for shell 
flask run --host 0.0.0.0 --debug -p 4000


