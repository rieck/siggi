# Datasets of Labeled Graphs

This directory contains different datasets of labeled graphs. Each
dataset is stored as a graph bundle, that is, the individual graphs
are represented in `dot` format and packaged in a simple `zip`
archive. All datasets have been compiled by Benjamin Plock for his
Master thesis at the University of Goettingen, Germany.

## Dataset: `android-fcg`

The samples are Android applications obtained from the Google Play
store and popular third-party markets. Their code structure is
represented by function call graphs, which contain a node for each
function of the application.  Labeling is carried out according to
a generic labeling scheme for Dalvik code: Thee Dalvik instructions
are assigned to 15 distinct functional categories. In this way,
information about the functions can be encoded in a 15-bit label,
where each bit indicates whether an instruction belonging to the
corresponding functional category is present in the function
code. The dataset contains 13,579 benign and 1,216 malicious
samples randomly chosen from the original dataset.

H. Gascon, F. Yamaguchi, D. Arp and K. Rieck. Structural Detection
of Android Malware using Embedded Call Graphs. Proc. of 6th ACM
Workshop on Artificial Intelligence and Security (AISEC), 2013

## Dataset: `dd`

The dataset consists of 1,178 proteins with 691 enzymes and 487
non-enzymes. Each protein is represented by a graph, in which the
nodes are amino acids and two nodes are connected by an edge if
they are less than six Angstroms apart.

_Source:_ P. D. Dobson and A. J. Doig. Distinguishing enzyme
structures from non-enzymes without alignments. Journal of
Molecular Biology, 330(4):771-783, 2003.

## Dataset: `enzymes`

The dataset contains protein tertiary structures consisting of 600
enzymes from the BRENDA enzyme database. In this case the task is
to correctly assign each enzyme to one of the six EC top level
classes.

_Source:_ K. M. Borgwardt, C. S. Ong, S. Schönauer,
S. V. N. Vishwanathan, A. J. Smola and H.-P. Kriegel. Protein
function prediction via graph kernels. Bioinformatics, 21(1):47-56,
Jan. 2005.

_Source:_ I. Schomburg, A. Chang, C. Ebeling, M. Gremse, C. Heldt, G. Huhn
and D. Schomburg. Brenda, the enzyme database: updates and major
new developments. Nucleic Acids Research, 32
(Database-Issue):431-433, 2004.

## Dataset: `flash-cfg`

The dataset comprises the control-flow graphs of Flash samples that
were collected over a period of 12 weeks.  The nodes of these
represent functions, blocks, conditions and references. Here, the
references model function calls by two child nodes, one being a
function node and one the successor after returning from the
function. Each of the four types is distinguished by a
corresponding node label. We selected a subset of 1,372 benign and
343 malicious Flash binaries from the original dataset.

_Source:_ C. Wressnegger, F. Yamaguchi, D. Arp and
K. Rieck. Comprehensive Analysis and Detection of Flash-based
Malware. Proc. of 13th Conference on Detection of Intrusions and
Malware & Vulnerability Assessment (DIMVA)

## Dataset: `mutag`

This is a dataset of 188 mutagenic aromatic and heteroaromatic
nitro compounds assayed for mutagenicity on bacterium Salmonella
typhimurium.  The classification task is to predict whether a given
molecule exerts a mutagenic effect. The graphs corresponding to the
molecules are crafted by representing the atoms as nodes and the
bounds between the atoms as edges. Each node is labeled with its
atom type.

_Source:_ A. K. Debnath, R. L. Lopez de Compadre, G. Debnath,
A. J. Shusterman and C.  Hansch. Structure-activity relationship of
mutagenic aromatic and heteroaromatic nitro compounds. Correlation
with molecular orbital energies and hydrophobicity. Journal of
Medicinal Chemistry, 34(2):786-797, 1991.

## Dataset: `nci1`

The dataset contains 4,110 chemical compounds as graphs.  These
compounds were screened for activity against non-small cell lung
cancer.

_Source:_ N. Wale and G. Karypis. Comparison of descriptor spaces
for chemical compound retrieval and classi cation. In ICDM, pages
678-689. IEEE Computer Society, 2006.

## Dataset: `nci109`

The dataset contains 4,127 chemical compounds as graphs. These
compounds were screened for activity against overian cancer cell
lines.

_Source:_ N. Wale and G. Karypis. Comparison of descriptor spaces
for chemical compound retrieval and classi cation. In ICDM, pages
678–689. IEEE Computer Society, 2006.

## Dataset: `ptc`

The dataset contains chemical compounds, which are tested for
cancerogenicity in mice and rats.  The classification task is to
predict the cancerogenicity of compounds. Each compound is
represented as a graph, whose nodes are atoms and whose edges are
bonds.  The PTC datasets record the cancerogenicity of several
hundred chemical compounds for male rats (MR), female rats (FR),
male mice (MM), and female mice (FM). We chose the 344 graphs of MR
for evaluation.

_Source:_ H. Toivonen, A. Srinivasan, R. D. King, S. Kramer, and
C. Helma. Statistical evaluation of the predictive toxicology
challenge 2000-2001.  Bioinformatics (Oxford, England),
19(10):1183-1193, 2003.
