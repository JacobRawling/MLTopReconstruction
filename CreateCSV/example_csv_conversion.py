"""
    A simple example to convert an ATLAS AnalysisTop style output tree and save 
    it as a csv 
"""
from Root2CSV import TupleCSVConverter

# Example 
def add_custom_variables(reco_event,truth_event):
    return [1.0]
def create_custom_header():
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
                                     cuts = ["(ejets_2015 || ejets_2016 || mujets_2016 || mujets_2015)"],
                                     truth_variables = [
                                        "MC_b_from_tbar_pt",
                                        "MC_b_from_tbar_eta"
                                     ],
                                     detector_variables = [
                                        "top_lep.Pt()",
                                        "top_lep.Eta()",
                                     ],
                                     add_custom_variables = add_custom_variables,
                                     create_custom_header = create_custom_header,
                                     )

    csv_convertor.create_csv("test.csv")
    csv_convertor.convert()
    csv_convertor.close()

example_conversion()