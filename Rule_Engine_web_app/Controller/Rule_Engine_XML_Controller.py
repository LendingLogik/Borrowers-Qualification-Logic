from Rules_using_XML import Rule_using_XML
from flask.views import MethodView
from flask import request
from preprocessing_of_data import PreprocessingOfData
import pandas as pd

def cast_value(value):
    try:
        # Try converting to integer
        return int(value)
    except ValueError:
        try:
            # If not integer, try converting to float
            return float(value)
        except ValueError:
            # If neither, return as string or handle special cases like dates
            return value



# Class responsible for handling XML-based loan interpretation using rule-based logic
class XML_File_Loan_Interpretation:
    rule_xml_approach = None  # Initialize a variable to store the rule-based XML approach

    def __init__(self):
        pass  # Constructor is not used here but is included for future extensibility
    
    @staticmethod
    def Instiate_XML_Rule(XML_file_path, XSD_file_path):
        """
        Static method to instantiate the Rule_using_XML class if the XML and XSD file paths are provided.
        
        Args:
            XML_file_path (str): Path to the XML file containing loan rules.
            XSD_file_path (str): Path to the XSD schema for XML validation.
        
        Returns:
            rule_xml_approach (Rule_using_XML): Instance of the Rule_using_XML class.
        """
        if (XML_file_path != "") and (XSD_file_path != ""):
            rule_xml_approach = Rule_using_XML(XML_file_path, XSD_file_path)
            return rule_xml_approach
    
    def Class_XML_node(self, Rule_Xml_approach, data):
        """
        Method to trigger the creation of rules using XML data provided.
        
        Args:
            Rule_Xml_approach: Instance of the Rule_using_XML class.
            data: Data to be processed for rule creation.
        """
        Rule_Xml_approach.create_rules_using_xml(data)

# Controller class for the Rule Engine that handles POST requests for XML-based rule evaluation
class Rule_Engine_XML_Controller(MethodView):
    methods = ["POST"]  # Define the supported HTTP method for this controller (POST only)

    def __init__(self):
        """
        Initialize the Rule_Engine_XML_Controller and instantiate the rule XML object
        for loan rule interpretation using the provided XML and XSD file paths.
        """
        self.XML_Loan_Interpretation_obj =  XML_File_Loan_Interpretation.Instiate_XML_Rule(
            "Lenders XML/output.xml", "Lenders XML/output.xsd"
        )

    def dispatch_request(self):
        """
        Handles incoming POST requests. Processes the client data, applies rule-based XML interpretation,
        and returns the evaluated loan rules.

        Returns:
            dict: The evaluated loan rules from the XML-based rule engine.
        """
        if request.method == "POST":
            # Extract the data from the request and preprocess it for rule evaluation
            data_from_client = request.json['body']
            # data_from_client = {key: [val] for key, val in data_from_client.items()}  # Convert to dictionary format
            
            # Cast each field's first element to the correct type
            for key, value in data_from_client.items():
                if key.endswith('date'):  # Check for date fields to convert to datetime
                    data_from_client[key] = [value] # pd.to_datetime(value[0])
                elif key == 'Primary__c' or key == 'usage_type':  # Handle boolean-like fields
                    data_from_client[key] = [value]
                else:
                    data_from_client[key] = [cast_value(value)]

            # Preprocess the client data for rule testing
            Preprocessed_data = PreprocessingOfData(data_from_client)
            Preprocessed_data.converting_df_to_dict()  # Convert DataFrame to dictionary
            Data_of_Rule_test = Preprocessed_data.Data_of_Rule_test  # Get processed data
            
            # Create and evaluate rules using the preprocessed data
            self.XML_Loan_Interpretation_obj.create_rules_using_xml(Data_of_Rule_test)
            
            # Return the lender rules after evaluation
            return self.XML_Loan_Interpretation_obj.lender_rules
        else:
            # If the request method is not POST, return an invalid request message
            return "Invalid Request Type for this Method"
