import sys

from PyQt5 import Qt, QtWidgets, uic, QtCore
from Scoring import OnTargetScore
from Algorithms import SeqTranslate

# =========================================================================================
# CLASS NAME: Results
# Inputs: Takes information from the main application window and displays the gRNA results
# Outputs: The display of the gRNA results search
# =========================================================================================


class Results(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Results, self).__init__(parent)
        uic.loadUi('resultsWindow.ui', self)

        self.setWindowTitle('Results')
        self.geneViewer.setReadOnly(True)
        # Scoring Class object #
        self.onscore = OnTargetScore()
        self.S = SeqTranslate()

        # Main Data container
        # Keys: Gene names
        # Values: #
        self.AllData = {}


        self.startpos = 0
        self.endpos = 0
        self.directory = ""

        self.switcher = [1,1,1,1,1,1,1]  # for keeping track of where we are in the sorting clicking for each column

        # Target Table settings #
        self.targetTable.setColumnCount(7)  # hardcoded because there will always be seven columns
        self.targetTable.setShowGrid(False)
        self.targetTable.setHorizontalHeaderLabels("Location;Sequence;Strand;PAM;Score;Off-Target;Highlight".split(";"))
        self.targetTable.horizontalHeader().setSectionsClickable(True)
        self.targetTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.targetTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.targetTable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.offTargetSearch.clicked.connect(self.offtargetButtonClicked)
        self.targetTable.horizontalHeader().sectionClicked.connect(self.table_sorting)

        self.targetTable.itemSelectionChanged.connect(self.item_select)



    # Function that is called in main in order to pass along the information the user inputted and the information
    # from the .cspr files that was discovered
    def transfer_data(self, org, endo, path, geneposdict, fasta):
        self.org = org
        self.endo = endo
        self.directory = path
        self.fasta_ref = fasta
        for gene in geneposdict:
            self.comboBoxGene.addItem(gene)
            self.get_targets(gene, geneposdict[gene])

    # Function grabs the information from the .cspr file and adds them to the AllData dictionary
    def get_targets(self, genename, pos_tuple):
        targets = []
        if self.directory.find("/") != -1:
            file = open(self.directory+"/" + self.org + "_" + self.endo + ".cspr")
        else:
            file = open(self.directory + "\\" + self.org + "_" + self.endo + ".cspr")
        mainHeader = file.readline()
        header = file.readline()


        # Find the right chromosome:
        while True:
            # in the right chromosome/scaffold?
            if header.find("(" + str(pos_tuple[0]) + ")"):
                while True:
                    # Find the appropriate location by quickly decompressing the location at the front of the line
                    myline = file.readline()
                    if self.S.decompress64(myline.split(",")[0]) >= pos_tuple[1]:
                        while self.S.decompress64(myline.split(",")[0]) < pos_tuple[2]:
                            targets.append(self.S.decompress_csf_tuple(myline))
                            myline = file.readline()
                    else:
                        continue
                    break
                break
            else:
                header = file.readline()

        self.AllData[genename] = targets
        self.displayGeneData()

    def displayGeneData(self):
        curgene = str(self.comboBoxGene.currentText())
        #self.geneViewer.setPlainText(cg)
        #  --- Shifting numbers over based on start and end ---  #

        self.targetTable.setRowCount(len(self.AllData[curgene]))
        print(self.AllData[curgene])
        index = 0
        for item in self.AllData[curgene]:
            loc = QtWidgets.QTableWidgetItem(str(item[0]))
            seq = QtWidgets.QTableWidgetItem(item[1])
            strand = QtWidgets.QTableWidgetItem(str(item[4]))
            PAM = QtWidgets.QTableWidgetItem(item[2])
            score = QtWidgets.QTableWidgetItem(str(item[3]))
            self.targetTable.setItem(index, 0, loc)
            self.targetTable.setItem(index, 1, seq)
            self.targetTable.setItem(index, 2, strand)
            self.targetTable.setItem(index, 3, PAM)
            self.targetTable.setItem(index, 4, score)
            self.targetTable.setItem(index, 5, QtWidgets.QTableWidgetItem("--.--"))
            ckbox = QtWidgets.QCheckBox()
            ckbox.clicked.connect(self.search_gene)
            self.targetTable.setCellWidget(index,6,ckbox)
            index += 1
        self.targetTable.resizeColumnsToContents()

    def search_gene(self):
        search_trms = []
        checkBox = self.sender()
        index = self.targetTable.indexAt(checkBox.pos())
        print(index.column(), index.row(), checkBox.isChecked())
        #self.geneViewer.setPlainText(self.geneViewer.text())
        seq = self.targetTable.item(index.row(),1).text()
        print(seq)
        x=1

    def item_select(self):
        print(self.targetTable.selectedItems())

    def table_sorting(self, logicalIndex):
        self.switcher[logicalIndex] *= -1
        if self.switcher[logicalIndex] == -1:
            self.targetTable.sortItems(logicalIndex, QtCore.Qt.DescendingOrder)
        else:
            self.targetTable.sortItems(logicalIndex, QtCore.Qt.AscendingOrder)

    def offtargetButtonClicked(self):
        all_targets = []
        index = 0
        holdt = ()
        QtWidgets.QMessageBox.question(self, "Text File Created",
                                       "A File with the off target data has been created.",
                                       QtWidgets.QMessageBox.Ok)
        """for target in self.targetTable.selectedItems():
            for item in target:
                print(item.text())

            #print(target.text())
        """
    """def displayGene(self,fastafile=None, Kegg=False, NCBI=False):
        organism_genome = list()  # list of chromosomes/scaffolds
        if fastafile:
            f = open(fastafile)
            chr_string = str()
            for line in f:
                if not line.startswith(">"):
                    chr_string += line[:-1]
                else:
                    organism_genome.append(chr_string)
                    chr_string = ""
            return organism_genome
        elif Kegg:
            # Get the gene from the Kegg database
        elif NCBI:
            # Get the gene from NCBI database (RefSeq)

        else:
            return "Error: Cannot find reference sequence.  Search Kegg, NCBI, or download a FASTA file to create a genome reference."""""





    #-----Testing Methods -----#
    def fill_table_TEST(self):
        y=2
        x = self.getTargets("tsh_spCas9-VRER")

        #self.loadGenesandTargets("testing_seq1",1,3,["target1","target2","target3"],"testo")
        #self.splitCsprFile("BY,Xc9d+CV,q")
        """self.targetTable.setRowCount(3)
        seq = QtWidgets.QTableWidgetItem("testing")
        self.targetTable.setItem(0, 0,seq )
        seq = QtWidgets.QTableWidgetItem("other")
        self.targetTable.setItem(1, 0, seq)
        seq = QtWidgets.QTableWidgetItem("third")
        self.targetTable.setItem(2, 0, seq)
        self.geneViewer.setPlainText("this is testing the third other thing")
        self.geneViewer.setFontItalic(True)
        self.geneViewer.find("testing")"""





# Window opening and GUI launching code #
# ----------------------------------------------------------------------------------------------------- #
"""
app = Qt.QApplication(sys.argv)
app.setOrganizationName("TrinhLab-UTK")
app.setApplicationName("CASPER")
window = Results()
window.transfer_data("yli", "spCas9", "C:\\Users\\GregCantrall\\Documents\\Cspr files", {"myfakegene":(1,1293,3496)}, "/Volumes/Seagate_Drive/FASTAs/yli.fna")
sys.exit(app.exec_())"""