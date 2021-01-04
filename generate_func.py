##===========================================================================================
##
## Class declaration
##
##===========================================================================================

class SkeletalSFactors:
    """ Class containing S-factors for skeletal sites using the phantoms 
        described in 
        
        Hough et al. 2011 (doi: 10.1088/0031-9155/56/8/001
        O'Reilly et al. 2016 (doi: 10.1088/1361-6560/61/24/8794)

        With the energy spectrum of 177-Lu as described in

        ICRP 107 2008 (doi: 10.1016/j.icrp.2008.10.004)

        Spread-sheet with the values are found in the utils-directory:

        utils/decdataenergies.xlsx
        utils/saf_values_female_redone.xlsx
        utils/saf_values_male_redone.xlsx
        
        """
    
    def __init__(self, 
                 isotopename, 
                 phantomsex, 
                 saf_file,
                 isotope_file):
        
        self.isotopename = isotopename
        self.phantomsex = phantomsex
        self.saf_file = saf_file
        self.isotope_file = isotope_file
        
        # Produce the skeletal-factors when initiated, 
        
        (self.skeletalfactors, 
                self.icrp_cf_vals, 
                self.trabecular_corrections) = self.create_s_factors_from_xlsx()

    def add_absorbed_dose_to_pandaframe(self, 
            data_frame):
        """
        Takes a pandas-frame as input, together with the parameters needed to
        run the calculate_dose function and tacks on the absorbed dose in a
        named extra column, then returns the frame with the extra column
        """

        # Take the needed values from the data-frame:

        index_in_frame = 0 # For looping over the frame

        mass_input = data_frame["Mass"][cf_stringc]


    def calculate_dose(self, mass, cumulative_activity, cf_string, site_name):

        """
        Function to calculate the absorbed dose from some input. Input should be
        the name of the site used, made to match the phantom site names.
        Cumulative activity are put in in the units of Bq-s, and the mass of the
        marrow space should be grams. A CF-factor is put in in the form of a string
        on the form "CFXX" or "CFXXX" or "ICRP"

        Parameter list:

        mass: The mass of the marrow space in g
        cumulative_activity: The cumulative activity in the marrow 
        cf_string: Desired cellularity factor in the form "CFXX" where XX is a value in 10-increments between 10 and 100
        site_name: String containing the name of the skeletal site. The string have to match the names given in the creation
                   of the phantom class element
        """

        # First get the correction factor from the site_name
        tbc_c = ((self.trabecular_corrections)[site_name][0])
        
        # Handle the ICRP-case for cellularity:
        if cf_string == "ICRP":
            cf_value = self.icrp_cf_vals[site_name]
        else:
            cf_value = float(cf_string[2::])/100.0

        assert cf_value <0.999 or cf_value > 0.001

        # Now adjust the mass
        mass_of_marrow = (MASS_DENSITY*mass/1.0e3)*cf_value*(1-tbc_c)

        # Calculate the energy stemming from the cumulative activity
        E_per_desintegration = (((self.skeletalfactors)[site_name])["EnergyPerDesintegration"][cf_string])
        E = cumulative_activity*ENERGY_J_PER_MEV*E_per_desintegration

        absorbed_dose = (E/mass_of_marrow)

        return absorbed_dose
        
    def print_all(self):
        print("This is a class containing")
        print(self.isotopename)
        print("Patient sex: " + self.phantomsex)
        print("An the following factors:")
        print(self.skeletalfactors)
        print("End of print")
        
    def create_s_factors_from_xlsx(self):

        """
        Function to create the skeletal phantom class used by this program to calculate 
        absorbed dose in skeletal sites. Return value is a class object.
        Input are .xlsx-files containing the required data.
        
        Units for the CFs are strings declaring the percentage, i.e. 80CF or CF80
        Units for the energy-factors are MeV per disintegration

        Changes needed: 
        1) Naming
        2) 
        
        """

        verbose = False # For debugging - TODO: Remove or put into the function-call

        # Import the saf-file as a regular xlsx-file. 
        # This uses an .xlsx-reader as the data
        # are distributed across different sheets.

        main_wb = openpyxl.load_workbook(filename=self.saf_file)
        sheet_names = main_wb.sheetnames
        
        # Remove unwanted sheets
        non_organ_sheets = ["Tissue-AM-Masses"]
        site_list = sheet_names
        
        for s in non_organ_sheets:
            if s in site_list: site_list.remove(s)
        
        mass_data = pd.read_excel(self.saf_file, sheet_name="Tissue-AM-Masses")

        if verbose:
            list_of_sites_in_mass_file = (mass_data["SiteName"].values)
        
            for organ in site_list:
                if organ in list_of_sites_in_mass_file:
                    print("Organ " + organ + " is in list")
                else:
                    print("Warning, names might mis-match " + organ)

        # The SAF-values are translated to panda-frames. 
        # First one large frame. This large frame get
        # shopped up into smaller frames, and saved
        # as a dict

        SFactorFrame = pd.DataFrame()

        num_of_cfs = 11 # Each skeletal site have 11 different CFs, including the ICRP-value
        SFactorFrameLen = len(site_list)*num_of_cfs 
        
        SFactorFrame["EnergyPerDesintegration"] = np.zeros(SFactorFrameLen)
        SFactorFrame["CFs"] = np.zeros(SFactorFrameLen)
        SFactorFrame["SiteName"] = np.zeros(SFactorFrameLen)
        
        res_index = 0
        
        CF_vector = np.array([0.1, 0.2, 
                                0.3, 0.4, 
                                0.5, 0.6, 
                                0.7, 0.8, 
                                0.9, 1.0, -1])  # ICRP-value is coded as -1.

        # Before the organ-loop, retreive the energy-spectrum:
        energies = pd.read_excel(self.isotope_file, 
                                sheet_name="AllElectrons")
        len_of_table = len(energies)
            
        energy_absorbtion_frame = pd.DataFrame(columns=["Energy", "Y", "phi"], 
                index=np.arange(len_of_table))

        energy_absorbtion_frame["Energy"] = energies["E (MeV)"]
        energy_absorbtion_frame["Y"] = energies["Y (/nt)"]

        for organ in site_list:
            if verbose:
                print(organ)
            
            mass_value = mass_data[mass_data["SiteName"] == organ]["AM-in-MST-100-CF"].values[0]
            ICRP_CF = mass_data[mass_data["SiteName"] == organ]["ICRP-CF"].values[0]/1.0e2

            organ_saf_values = pd.read_excel(self.saf_file, sheet_name=organ)
            energy_look_up_vector = organ_saf_values["Energy"].values

            for cf in CF_vector:
                if cf == -1:
                    cf = ICRP_CF
                    CF_string = "ICRP"
                        
                    for i in range(len_of_table):
                        energy_to_look_up = (energy_absorbtion_frame.at[i, "Energy"])
                        index = (np.abs(energy_look_up_vector-energy_to_look_up)).argmin()
                        phi = (organ_saf_values.at[index, CF_string])*mass_value*cf
                        energy_absorbtion_frame.at[i, "phi"] = phi
                    
                    energy_per_desintegration = (np.sum(energy_absorbtion_frame["Energy"]* \
                    energy_absorbtion_frame["Y"]*energy_absorbtion_frame["phi"]))
                        
                    if verbose:
                        print(organ, cf, energy_per_desintegration, res_index)

                    SFactorFrame.loc[res_index,("EnergyPerDesintegration")] = energy_per_desintegration
                    SFactorFrame.loc[res_index,("CFs")] = CF_string
                    SFactorFrame.loc[res_index,("SiteName")] = organ
                    res_index = res_index + 1
                        
                else:

                    CF_string = ("CF" + str(int(cf*100)))

                    for i in range(len_of_table):
                        energy_to_look_up = (energy_absorbtion_frame.at[i, "Energy"])
                        index = (np.abs(energy_look_up_vector-energy_to_look_up)).argmin()
                        phi = (organ_saf_values.at[index, CF_string])*mass_value*cf
                        energy_absorbtion_frame.at[i, "phi"] = phi
            
                    energy_per_desintegration = (np.sum(energy_absorbtion_frame["Energy"]* \
                    energy_absorbtion_frame["Y"]*energy_absorbtion_frame["phi"]))
            
                    if verbose:
                        print(organ, cf, energy_per_desintegration, res_index)

                    SFactorFrame.loc[res_index,("EnergyPerDesintegration")] = energy_per_desintegration
                    SFactorFrame.loc[res_index,("CFs")] = CF_string
                    SFactorFrame.loc[res_index,("SiteName")] = organ
                    res_index = res_index + 1

        # Make the class-objects from the generated pandas

        # Set a dict for the individual frames
        
        skeletalsites = {}
        CF_ICRP_values = {}
        tbv_fractions = {}
        
        for site in site_list:
            tmp_frame = (SFactorFrame[SFactorFrame["SiteName"]==site])
            tmp_frame = tmp_frame.set_index("CFs")
            
            ICRP_CF = mass_data[mass_data["SiteName"] == site]["ICRP-CF"].values[0]/1.0e2
            tbv_correction = mass_data[mass_data["SiteName"] == site]["TBV-fraction"].values
            
            skeletalsites[site] = tmp_frame
            CF_ICRP_values[site] = ICRP_CF
            tbv_fractions[site] = tbv_correction

        return(skeletalsites, CF_ICRP_values, tbv_fractions)

##===========================================================================================
##
## Global constants
##
##===========================================================================================

# Energy in J per MeV 
ENERGY_J_PER_MEV = 1.60217662e-13

# Mass density of the marrow

MASS_DENSITY = 1.0 # Could also be set to 1.03

##===========================================================================================
##
## Main part for testing
##
##===========================================================================================

print("Loading module...")

import numpy as np
import pandas as pd
import openpyxl

# Make a dummy-run to check for assertion errors

dummy_skeletal = SkeletalSFactors(isotopename = "177-Lu",
	phantomsex = "M",
	saf_file = "utils/saf_values_male_redone.xlsx",
        isotope_file = "utils/decdataenergies.xlsx")

print("Loaded")

