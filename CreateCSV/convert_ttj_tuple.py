"""
	Converts an AnalysisTop stlye output file from a ROOT file to a Tuple 
    Takes ~1m to conver 13million events.
"""

import settings as s
import ROOT as r
from Root2CSV import TupleCSVConverter

def add_custom_variables(reco_event,truth_event):
    """
        Example of adding custom variables to the csv - this is a dummy and returns the value of
        1.o for every event. 

        The objects passed to this function are two TTrees. 

        This function MUST return an array 
    """
    
    # Find the leptonic and hadronic tops at parton level as four vectors 
    if tbar_is_leptonic(reco_event, truth_event):
        # Now we know that the bbar must match to leptonic b-jet   
        leptonic_t = r.TLorentzVector() 
        leptonic_t.SetPtEtaPhiM(truth_event.MC_tbar_afterFSR_pt,
                                truth_event.MC_tbar_afterFSR_eta,
                                truth_event.MC_tbar_afterFSR_phi,
                                truth_event.MC_tbar_afterFSR_m
                            )
        hadronic_t = r.TLorentzVector() 
        hadronic_t.SetPtEtaPhiM(truth_event.MC_t_afterFSR_pt,
                                truth_event.MC_t_afterFSR_eta,
                                truth_event.MC_t_afterFSR_phi,
                                truth_event.MC_t_afterFSR_m
                            )
        hadronic_W = r.TLorentzVector() 
        hadronic_W.SetPtEtaPhiM(truth_event.MC_W_from_t_pt,
                                truth_event.MC_W_from_t_eta,
                                truth_event.MC_W_from_t_phi,
                                truth_event.MC_W_from_t_m
                            )

    else:
        # Swap them round if the top is the leptonic 
        hadronic_t = r.TLorentzVector() 
        hadronic_t.SetPtEtaPhiM(truth_event.MC_tbar_afterFSR_pt,
                                truth_event.MC_tbar_afterFSR_eta,
                                truth_event.MC_tbar_afterFSR_phi,
                                truth_event.MC_tbar_afterFSR_m
                            )
        leptonic_t = r.TLorentzVector() 
        leptonic_t.SetPtEtaPhiM(truth_event.MC_t_afterFSR_pt,
                                truth_event.MC_t_afterFSR_eta,
                                truth_event.MC_t_afterFSR_phi,
                                truth_event.MC_t_afterFSR_m
                        )
        hadronic_W = r.TLorentzVector() 
        hadronic_W.SetPtEtaPhiM(truth_event.MC_W_from_tbar_pt,
                                truth_event.MC_W_from_tbar_eta,
                                truth_event.MC_W_from_tbar_phi,
                                truth_event.MC_W_from_tbar_m)

    # Now lets save the jets
    jet_vars = []
    for i in xrange(len(reco_event.jet_pt)):
        #we only wish to store 5 jets 
        if len(jet_vars)/4 >=3:
            break

        if ord(reco_event.jet_isbtagged_MV2c10_85[i]  ) != 1:
            jet = r.TLorentzVector() 
            jet.SetPtEtaPhiM(
                        reco_event.jet_pt[i] ,
                        reco_event.jet_eta[i],
                        reco_event.jet_phi[i],
                        reco_event.jet_e[i] )
            jet_vars.append(jet.Px()) 
            jet_vars.append(jet.Py())
            jet_vars.append(jet.Pz())
            jet_vars.append(jet.E ())

    return [
            leptonic_t.Px(),
            leptonic_t.Py(),
            leptonic_t.Pz(),
            leptonic_t.E(),
            hadronic_t.Px(),
            hadronic_t.Py(),
            hadronic_t.Pz(),
            hadronic_t.E(),
            hadronic_W.Px(),
            hadronic_W.Py(),
            hadronic_W.Pz(),
            hadronic_W.E()
            ]+jet_vars

def create_custom_header():
    """        
        Adds the header to the csv for all top quarks and W bosons
    """
    return ["parton_t_lep_Px",
            "parton_t_lep_Py",
            "parton_t_lep_Pz",
            "parton_t_lep_E",
            "parton_t_had_Px",
            "parton_t_had_Py",
            "parton_t_had_Pz",
            "parton_t_had_E",
            "parton_W_had_Px",
            "parton_W_had_Py",
            "parton_W_had_Pz",
            "parton_W_had_E",
            "jet1_Px",
            "jet1_Py",
            "jet1_Pz",
            "jet1_E",
            "jet2_Px",
            "jet2_Py",
            "jet2_Pz",
            "jet2_E",
            "jet3_Px",
            "jet3_Py",
            "jet3_Pz",
            "jet3_E",
            ]

def tbar_is_leptonic(reco_event, truth_event):
    """
        Determines whether tbar in the event is leptonic, or if it's hadronic 
        Does this by checking the sign of the charge lepton in the event.
        The charge of the lepton is NEGATVIE then the tbar is the leptonic top
            tbar > W-b > l-nub 
    
    """
    # Evaluate which lepton's charge to evaluate
    if len(reco_event.el_pt) > 0:
        return reco_event.el_charge[0] < 0
    else:
        return reco_event.mu_charge[0] < 0

def main():
    """
        Main entry point of the file, converts a typical tuple into the desired output.
    """
    csv_convertor = TupleCSVConverter(
                                     input_file = s.input_file,
                                     tuple_name = "nominal",
                                     friend_tuple_name = "truth",
                                     output_folder = "../in/",
                                     # List of boolean cuts
                                     cuts = ["(ejets_2015 || ejets_2016 || mujets_2016 || mujets_2015)"],
                                     # Example veariables for the detector tree
                                     variables = [
                                        # Top quark reco variables
                                        "top_lep.Px()",
                                        "top_lep.Py()",
                                        "top_lep.Pz()",
                                        "top_lep.E()",

                                        "top_had.Px()",
                                        "top_had.Py()",
                                        "top_had.Pz()",
                                        "top_had.E()",
                                        # # b-quarks currently assigned 
                                        "b_lep.Px()",
                                        "b_lep.Py()",
                                        "b_lep.Pz()",
                                        "b_lep.E()",
                                        "b_had.Px()",
                                        "b_had.Py()",
                                        "b_had.Pz()",
                                        "b_had.E()",

                                        "W_lep.Px()",
                                        "W_lep.Py()",
                                        "W_lep.Pz()",
                                        "W_lep.E()",
                                     ],
                                     # Truth tree does not store objects as leptonic vs hadronic 
                                     # So use custom functions to do this 
                                     friend_variables = [ ],
                                     # Add functions that will be called to create the header name
                                     # and evaluate the event level 
                                     add_custom_variables = add_custom_variables,
                                     create_custom_header = create_custom_header,
                                     index_variable = "eventNumber"
                                     )

    csv_convertor.create_csv(s.output_file_name )
    csv_convertor.convert()
    csv_convertor.close()
main()