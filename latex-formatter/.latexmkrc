# ==============================================================================
# FoodLAB Guidebook LaTeXmk Configuration
# ==============================================================================
# Automatically outputs compiled PDF to 'build/' and purges all intermediate
# auxiliary files upon completion to guarantee a clean build/ folder.
# ==============================================================================

$out_dir = 'build';
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 -file-line-error %O %S';

# Automatic auxiliary cleanup (1 = clean after successful compilation, keeps .pdf only)
$cleanup_mode = 1;

# Comprehensive list of auxiliary extensions to purge
$clean_ext = 'synctex.gz synctex.gz(busy) synctex(busy) lof lot out toc fls fdb_latexmk aux log bbl blg idx ilg ind nav snm vrb run.xml bcf %R.synctex%O';
