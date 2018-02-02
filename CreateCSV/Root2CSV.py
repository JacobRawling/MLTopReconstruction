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

def open_file(file_name, option="READ"):
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
            tuple_name,
            friend_tuple_name,
            output_folder,
            cuts = [],
            variables = [],
            friend_variables    = [],
            verbosity = 1,
            create_custom_header= None,
            add_custom_variables= None,
            index_variable      = None
        ):
        """ 
            Converts a TTree to a csv file 

            input_file:           Root file input path 
            tuple_name:           name of the first tuple in the root file 
            friend_tuple_name:    name of a second tuple in the file
            output_folder:        Location that the csv will be saved to
            cuts:                 A list of cuts for the reco events 
            friend_variables:     A list of strings that can be evaluate upon the truth tuple
            variables:            A list of strings that can be evaluated upon the detector tuple
            verbosity:            How much output this tool will display 

            create_custom_header: Function that can be override to create a custom set of headers, must return an array of 
                                  strings 
            add_custom_variables: Function that takes the tree and friend_tree as inputs, and returns an array of numbers
                                  that will be saved to the csv file - allows for complicated functions that depend on 
                                  either or both trees to be evaluated. See example_csv_conversion.py for an example 
                                  implementation.
        """
        self.input_file           = input_file
        self.tuple_name           = tuple_name
        self.friend_tuple_name    = friend_tuple_name
        self.output_folder        = output_folder
        self.index_variable       = index_variable
        self.verbosity            = verbosity
        self.friend_variables     = friend_variables
        self.variables            = variables

        # Allow for cuts given in a ROOT::TTreeFormula expression style
        self.selection            = "1.0"
        for cut in cuts:
            self.selection += "*(" + cut +  ")"

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
                if header != headers[-1] or len(self.friend_variables) > 0 or len(self.variables) > 0:
                    self.out_file.write(", ")

        # Examine truth variables if we are looking at this tuple
        if self.index_variable != None:
            for var in self.friend_variables:
                self.out_file.write(clean_string(var) )
                # Add a comma iff we are not the last item on this line 
                if var != self.friend_variables[-1] or len(self.variables) > 0:
                    self.out_file.write(", ")

        # Examine reconstruction level variables 
        for var in self.variables:
            self.out_file.write(clean_string(var))
            # Add a comma iff we are not the last item on this line 
            if var != self.variables[-1]:
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
        tree  = in_file.Get(self.tuple_name)

        # Only read the truth tree if it's defined
        if self.index_variable != None:
            friend_tree = in_file.Get(self.friend_tuple_name)
        else:
            friend_tree = None

        # Very costly for large files
        if self.index_variable != None:
            tree.BuildIndex(self.index_variable)
            friend_tree.BuildIndex(self.index_variable)

        # Construct the weight based upon the cuts:
        weight_formula   = r.TTreeFormula("weight_formula", self.selection, tree)

        # Create TTRee::Formulas for variables given as contsructors to save 
        formulae = []
        for var in self.variables:
            formulae.append(r.TTreeFormula(var, var, tree))

        friend_formulae = []
        if self.index_variable != None:
           for var in self.friend_variables:
               formulae.append(r.TTreeFormula(var, var, friend_tree))

        for event in tree:
            index = tree.GetEntryNumberWithIndex(event.eventNumber)
            # Also read the truth level variable if we are trying to synchronise across two trees
            if self.index_variable != None:
                friend_tree.GetEntry(index)

            # Reject events that fail the cuts
            weight  = weight_formula.EvalInstance()
            if weight < 1.0:
                continue

            # Also allow for a more complicated analysis of eents 
            if self.add_custom_variables != None:
                custom_vars = self.add_custom_variables(event, friend_tree)
                # Save these to the file 
                for var in custom_vars:
                   self.out_file.write(str(var))
                   if var != custom_vars[-1] or len(friend_formulae) > 0 or len(formulae) > 0:
                       self.out_file.write(",")

            # Save the friend tree variables first 
            if self.index_variable != None:
                for formula in friend_formulae:
                    self.out_file.write( str(formula.EvalInstance()))
                    if formula != friend_formulae[-1] or len(formulae) > 0:
                        self.out_file.write( ", ")

            # Now save the main TTrees variables that we desire
            for formula in formulae:
                self.out_file.write( str(formula.EvalInstance()))
                if formula != formulae[-1]:
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