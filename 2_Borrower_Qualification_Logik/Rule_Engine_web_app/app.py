# Importing Flask from flask library to create a Flask application
from flask import Flask 

# Importing custom controllers for handling XML and JSON rule engine logic
from Controller.Rule_Engine_XML_Controller import Rule_Engine_XML_Controller
from Controller.Rule_Engine_JSON_Form_Controller import Rule_Engine_JSON_Form_Controller


# Creating the Flask application instance
app = Flask(__name__)

# Defining the static folder for serving static files (if needed)
app.static_folder = 'static'

# Adding a URL rule to handle requests at "/api/request-rules"
# This URL is mapped to the Rule_Engine_XML_Controller which handles GET and POST requests
app.add_url_rule(
    "/api/request-rules", 
    view_func=Rule_Engine_XML_Controller.as_view("my-view"), 
    methods=["GET", "POST"]
)

# Adding a URL rule for the root URL ("/") which uses the Rule_Engine_JSON_Form_Controller
# This handles form-based JSON rule engine logic
app.add_url_rule(
    f"/", 
    view_func=Rule_Engine_JSON_Form_Controller.as_view("Rule_Engine_JSON_Form-Controller")
)

# Starting the Flask application when the script is executed directly
if __name__ == '__main__':

    app.run()