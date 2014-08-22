import httplib2
import xmltodict
import string
import os.path
import meshbrowser

earlyyears = [2004, 2004, 2004, 2006, 2006, 2006, 2006, 2005, 2005, 2005, 2005, 2003, 2003, 2003, 2003, 2003]
lateyears = [2012, 2012, 2012, 2013, 2013, 2013, 2013, 2014, 2014, 2014, 2014, 2013, 2013, 2013, 2013, 2013]

# CONSTANTS + INITIALIZATION

# recommendations from guidelines
# DUTCH BREAST CANCER GUIDELINES
recommendations = {}
recommendations[1] = """Addition of radiotherapy following local excision of DCIS results in a significantly lower risk of local recurrence (this is valid for all subgroups)."""
recommendations[2] = """Adjuvant therapy with tamoxifen in breast-conserving treatment of DCIS, removed with tumour-free excision margins, results in limited improvement of local tumour control and no survival benefit."""
recommendations[3] = """After a boost the risk of local recurrence is lower. The absolute benefit of a boost following complete resection decreases with patient age."""
# SIGN HEPATITIS C GUIDELINES
recommendations[4] = """Children with evidence of moderate or severe liver disease should be considered for treatment with pegylated IFN and ribavirin.
In children who are asymptomatic with mild or no liver disease, benefits of treatment need to be weighed against the risk of side effects.
Children infected with HCV should be managed in consultation with a paediatric service with specialist expertise in hepatitis C."""
recommendations[5] = """Patients with CHC who are on a drug treatment programme can be considered for treatment with a combination of pegylated IFN and ribavirin. Active drug users should be engaged in efforts to address their healthcare needs and in harm reduction. Active drugs users should have a comprehensive assessment of their psychological needs and of their likely adherence to antiviral treatment."""
recommendations[6] = """Patients with compensated cirrhosis should be considered for therapy with pegylated IFN and ribavirin, unless contraindicated."""
recommendations[7] = """Patients with compensated HCV cirrhosis may benefit from IFN treatment to reduce the risk of development of HCC. The duration of therapy required to achieve this is not clear."""
# SIGN LUNG CANCER GUIDELINES
recommendations[8] = """Patients with a negative CT scan result for mediastinal adenopathy should proceed to PET, except for those with small peripheral tumours. Patients with a negative PET scan result for mediastinal adenopathy should proceed to thoracotomy. Patients with a positive PET scan result for mediastinal adenopathy require histological confirmation."""
recommendations[9] = """It may be reasonable to forego further investigation of adrenal glands <2 cm, in patients who are stage cI-II and who have a negative clinical evaluation. Patients having adrenal gland nodules >2 cm, should proceed to further imaging studies and biopsy as necessary."""
recommendations[10] = """VATS resection, undertaken by an appropriately skilled surgeon, may be offered to selected patients with clinical stage I lung cancer."""
recommendations[11] = """Patients with single brain metastases should be offered resection followed by whole brain radiotherapy."""
# SIGN OVARIAN CANCER GUIDELINES
recommendations[12] = """GPs should include ovarian cancer in the differential diagnosis when women present with recent onset persistent non-specific abdominal symptoms (including women whose abdominal and pelvic clinical examinations appear normal)."""
recommendations[13] = """The RMI scoring system is the method of choice for predicting whether or not an ovarian mass is likely to be malignant. Women with an RMI score >200 should be referred to a centre with experience in ovarian cancer surgery."""
recommendations[14] = """To minimise the need for a second operative staging procedure, intraoperative frozen section assessment can be used to diagnose malignancy and to exclude metastatic disease.""" 
recommendations[15] = """In women who wish to conserve their fertility a unilateral salpingo-oophorectomy may be performed if the contralateral ovary appears normal."""
recommendations[16] = """Paclitaxel is recommended in combination therapy with platinum in the first line post-surgery treatment of epithelial ovarian cancer where the potential benefits justify the toxicity of the therapy. Patients who choose less toxic therapy or who are unfit for taxanes should be offered single agent carboplatin. Where carboplatin is used as a single agent in first line therapy attention should be paid to platinum dose optimisation."""



# evidence IDs
evidence_ids = {}
# DUTCH BREAST CANCER GUIDELINES
evidence_ids[1] = ["9469327", "12867108", "10683002", "8292119"]
evidence_ids[2] = ["12867108", "10376613"]
evidence_ids[3] = ["11794170"]
# SIGN HEPATITIS C GUIDELINES
evidence_ids[4] = ["15793840", "11840040", "12395341", "10722449"] 
evidence_ids[5] = ["11818693", "15239094"] 
evidence_ids[6] = ["14996676", "11583749", "12324553", "11106716"]
evidence_ids[7] = ["11394661"]
# SIGN LUNG CANCER GUIDELINES
evidence_ids[8] = ["10911007", "12815135"]
evidence_ids[9] = ["8521790", "1745970", "7972740"]
evidence_ids[10] = ["9801252", "9801251", "9801256", "9801254", "9801253", "9801250", "9801255", "12560900", "11093502", "11016337", "10872623", "7944693"]
evidence_ids[11] = ["2405271", "8498838", "9256144"]
# SIGN OVARIAN CANCER GUIDELINES
evidence_ids[12] = ["11506835", "3338609", "11066047", "11799032"]
evidence_ids[13] = ["2223684", "8760716", "10426607", "11117760", "9263422", "7654041"] 
evidence_ids[14] = ["9714989", "10831977", "9849847"]
evidence_ids[15] = ["9307530"]
evidence_ids[16] = ["10963636", "10623700", "10793106", "12241653"]


# goals: updated evidence
goal_ids = {}
# DUTCH BREAST CANCER GUIDELINES
goal_ids[1] = ["16864166", "20956824", "16801628"]
goal_ids[2] = ["20956824", "21398619"]
goal_ids[3] = ["17577015"]
# SIGN HEPATITIS C GUIDELINES
goal_ids[4] = ["21036173", "20189674", "20400194"]
goal_ids[5] = ["18637072", "18945252", "20351554"]
goal_ids[6] = ["22439668", "22296568", "12324553", "11106716"]
goal_ids[7] = ["22030902", "22414050", "22337287", "21419770"]
# SIGN LUNG CANCER GUIDELINES
goal_ids[8] = ["15620991", "16337397", "17873157", "17448671", "17873168"]
goal_ids[9] = ["21330566", "20099976", "19188319", "15585482", "19752760", "17252463"]
goal_ids[10] = ["17118669", "20106398", "19022040", "19577048", "19626361", "18154816", "16213906"]
goal_ids[11] = ["21041710"]
# SIGN OVARIAN CANCER GUIDELINES
goal_ids[12] = ["22217633", "15957984", "19945742", "15964871", "17154394", "15187051", "19706933", "22217630", "20110551"]
goal_ids[13] = ["19155910", "22484399", "20162854", "19327881", "20219002"]
goal_ids[14] = ["22317865", "21895958", "15589572", "15823099"]
goal_ids[15] = ["16343232", "18080718", "19670446", "21970882", "20116965", "20194858"]
goal_ids[16] = ["18691879", "20673626", "19224846", "20937992", "20733132", "21978765", "21844495"]


# create MeSHBrowser object to calculate MeSH distance 
mb = meshbrowser.MeSHBrowser()

# API set-up
# base URL for all Entrez queries
baseURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
pubURL = "http://www.ncbi.nlm.nih.gov/pubmed/"
# API credentials
creds = "" # &email=XXX@XXX.com&tool=XXX""

# HTTP processor
h = httplib2.Http()
