"""
    A simple example to convert an ATLAS AnalysisTop style output tree and save 
    it as a csv.
"""
from Root2CSV import TupleCSVConverter

# Example 
def add_custom_variables(reco_event,truth_event):
    """
        Example of adding custom variables to the csv - this is a dummy and returns the value of
        1.o for every event. 

        The objects passed to this function are two TTrees. 

        This function MUST return an array 
    """
    return [1.0]

def create_custom_header():
    """        
        Example of adding custom variable header to the csv - this is a dummy and returns the value of
        a list with one entry ["dummy"]
    """
    return ["dummy"]

def example_conversion():
    """
        Main entry point of the file, converts a typical tuple into the desired output.
    """
    csv_convertor = TupleCSVConverter(
                                     "test.root",
                                     "nominal",
                                     "truth",
                                     "",
                                     # List of boolean cuts
                                     cuts = ["(ejets_2015 || ejets_2016 || mujets_2016 || mujets_2015)"],
                                     # Example variables for the truth tree
                                     truth_variables = [
                                        "MC_b_from_tbar_pt",
                                        "MC_b_from_tbar_eta"
                                     ],
                                     # Example veariables for the detector tree
                                     detector_variables = [
                                        "top_lep.Pt()",
                                        "top_lep.Eta()",
                                     ],
                                     # Add functions that will be called to create the header name
                                     # and evaluate the event level 
                                     add_custom_variables = add_custom_variables,
                                     create_custom_header = create_custom_header,
                                     )

    csv_convertor.create_csv("test.csv")
    csv_convertor.convert()
    csv_convertor.close()

example_conversion()