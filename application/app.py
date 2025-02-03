from flask import Flask, request, jsonify, render_template_string, Response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

# ==============================
# Configuration
# ==============================
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hkrn.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# ==============================
# Initialize App, DB, and API
# ==============================
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app)

# ==============================
# Home Page Route with Attractive CSS
# ==============================
@app.route('/')
def home():
    home_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>HKRN API Home</title>
      <style>
          body {
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              background: linear-gradient(135deg, #71b7e6, #9b59b6);
              color: #fff;
              text-align: center;
              padding: 50px;
          }
          h1 {
              font-size: 2.5em;
              margin-bottom: 20px;
          }
          ul {
              list-style: none;
              padding: 0;
          }
          li {
              margin: 15px 0;
          }
          a {
              text-decoration: none;
              color: #fff;
              background-color: rgba(0,0,0,0.2);
              padding: 12px 20px;
              border-radius: 5px;
              font-size: 1.1em;
              transition: background-color 0.3s ease;
          }
          a:hover {
              background-color: rgba(0,0,0,0.4);
          }
      </style>
    </head>
    <body>
      <h1>Welcome to the HKRN API</h1>
      <p>Navigate to the following endpoints:</p>
      <ul>
          <li><a href="/candidates">Candidates</a></li>
          <li><a href="/job_listings">Job Listings</a></li>
          <li><a href="/training_programs">Training Programs</a></li>
          <li><a href="/assessment_tests">Assessment Tests</a></li>
          <li><a href="/applications">Applications</a></li>
      </ul>
    </body>
    </html>
    """
    return render_template_string(home_html)

# ==============================
# Models
# ==============================
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255))
    skills = db.Column(db.Text)
    qualifications = db.Column(db.Text)
    experience = db.Column(db.Text)

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    salary = db.Column(db.String(50))
    status = db.Column(db.String(10), default='Open')

class TrainingProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    skills_covered = db.Column(db.Text)
    institution_partnered = db.Column(db.String(255))

class AssessmentTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_area = db.Column(db.String(255), nullable=False)
    test_description = db.Column(db.Text)
    performance_metrics = db.Column(db.Text)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')

# ==============================
# Helper Function to Render HTML Tables
# ==============================
def render_table(title, columns, data):
    header = "".join([f"<th>{col}</th>" for col in columns])
    rows = ""
    for row in data:
        row_html = "".join([f"<td>{row.get(col, '')}</td>" for col in columns])
        rows += f"<tr>{row_html}</tr>"
    no_data_row = f'<tr><td colspan="{len(columns)}">No records available.</td></tr>'
    table = f"""
    <h1>{title}</h1>
    <table class='data-table'>
      <thead>
        <tr>{header}</tr>
      </thead>
      <tbody>
        {rows if rows else no_data_row}
      </tbody>
    </table>
    <p><a href='/'>Back to Home</a></p>
    """
    return table

def render_page(content, title="HKRN Data"):
    page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{title}</title>
      <style>
          body {{
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              background-color: #f4f4f4;
              padding: 20px;
          }}
          h1 {{
              color: #333;
              text-align: center;
          }}
          table.data-table {{
              width: 80%;
              margin: 20px auto;
              border-collapse: collapse;
          }}
          table.data-table th, table.data-table td {{
              border: 1px solid #ccc;
              padding: 10px;
              text-align: left;
          }}
          table.data-table th {{
              background-color: #007BFF;
              color: #fff;
          }}
          a {{
              display: block;
              width: 150px;
              margin: 20px auto;
              text-align: center;
              text-decoration: none;
              padding: 10px;
              background-color: #007BFF;
              color: #fff;
              border-radius: 5px;
          }}
          a:hover {{
              background-color: #0056b3;
          }}
      </style>
    </head>
    <body>
      {content}
    </body>
    </html>
    """
    return page

# ==============================
# API Endpoints with HTML Rendering
# ==============================
class CandidateResource(Resource):
    def get(self):
        candidates = Candidate.query.all()
        data = [{
            'ID': c.id,
            'Name': c.name,
            'Contact': c.contact_info,
            'Skills': c.skills
        } for c in candidates]
        content = render_table("Candidates", ['ID', 'Name', 'Contact', 'Skills'], data)
        html = render_page(content, "Candidates")
        return Response(html, mimetype='text/html')

class JobListingResource(Resource):
    def get(self):
        jobs = JobListing.query.all()
        data = [{
            'ID': j.id,
            'Company': j.company_name,
            'Salary': j.salary,
            'Status': j.status
        } for j in jobs]
        content = render_table("Job Listings", ['ID', 'Company', 'Salary', 'Status'], data)
        html = render_page(content, "Job Listings")
        return Response(html, mimetype='text/html')

class TrainingProgramResource(Resource):
    def get(self):
        programs = TrainingProgram.query.all()
        data = [{
            'ID': t.id,
            'Program': t.program_name,
            'Institution': t.institution_partnered
        } for t in programs]
        content = render_table("Training Programs", ['ID', 'Program', 'Institution'], data)
        html = render_page(content, "Training Programs")
        return Response(html, mimetype='text/html')

class AssessmentTestResource(Resource):
    def get(self):
        tests = AssessmentTest.query.all()
        data = [{
            'ID': a.id,
            'Skill Area': a.skill_area,
            'Description': a.test_description
        } for a in tests]
        content = render_table("Assessment Tests", ['ID', 'Skill Area', 'Description'], data)
        html = render_page(content, "Assessment Tests")
        return Response(html, mimetype='text/html')

class ApplicationResource(Resource):
    def get(self):
        applications = Application.query.all()
        data = [{
            'ID': a.id,
            'Candidate ID': a.candidate_id,
            'Job ID': a.job_id,
            'Status': a.status
        } for a in applications]
        content = render_table("Applications", ['ID', 'Candidate ID', 'Job ID', 'Status'], data)
        html = render_page(content, "Applications")
        return Response(html, mimetype='text/html')

# ==============================
# Register API Endpoints
# ==============================
api.add_resource(CandidateResource, '/candidates')
api.add_resource(JobListingResource, '/job_listings')
api.add_resource(TrainingProgramResource, '/training_programs')
api.add_resource(AssessmentTestResource, '/assessment_tests')
api.add_resource(ApplicationResource, '/applications')

# ==============================
# Main Execution (Create DB and Insert Sample Data)
# ==============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Candidate.query.count() == 0:
            sample_candidate = Candidate(
                name="John Doe",
                contact_info="john@example.com",
                skills="Python, Flask, SQLAlchemy",
                qualifications="B.Sc. Computer Science",
                experience="3 years"
            )
            db.session.add(sample_candidate)
        if JobListing.query.count() == 0:
            sample_job = JobListing(
                company_name="Acme Corp",
                job_description="Software Developer position",
                required_skills="Python, SQL, REST APIs",
                salary="$50,000",
                status="Open"
            )
            db.session.add(sample_job)
        if TrainingProgram.query.count() == 0:
            sample_training = TrainingProgram(
                program_name="Python Bootcamp",
                description="Intensive training in Python and Flask.",
                skills_covered="Python, Flask, SQLAlchemy",
                institution_partnered="Tech Institute"
            )
            db.session.add(sample_training)
        if AssessmentTest.query.count() == 0:
            sample_test = AssessmentTest(
                skill_area="Python",
                test_description="Basic Python programming skills assessment.",
                performance_metrics="Score out of 100"
            )
            db.session.add(sample_test)
        if Application.query.count() == 0:
            sample_application = Application(
                candidate_id=1,
                job_id=1,
                status="Pending"
            )
            db.session.add(sample_application)
        db.session.commit()
    app.run(debug=True)