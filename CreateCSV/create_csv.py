""" 
    Converts a ROOT ntuple formatted in a way defined by internal ATLAS structures
    and outputs a CSV that can then be processed by pandas, R, etc.


"""

import settings as s
import ROOT as r

def open_file(file_name, option="READ" ):
    f = r.TFile(file_name,option)
    assert f, ("ERROR: failed to open file: ",file_name)
    return f

def clean_string(string):
    cleaned_string = string
    cleaned_string = cleaned_string.replace(".","_")
    cleaned_string = cleaned_string.replace("(","")
    cleaned_string = cleaned_string.replace(")","")
    return cleaned_string

class TupleCSVConverter:
    def __init__(
            self,
            input_file,
            detector_tuple_name,
            truth_tuple_name,
            output_folder,
            cuts = [""],
            truth_variables    = [""],
            detector_variables = [""],
            verbosity = 1
        ):
        """

        """
        self.input_file          = input_file
        self.detector_tuple_name = detector_tuple_name
        self.truth_tuple_name    = truth_tuple_name
        self.output_folder       = output_folder
        self.weight              = "1.0"
        self.verbosity           = verbosity
        self.truth_variables     = truth_variables
        self.detector_variables  = detector_variables
        # Allow for cuts given in a ROOT::TTreeFormula expression style
        for cut in cuts:
            self.weight += "*(" + cut +  ")"

    def process_event(self,truth_event, reco_event):
        """
            For a given reco and truth event fill the CSV file that is currently ope n
        """
        pass
        # Fill the top partonic information 

        # Fill the reco jet information 

        # Fill the leptonic W 

    def create_csv(self, file_name):
        """
            Opens a csv file and sets the headers
        """
        self.log("Created file: " +  self.output_folder + file_name)
        self.out_file = open(self.output_folder + file_name,"w+")
        assert not self.out_file.closed, (" FAILED TO OPEN FILE: "+  self.output_folder + file_name)
        self.file_name = file_name

        # Examine truth variables 
        for var in self.truth_variables:
            self.out_file.write(clean_string(var) )
            # Add a comma iff we are not the last item on this line 
            if var != self.truth_variables[-1] or len(self.detector_variables) > 0:
                self.out_file.write(", ")


        # Examine reconstruction level variables 
        for var in self.detector_variables:
            self.out_file.write(clean_string(var))
            # Add a comma iff we are not the last item on this line 
            if var != self.detector_variables[-1]:
                self.out_file.write(", ")

        self.out_file.write("\n")

    def close(self):
        """
            Close the open csv file
        """
        self.out_file.close()
        self.log( "Conversion successful.")
        self.log( "Output file: " + self.output_folder + self.file_name)

    def convert(self):
        """
            Reads over the root file and fill the csv file.
        """
        # Read the root file 
        in_file = open_file(self.input_file, "READ")

        # Get the tuples and synchronise them across eventNubers
        reco_tree  = in_file.Get(self.detector_tuple_name)
        truth_tree = in_file.Get(self.truth_tuple_name)

        # Very costly for large files
        reco_tree.BuildIndex('eventNumber')
        truth_tree.BuildIndex('eventNumber')

        # Construct the weight based upon the reco_cuts:
        weight_formula   = r.TTreeFormula("weight_formula", self.weight, reco_tree)

        # Create TTRee::Formulas for variables given as contsructors to save 
        reco_formulae = []
        for var in self.detector_variables:
            reco_formulae.append(r.TTreeFormula(var, var, reco_tree))

        truth_formulae = []
        for var in self.truth_variables:
            reco_formulae.append(r.TTreeFormula(var, var, truth_tree))

        for event in reco_tree:
            index = reco_tree.GetEntryNumberWithIndex(event.eventNumber)
            truth_tree.GetEntry(index)

            # Reject events that fail the cuts
            weight  = weight_formula.EvalInstance()
            if weight < 1.0:
                continue

            # Also allow for a more complicated analysis of eents 
            self.process_event(event, truth_tree)

            for formula in truth_formulae:
                self.out_file.write( str(formula.EvalInstance()))
                if formula != truth_formulae[-1] or len(reco_formulae) > 0:
                    self.out_file.write( ", ")



            for formula in reco_formulae:
                self.out_file.write( str(formula.EvalInstance()))
                if formula != reco_formulae[-1]:
                    self.out_file.write( ", ") 
            self.out_file.write("\n") 


        # Clean up the root file
        in_file.Close()

    def log(self,message):
        if self.verbosity > 0:
            print (" [ CSV-CONVERTOR ] - " + message)

def example_conversion():
    """
        Main entry point of the file, converts a typical tuple into the desired output.
    """
    csv_convertor = TupleCSVConverter(
                                     s.input_file,
                                     s.detector_tuple_name,
                                     s.truth_tuple_name,
                                     s.output_folder,
                                     cuts = ["(ejets_2015 || ejets_2016 || mujets_2016 || mujets_2015)"],
                                     truth_variables = [
                                        "MC_b_from_tbar_pt",
                                        "MC_b_from_tbar_eta"
                                     ],
                                     detector_variables = [
                                        "top_lep.Pt()",
                                        "top_lep.Eta()",
                                     ]
                                     )

    csv_convertor.create_csv(s.name)
    csv_convertor.convert()
    csv_convertor.close()

example_conversion()