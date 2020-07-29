# Red marrow S-factor

Script to calculate to the S-factor for different skeletal sites.

Per july 2020 it uses the Hough and O'Rilley phantoms from the
University of Florida, combined with ICRP-107-data for nuclide
information.

29/7/2020: Made classes for the skeletal phantoms. Now can produce workable multiple CF-phantoms with one line of code. Neat!

Needed things:

0) Different CFs in a neat format. Stick with pandas-frame for now? Use pickle-files for persistent data-storage.

1) Input data-format, best with perhaps an input file?

2) Other nuclies, 90-Y, 131-I?

3) Usable interface - see point 1.

