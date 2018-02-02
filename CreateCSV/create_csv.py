""" 
    Converts a ROOT ntuple formatted in a way defined by internal ATLAS structures
    and outputs a CSV that can then be processed by pandas, R, etc.
"""

import settings as s
import ROOT as r


class TupleCSVConverter:
    def ___init__(
            self,
            input_file,
            detector_tuple_name,
            truth_tuple_name,
            output_folder,
            verbosity = 1
        )

        self.input_file          = input_file
        self.detector_tuple_name = detector_tuple_name
        self.truth_tuple_name    = truth_tuple_name
        self.output_folder       = output_folder

    def process_event(truth_event, reco_event):
        """
            For a given reco and truth event fill the CSV file that is currently ope n
        """
        pass

    def create_csv(self, file_name):
        """
            Opens a csv file and sets the headers
        """
        self.out_file = open(self.output_folder + file_name,"w+")


    def close(self):
        """
            Close the open csv file
        """
        self.out_file.close()

    def convert(self):
        """
            Reads over the root file and fill the csv file.
        """

    def log(self,message):
        if self.verbosity > 0:
            print (" [ CSV-CONVERTOR ] - " + message)
        
def main():
    """
        Main entry point of the file, converts a typical tuple into the desired output.
    """

    csv_convertor = TupleCSVConverter( s.input_file         
                                     s.detector_tuple_name
                                     s.truth_tuple_name   
                                     s.output_folder       )

    csv_convertor.create_csv(s.name)
    csv_convertor.convert()
    csv_convertor.close()

main()