# Red marrow S-factor

Script to calculate to the S-factor for different skeletal sites.

Per july 2020 it uses the Hough and O'Rilley phantoms from the
University of Florida, combined with ICRP-107-data for nuclide
information.

29/7/2020: Made classes for the skeletal phantoms. Now can produce workable multiple CF-phantoms with one line of code.
3/8/2020: Incorporated the generator-function into the class declaration.
6/8/2020: Wrote function to calculate dose directly from a set of inputs on the phantom objects

Bugs:

Needed things:

1) Input data-format, best with perhaps an input file? Input now is an excel-file imported as a pandas-frame with named columns. Write function to tack on the absorbed dose?
* Name of the absorbed-dose column
* Pandas-frame
* Call to the calculate-dose-function

Would make it more user-friendly

