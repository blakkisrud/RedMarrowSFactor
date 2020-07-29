def create_skeletal_phantom(saf_file_path, 
                            isotope_data_path,
                            verbose = False):
    """
    Function to create the skeletal phantom class used by this program to calculate 
    absorbed dose in skeletal sites. Return value is a class object.
    Input are .xlsx-files containing the required data.
    
    This function might be written into the class definition itself

    Units for the CFs are strings declaring the percentage, i.e. 80CF or CF80
    Units for the energy-factors are MeV per disintegration

    Changes needed: 
    1) Naming, some are misleading
    2) 
    
    """

    # Import the saf-file as a regular xlsx-file. 
    # This uses an .xlsx-reader as the data
    # are distributed across different sheets.

    main_wb = openpyxl.load_workbook(filename=saf_file_path)
    sheet_names = main_wb.sheetnames

    # Remove unwanted sheets
    non_organ_sheets = ["Tissue-AM-Masses"]
    site_list = sheet_names
    
    for s in non_organ_sheets:
        if s in site_list: site_list.remove(s)
    
    mass_data = pd.read_excel(saf_file_path, sheet_name="Tissue-AM-Masses")
    
    if verbose:
        list_of_sites_in_mass_file = (mass_data["SiteName"].values) # TODO: Is this being used somewhere?
    
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
    
    SFactorFrame["Sfactors"] = np.zeros(SFactorFrameLen)
    SFactorFrame["CFs"] = np.zeros(SFactorFrameLen)
    SFactorFrame["SiteName"] = np.zeros(SFactorFrameLen)
    
    res_index = 0
    
    CF_vector = np.array([0.1, 0.2, 
                            0.3, 0.4, 
                            0.5, 0.6, 
                            0.7, 0.8, 
                            0.9, 1.0, -1])  # ICRP-value is coded as -1.

    # Before the organ-loop, retreive the energy-spectrum:
    energies = pd.read_excel(isotope_data_path, 
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

        organ_saf_values = pd.read_excel(saf_file_path, sheet_name=organ)
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

                SFactorFrame.loc[res_index,("Sfactors")] = energy_per_desintegration
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

                SFactorFrame.loc[res_index,("Sfactors")] = energy_per_desintegration
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
        
    return (skeletalsites, CF_ICRP_values, tbv_fractions)

##==========================================================================================================================
##
## Main part for testing
##
##==========================================================================================================================

import numpy as np
import pandas as pd
import openpyxl

print("I did run!")

foo, bar, foobar = create_skeletal_phantom(
        saf_file_path = "utils/saf_values_male_redone.xlsx",
        isotope_data_path = "utils/decdataenergies.xlsx",
	verbose = False)

#print(foo[foo["SiteName"] == "LumbarVertebrae"])

print("I produced something!")

