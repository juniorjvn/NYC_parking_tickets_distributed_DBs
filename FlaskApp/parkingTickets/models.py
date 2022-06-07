from parkingTickets import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.first_name}', '{self.last_name}')"


class Global_violations(db.Model):
    summons_number = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2), nullable=False)
    county = db.Column(db.Integer, nullable=False)
    plate = db.Column(db.String(10), nullable=False)
    license_type = db.Column(db.String(3), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    violation_time = db.Column(db.Time, nullable=True)
    violation = db.Column(db.String(50), nullable=True)
    fine_amount = db.Column(db.Float, nullable=True)
    penalty_amount = db.Column(db.Float, nullable=True)
    interest_amount = db.Column(db.Float, nullable=True)
    reduction_amount = db.Column(db.Float, nullable=True)
    issuing_agency = db.Column(db.String(40), nullable=True)
    violation_status = db.Column(db.String(30), nullable=True)
    summons_image = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Violation('{self.summons_number}', '{self.state}', '{self.plate}', '{self.issue_date}')"

