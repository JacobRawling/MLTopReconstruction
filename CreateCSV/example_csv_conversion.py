"""
    A simple example to convert an ATLAS AnalysisTop style output tree and save 
    it as a csv.
"""
from Root2CSV import TupleCSVConverter

# Example 
def add_custom_variables(reco_event,truth_event):
    """
        Example of adding custom variables to the csv - this is a dummy and returns the value of
        1.0 and the eventNumber twice for every event. 

        The objects passed to this function are the root2csv two TTrees. 

        This function MUST return an array 
    """
    return [1.0,reco_event.eventNumber,truth_event.eventNumber]

def create_custom_header():
    """        
        Example of adding custom variable header to the csv - this is a dummy and returns the value of
        a list with entries "dummy","reco_event_number", "truth_event_number"
    """
    return ["dummy","reco_event_number", "truth_event_number"]

def example_conversion():
    """
        Main entry point of the file, converts a typical tuple into the desired output.
    """
    csv_convertor = TupleCSVConverter(
                                     input_file = "test.root",
                                     tuple_name = "nominal",
                                     friend_tuple_name = "truth",
                                     output_folder = "",
                                     # List of boolean cuts
                                     cuts = ["(ejets_2015 || ejets_2016 || mujets_2016 || mujets_2015)"],
                                     # Example veariables for the detector tree
                                     variables = [
                                        "top_lep.Pt()",
                                        "top_lep.Eta()",
                                     ],
                                     # Example variables for the truth tree
                                     friend_variables = [
                                        "MC_b_from_tbar_pt",
                                        "MC_b_from_tbar_eta"
                                     ],
                                     # Add functions that will be called to create the header name
                                     # and evaluate the event level 
                                     add_custom_variables = add_custom_variables,
                                     create_custom_header = create_custom_header,
                                     index_variable = "eventNumber"
                                     )

    csv_convertor.create_csv(file_name = "test.csv")
    csv_convertor.convert()
    csv_convertor.close()

example_conversion()