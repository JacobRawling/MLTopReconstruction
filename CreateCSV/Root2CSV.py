""" 
    Converts a ROOT file with up to two tuples into a tuple. 

    Works with TTreeFormula class to allow a user to input a list of variable names to save. Also has support 
    for abitrarily complicated variables to be with user defined evaluation of an event returing an array of 
    variables to save in the csv. 

    Aimed at users wishing to processess ROOT events with pandas or any other common data analysis framework that 
    works with csv but not the ROOT format.

    NOTE: root has excellent compression, so expect file size to grow substantially with this tool
"""
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
            truth_variables    = [],
            detector_variables = [],
            verbosity = 1,
            create_custom_header= None,
            add_custom_variables= None,
            weight              = "1.0",
            index_variable      = None
        ):
        """ 
            Converts a TTree to a csv file 

            input_file:           Root file input path 
            detector_tuple_name:  name of the first tuple in the root file 
            truth_tuple_name:     name of a second tuple in the file
            output_folder:        location that the csv will be saved to
            cuts:                 A list of cuts for the reco events 
            truth_variables:      A list of strings that can be evaluate upon the truth tuple
            detector_variables:   A list of strings that can be evaluated upon the detector tuple
            verbosity:            How much output this tool will display 
            create_custom_header: Function that can be override ti create a custom set of headers, must return an array of 
                                  strings
            add_custom_variables: Function that takes reco_tree and truth_tree as inputs, and returns an array of numbers
                                  that will be saved to the csv file 
        """
        self.input_file          = input_file
        self.detector_tuple_name = detector_tuple_name
        self.truth_tuple_name    = truth_tuple_name
        self.output_folder       = output_folder
        self.weight              = weight
        self.index_variable      = index_variable
        self.verbosity           = verbosity
        self.truth_variables     = truth_variables
        self.detector_variables  = detector_variables
        # Allow for cuts given in a ROOT::TTreeFormula expression style
        for cut in cuts:
            self.weight += "*(" + cut +  ")"

        self.create_custom_header = create_custom_header
        self.add_custom_variables = add_custom_variables

    def create_csv(self, file_name):
        """
            Opens a csv file and sets the headers
        """
        self.log("Created file: " +  self.output_folder + file_name)
        self.out_file = open(self.output_folder + file_name,"w+")
        assert not self.out_file.closed, (" FAILED TO OPEN FILE: "+  self.output_folder + file_name)
        self.file_name = file_name

        if self.create_custom_header != None:        
            headers = self.create_custom_header()
            for header in headers:
                self.out_file.write(header)
                if header != headers[-1] or len(self.truth_variables) > 0 or len(self.detector_variables) > 0:
                    self.out_file.write(", ")

        # Examine truth variables if we are looking at this tuple
        if self.index_variable != None:
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

        # Only read the truth tree if it's defined
        if self.index_variable != None:
            truth_tree = in_file.Get(self.truth_tuple_name)
        else:
            truth_tree = None

        # Very costly for large files
        if self.index_variable != None:
            reco_tree.BuildIndex(self.index_variable)
            truth_tree.BuildIndex(self.index_variable)

        # Construct the weight based upon the reco_cuts:
        weight_formula   = r.TTreeFormula("weight_formula", self.weight, reco_tree)

        # Create TTRee::Formulas for variables given as contsructors to save 
        reco_formulae = []
        for var in self.detector_variables:
            reco_formulae.append(r.TTreeFormula(var, var, reco_tree))

        truth_formulae = []
        if self.index_variable != None:
           for var in self.truth_variables:
               reco_formulae.append(r.TTreeFormula(var, var, truth_tree))

        for event in reco_tree:
            index = reco_tree.GetEntryNumberWithIndex(event.eventNumber)
            # Also read the truth level variable if we are trying to synchronise across two trees
            if self.index_variable != None:
                truth_tree.GetEntry(index)

            # Reject events that fail the cuts
            weight  = weight_formula.EvalInstance()
            if weight < 1.0:
                continue

            # Also allow for a more complicated analysis of eents 
            if self.add_custom_variables != None:
                custom_vars = self.add_custom_variables(event, truth_tree)
                # Save these to the file 
                for var in custom_vars:
                   self.out_file.write(str(var))
                   if var != custom_vars[-1] or len(truth_formulae) > 0 or len(reco_formulae) > 0:
                       self.out_file.write(",")

            if self.index_variable != None:
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
        """
            Prints a message depending on the verbosity of this tool
        """
        if self.verbosity > 0:
            print (" [ CSV-CONVERTOR ] - " + message)