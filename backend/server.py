from flask import Flask, request, jsonify
from flask_cors import CORS
# from flask_mysqldb import MySQL
import groups

from authentication import login, register

app = Flask(__name__)
# CORS(app)
# mysql = MySQL()

# app.config['MYSQL_DATABASE_DB'] = 'projdb'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_PORT'] = '5002'
# mysql.init_app(app)

MAX_STUDENT_PER_GROUP = 6


@app.route('/')
def home():
    return "TEST"

@app.post('/login')
def auth_login():
    email = request.form['email']
    password = request.form['password']
    return jsonify(login(email, password))

@app.post('/register')
def auth_register():
    email = request.form['email']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    return jsonify(register(email, password, firstName, lastName))

@app.route('/group/create', methods=['POST'])
def create_group_endpoint():
    group_name = request.form['groupname']
    creator_id = request.form['ownerid']
    response, status_code = groups.create_group(group_name, creator_id)
    return jsonify(response), status_code

@app.route('/groups/view', methods=['GET'])
def view_groups_route():
    return jsonify(groups.view_groups())

@app.route('/group/join', methods=['POST'])
def join_group_route():
    data = request.form
    group_id = data.get('groupid')
    student_id = data.get('userid')
    response, status_code = groups.join_group(group_id, student_id, MAX_STUDENT_PER_GROUP)
    return jsonify(response), status_code

@app.route('/group/request/handle', methods=['POST'])
def handle_join_request_route():
    data = request.form
    user_id = int(data.get('userid'))
    applicant_id = int(data.get('applicantid'))
    group_id = int(data.get('groupid'))
    accept = int(data.get('accept'))
    response, status_code = groups.handle_join_request(user_id, applicant_id, group_id, accept, MAX_STUDENT_PER_GROUP)
    return jsonify(response), status_code

@app.route('/group', methods=['GET'])
def view_group_details_route():
    group_id = request.args.get('groupid')
    response, status_code = groups.view_group_details(group_id)
    return jsonify(response), status_code

@app.route('/user/join_requests', methods=['GET'])
def view_join_requests_route():
    user_id = request.args.get('userid')
    response, status_code = groups.view_join_requests(user_id)
    return jsonify(response), status_code

@app.route('/group/leave', methods=['POST'])
def leave_group_route():
    data = request.form
    user_id = data.get('userid')
    response, status_code = groups.leave_group(user_id)
    return jsonify(response), status_code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5097)