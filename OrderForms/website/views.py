from flask import Blueprint, render_template, request, url_for, redirect, session, jsonify
from flask_login import login_required, current_user
from .models import KitType, Customer
from datetime import datetime
import re, requests, json, uuid, random

# Set blueprint
views = Blueprint('views', __name__)

# Orders
@views.route('/', methods=['GET', 'POST'])
@login_required
def orders():
    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Init session variables (Check if value exists first)
    session['OrderNumber'] = session['OrderNumber'] if 'OrderNumber' in session else None
    session['Details'] = session['Details'] if 'Details' in session else None
    errors = None
    
    if request.method == 'POST':

        # Get all form data
        data = request.form

        # Create errors dictionary
        errors = {}

        # Set session variables
        session['OrderNumber'] = data['OrderNumber']
        session['Details'] = data['Details']

        # Check order number length
        if len(data['OrderNumber']) < 3:
            errors['OrderNumber'] = 'Order number must be at least 3 characters'
        else:
            # Go to kit types
            return redirect(url_for("views.kit_types", user=current_user))
        
    return render_template("orders.jinja", user=current_user, role=session['Role'], order_number=session['OrderNumber'], details=session['Details'], errors=errors)

# Kit types
@views.route('/kit_types', methods=['GET', 'POST'])
@login_required
def kit_types():
    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they came from orders page
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    
    # Get kit types
    kit_types = KitType.query.join(Customer).filter(Customer.name == session['Role']).all()
    
    # Init session variables (Check if value exists first)
    session['Selection'] = session['Selection'] if 'Selection' in session else None
    index = int(len(session['Selection'])) if session['Selection'] is not None else 1
    
    if request.method == 'POST':

        # Get all form data
        data = request.form

        # Create item dictionary to hold kit type and quantities
        items = {}

        # Set session variables
        for i in range(1, int(len(data) / 2) + 1):
            if data[f'kit-option{i}'] in items:
                items[data[f'kit-option{i}']] = int(items[data[f'kit-option{i}']]) + int(data[f'kit-quantity{i}'])
            else:
                items[data[f'kit-option{i}']] = int(data[f'kit-quantity{i}'])

        session['Selection'] = items
        index = int(len(session['Selection'])) if session['Selection'] is not None else 1

        # Go to patient_info
        return redirect(url_for("views.patient_info"))

    if session['Selection'] is not None:
        return render_template("kit_types.jinja", user=current_user, kit_types=kit_types, selection=session['Selection'], index=index)
    else:
        return render_template("kit_types.jinja", user=current_user, kit_types=kit_types, selection={'default_key': 'default_value'}, index=index)

# Patient info
@views.route('/patient_info', methods=['GET', 'POST'])
@login_required
def patient_info():
    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    
    # Init session variables (Check if value exists first)
    session['FirstName'] = session['FirstName'] if 'FirstName' in session else None
    session['LastName'] = session['LastName'] if 'LastName' in session else None
    session['Email'] = session['Email'] if 'Email' in session else None
    session['Phone'] = session['Phone'] if 'Phone' in session else None
    errors = None
    
    if request.method == 'POST':

        # Get all form data
        data = request.form

        # Create errors dictionary
        errors = {}

        # Set session variables
        session['FirstName'] = data['FirstName']
        session['LastName'] = data['LastName']
        session['Email'] = data['Email']
        session['Phone'] = data['Phone']

        # Email address regex
        email_pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$" 

        # Phone regex
        phone_pattern = r"^\(\d{3}\) \d{3}-\d{4}$"

        if len(data['FirstName']) < 3:
            errors['FirstName'] = 'First name must be at least 3 characters'
        if len(data['LastName']) < 3:
            errors['LastName'] = 'Last Name must be at least 3 characters'
        if re.match(email_pattern, data['Email']) == None:
            errors['Email'] = 'Invalid email format, please try again'
        if re.match(phone_pattern, data['Phone']) == None:
            errors['Phone'] = 'Invalid phone format, please try again. Format should be (###)-###-####'

        if len(errors) == 0:
            # Go to address
            return redirect(url_for("views.address"))
        
    return render_template("patient_info.jinja", user=current_user, first_name=session['FirstName'], last_name=session['LastName'], 
                            email=session['Email'], phone=session['Phone'], errors=errors)

# Address
@views.route('/address', methods=['GET', 'POST'])
@login_required
def address():
    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    if 'FirstName' not in session or session['FirstName'] == None:
        return redirect(url_for('views.patient'))
    
    # Init session variables (Check if value exists first)
    session['AddressLine1'] = session['AddressLine1'] if 'AddressLine1' in session else None
    session['AddressLine2'] = session['AddressLine2'] if 'AddressLine2' in session else None
    session['City'] = session['City'] if 'City' in session else None
    session['State'] = session['State'] if 'State' in session else None
    session['Zip'] = session['Zip'] if 'Zip' in session else None
    session['CountryCode'] = session['CountryCode'] if 'CountryCode' in session else None
    errors = None
    
    if request.method == 'POST':

        # Get all form data
        data = request.form

        # Create errors dictionary
        errors = {}

        # Set session variables
        session['AddressLine1'] = data['AddressLine1']
        session['AddressLine2'] = data['AddressLine2']
        session['City'] = data['City']
        session['State'] = data['State']
        session['Zip'] = data['Zip']
        session['CountryCode'] = data['CountryCode']

        if len(data['AddressLine1']) < 3:
            errors['AddressLine1'] = 'Address Line 1 must be at least 3 characters'
        if len(data['State']) < 3:
            errors['State'] = 'State must be at least 3 characters'
        if len(data['City']) < 3:
            errors['City'] = 'City must be at least 3 characters'
        if len(data['Zip']) < 3:
            errors['Zip'] = 'Zip must be at least 3 characters'

        if len(errors) == 0:
            # Go to submitted page
            return redirect(url_for('views.submission'))
            
    return render_template("address.jinja", user=current_user, address_line_1=session['AddressLine1'], address_line_2=session['AddressLine2'], 
                            state=session['State'], city=session['City'], zip=session['Zip'], country_code=session['CountryCode'], errors=errors)

