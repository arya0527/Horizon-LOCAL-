import os
from flask import Blueprint
from flask import jsonify

import pandas as pd

internship_bp = Blueprint(
    'internship',
    __name__
)

@internship_bp.route('/internships', methods=['GET'])
def get_internships():

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, 'datasets', 'internships.csv')
    internships_df = pd.read_csv(csv_path)

    internships = internships_df.to_dict(
        orient='records'
    )

    return jsonify(internships)