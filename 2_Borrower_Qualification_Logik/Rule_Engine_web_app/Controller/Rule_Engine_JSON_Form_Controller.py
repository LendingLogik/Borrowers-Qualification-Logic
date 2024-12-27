# Not written the comments yet because I think this controller needs more improvements
from flask.views import MethodView
from flask import Flask, jsonify, request
from preprocessing_of_data import PreprocessingOfData
from flask import  render_template
import secrets # To generate unique application numbers
from Rules_using_JSON import  Rules_using_JSON
import copy

# Dictionary defining the rules for different lenders
LenderRules = {
    "Flexi"  : [ 'Primary Flexi_up_to_20K', 'Primary Flexi_from_20_50K', 'Primary Flexi_50_300K', 'Secondary Flexi_upto_20K',  'Secondary Flexi_from_20_50K', 'Secondary Flexi_50_300K', 'Tertiary Flexi_upto_20K', 'Tertiary Flexi_from_20_50K',  'Tertiary Flexi_50_300K'],
    "Pepper"  : ['Primary Pepper_Tier_A', 'Primary Pepper_Tier_B', 'Primary Pepper_Tier_C',  'Secondary Pepper_Tier_A',  'Secondary Pepper_Tier_B', 'Tertiary Pepper_Tier_A', 'Tertiary Pepper_Tier_B'],
    "Resimac" : [ 'Primary Resimac- light doc', 'Primary Resimac- low doc',  'Secondary Resimac- low doc',  'Secondary Resimac- light doc', 'Tertiary Resimac- light doc',  'Tertiary Resimac- low doc']
}

# Controller to handle requests related to the Rule Engine using JSON Form input
class Rule_Engine_JSON_Form_Controller(MethodView):

    def get(self):
        """
            Handle GET requests to serve the HTML form for input.
            
            Returns:
                HTML template: The form where the user can input data for rule processing.
        """
        return render_template('App/index.html')

    def post(self):
        """
            Handle POST requests for processing form data submitted by the user.
            
            - Extracts form data from the request.
            - Preprocesses the data.
            - Applies rule evaluation logic using JSON rules.
            
            Returns:
                dict: Remarks generated based on the rule evaluation.
        """
        if request.method == "POST":
            # Extract data from the form submission
            amount_financed         = request.form.get('amount_financed')
            deposit_amount          = request.form.get('deposit_amount')
            balloon_amount          = request.form.get('balloon_amount')
            repayment_term_month    = request.form.get('repayment_term_month')
            applicant_entity_type   = request.form.get('applicant_entity_type')
            asset_supplier_type     = request.form.get('asset_supplier_type')
            asset_category          = request.form.get('asset_category')
            asset_type              = request.form.get('asset_type')
            asset_manufacture_year  = request.form.get('asset_manufacture_year')
            usage_type              = request.form.get('usage_type')
            gst_registered_date     = request.form.get('gst_registered_date')
            abn_registered_date     = request.form.get('abn_registered_date')
            guarantor_1_residential_status = request.form.get('guarantor_1_residential_status')
            
            # Create a dictionary containing the client's data to be used for rule evaluation
            ClientData = {
            'application_number':[secrets.token_hex(8)],  # Generate a unique application number
            'amount_financed': [amount_financed],
            'deposit_amount': [deposit_amount],
            'balloon_amount': [balloon_amount],
            'repayment_term_month': [repayment_term_month],
            'applicant_entity_type': [applicant_entity_type],
            'asset_supplier_type': [asset_supplier_type],
            'asset_category': [asset_category],
            'asset_type': [asset_type],
            'asset_manufacture_year': [asset_manufacture_year],
            'usage_type': [usage_type],
            'gst_registered_date': [gst_registered_date],
            'abn_registered_date': [abn_registered_date],
            'guarantor_1_residential_status': [guarantor_1_residential_status]
        }
        # Preprocess the data before passing it to the rule engine
        Preprocessed_data = PreprocessingOfData(ClientData)
        Preprocessed_data.converting_df_to_dict()
        Data_of_Rule_test = Preprocessed_data.Data_of_Rule_test
        
        # Check for right usage:
        #   - approach = rule-engine
        #   - approach = if-statements

        

        # Initialize the rule engine using JSON-based rules
        Rules_by_Lender  = Rules_using_JSON('Rules.Json')
        Rules_by_Lender.Create_rules_using_json()
        # Retrieve the remarks generated based on the rule evaluation
        Remarks = Rules_by_Lender.Remarks
        for Data_rule in Data_of_Rule_test:

            #Dictionary which will be jsonify for the User Interface
            TempDict = {"Flexi":{},'Pepper':{},"Resimac":{}} 

            for LenderName,LenderRule in Rules_by_Lender.lender_rules.items():
                LendrName = ""
                for Key,Val in LenderRules.items():
                    if LenderName.upper().find(Key.upper()) != -1:
                        if LenderName in Val:
                            LendrName = Key

                if not Preprocessed_data.Asset_category_classification(Data_rule['asset_type'], LendrName, LenderName.split(" ")[0]):
                    continue
                #Checking only for the specific asset category
                # if LenderName.upper().find(Data_rule['asset_category'].split("_")[0]) == -1:
                #     continue
                
                #Giving requried Json format to dictionary  
                # Example { "Pepper": { "Primary Pepper_Tier_A" : { rule : {rule result : true , remark : "reason for true or false" }, eligibility : true}} }
                if "Pepper" in LenderName:
                    lender = 'Pepper'
                    TempDict[lender][LenderName] = {}
                elif "Resimac" in LenderName:
                    lender = 'Resimac'
                    TempDict[lender][LenderName] = {}
                else :
                    lender = 'Flexi'
                    TempDict[lender][LenderName] = {}

                temppte = copy.deepcopy(LenderRule)
                remarks = ""
                Running_logs = ""
                while temppte!=None:
                    Rule_evaluate = temppte.Rule.evaluate(Data_rule)
                    Running_logs = Running_logs + " -- " + Rule_evaluate['Remark']  if Running_logs!="" else Rule_evaluate['Remark']
                    TempDict[lender][LenderName][ temppte.RC_ID] = {}
                    EATD = temppte.take_decisions(temppte.Rule)
                    if temppte.Rule.Is_Evaluating:
                        TempDict[lender][LenderName][temppte.RC_ID]["RC_Result"] = Rule_evaluate['Return_result']   # Rule Condition Result
                    else:
                        TempDict[lender][LenderName][temppte.RC_ID]["RC_Result"] = True
                    TempDict[lender][LenderName][temppte.RC_ID]["Remark"] = Rule_evaluate['Remark']
                    if not EATD :
                        break
                    temppte = temppte.next_Rule
                # if temppte is none , it means all rules are passed 
                if temppte == None:
                    TempDict[lender][LenderName]['Eligibility'] = True
                    # Data_rule['Evaluated_Lender'] = LenderName
                
                else:
                    TempDict[lender][LenderName]['Eligibility'] = False
                    # Data_rule['Evaluated_Lender'] = "No Lender Found!"
        return jsonify(TempDict)