# Submission
@views.route('/submission', methods=['GET', 'POST'])
@login_required
def submission():

    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    if 'FirstName' not in session or session['FirstName'] == None:
        return redirect(url_for('views.patient'))
    if 'AddressLine1' not in session or session['AddressLine1'] == None:
        return redirect(url_for('views.address'))
    
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('views.address'))
        
    return render_template("submission.jinja", user=current_user)

# Submission Passed
@views.route('/submission_passed', methods=['GET', 'POST'])
@login_required
def submission_passed():

    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    if 'FirstName' not in session or session['FirstName'] == None:
        return redirect(url_for('views.patient'))
    if 'AddressLine1' not in session or session['AddressLine1'] == None:
        return redirect(url_for('views.address'))
    
    if request.method == 'POST':
        role = session['Role']
        session.clear()
        session['Role'] = role
        return redirect(url_for('views.orders'))
        
    return render_template("submission-passed.jinja", user=current_user)

# Submission
@views.route('/submission_failed', methods=['GET', 'POST'])
@login_required
def submission_failed():

    # Check if session is active
    if 'Role' not in session:
        return redirect(url_for('auth.logout'))
    
    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    if 'FirstName' not in session or session['FirstName'] == None:
        return redirect(url_for('views.patient'))
    if 'AddressLine1' not in session or session['AddressLine1'] == None:
        return redirect(url_for('views.address'))
    
    if request.method == 'POST':
        role = session['Role']
        session.clear()
        session['Role'] = role
        return redirect(url_for('views.orders'))
        
    return render_template("submission-failed.jinja", user=current_user, error=session['SubmissionError'], message=session['SubmissionMessage'])

# Send Data
@views.route('/send_data', methods=['GET'])
@login_required
def send_data():

    # Only allow user to continue if they followed the correct process
    if 'OrderNumber' not in session or session['OrderNumber'] == None:
        return redirect(url_for('views.orders'))
    if 'Selection' not in session or session['Selection'] == None:
        return redirect(url_for('views.kit_types'))
    if 'FirstName' not in session or session['FirstName'] == None:
        return redirect(url_for('views.patient'))
    if 'AddressLine1' not in session or session['AddressLine1'] == None:
        return redirect(url_for('views.address'))

    # Url to send data to
    url = ""

    # Compile products
    products = []
    for k, v in session['Selection'].items():
        products.append({'sku': k, 'quantity': v})

    # Compile data for json string
    data = {}
    data['enterpriseGUID'] = str(uuid.uuid4())
    data['transDate'] = datetime.now().strftime("%m%d%Y")
    data['transTime'] = datetime.now().strftime("%H%M%S")
    data['sourceSystem'] = ''
    data['destinationSystem'] = ''
    data['request'] = {
        'requestID': str(random.randrange(1000000000, 10000000000)),
        'orders': [{
            'customer': session['Role'],
            'order_number': session['OrderNumber'],
            'order_details': session['Details'],
            'order_date': datetime.now().strftime("%Y-%m-%d"),
            'products': products,
            'shipping_address': {
                'state_province': session['State'],
                'zip_postal_code': session['Zip'],
                'phone': session['Phone'],
                'email': session['Email'],
                'country_code': session['CountryCode'],
                'country': 'Canada',
                'company': '',
                'city': session['City'],
                'first_name': session['FirstName'],
                'last_name': session['LastName'],
                'attention': f"{session['FirstName']} {session['LastName']}",
                'address2': session['AddressLine2'],
                'address1': session['AddressLine1']
            }
        }]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': ''
    }

    # Send the request to flow
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))

    # Get error messages
    if response.status_code == 200:
        json_response = json.loads(response.text)['response']
        if json_response['requestStatus'] == 'REJECTED':
            message = f"<b>Global Error:</b> {json_response['globalError']} <br> <b>Order Error:</b> "
            index = 1
            for e in json_response['rejectedOrders'][0]['errors']:
                message += f"<b>({index})</b> - {e} "
                index = index + 1
            session['SubmissionError'] = True
            session['SubmissionMessage'] = message
        else:
            return jsonify({'redirect_url': '/submission_passed'})
    else:
        session['SubmissionError'] = True
        session['SubmissionMessage'] = f"<b>Unable to Connect</b> <br> <b>Status Code:</b> {response.status_code} <br> <b>Reason:</b> {response.reason}"

    return jsonify({'redirect_url': '/submission_failed'})