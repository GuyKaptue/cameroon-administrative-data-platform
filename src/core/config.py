"""
cameroon-administrative-data-platform/src/core/config.py
Configuration settings for the population simulation pipeline - paths, growth rates,
regional multipliers, and validation thresholds.

Includes:
- RGPH 2005 census data (arrondissement level) from the official village repertoire
- RGPH 2010 data (arrondissement level) from the partition PDF
- UN World Population Prospects 2024 for national totals
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_PROJECT_ROOT = Path("/Volumes/Intenso/my_work_spaces/cameroon-administrative-data-platform")


def get_project_root() -> Path:
    env_root = os.environ.get("CAMEROON_PROJECT_ROOT")
    if env_root:
        root_path = Path(env_root).resolve()
        if root_path.exists():
            print(f"📁 Using project root from environment variable: {root_path}")
            return root_path

    if DEFAULT_PROJECT_ROOT.exists():
        print(f"📁 Using default project root: {DEFAULT_PROJECT_ROOT}")
        return DEFAULT_PROJECT_ROOT

    current = Path(__file__).resolve()
    markers = ["data", "src", "requirements.txt", "pyproject.toml", "LICENCE"]

    for parent in [current] + list(current.parents):
        if parent.name == "cameroon-administrative-data-platform":
            print(f"📁 Auto-detected project root: {parent}")
            return parent
        for marker in markers:
            if (parent / marker).exists():
                print(f"📁 Auto-detected project root: {parent}")
                return parent

    fallback = Path.cwd()
    print(f"⚠️ Using fallback project root: {fallback}")
    return fallback


@dataclass
class Config:
    """Configuration class for Cameroon population pipeline"""

    custom_root: Optional[Path] = None

    def __post_init__(self):
        if self.custom_root:
            self._root = Path(self.custom_root).resolve()
            print(f"📁 Using custom root: {self._root}")
        else:
            self._root = get_project_root()

    @property
    def BASE_DIR(self) -> Path:
        return self._root

    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "data"

    @property
    def EXTERNAL_DIR(self) -> Path:
        return self.DATA_DIR / "external"

    @property
    def RAW_DIR(self) -> Path:
        return self.DATA_DIR / "raw"

    @property
    def PROCESSED_DIR(self) -> Path:
        return self.DATA_DIR / "processed"

    @property
    def OUTPUT_DIR(self) -> Path:
        return self.DATA_DIR / "output"

    # GeoBoundaries files
    @property
    def ADM1_FILE(self) -> Path:
        return self.EXTERNAL_DIR / "geoBoundaries-CMR-ADM1.geojson"

    @property
    def ADM2_FILE(self) -> Path:
        return self.EXTERNAL_DIR / "geoBoundaries-CMR-ADM2.geojson"

    @property
    def ADM3_FILE(self) -> Path:
        return self.EXTERNAL_DIR / "geoBoundaries-CMR-ADM3.geojson"

    @property
    def WOF_DIR(self) -> Path:
        return self.EXTERNAL_DIR / "whosonfirst-data-admin-cm-latest"

    @property
    def WOF_LOCALITY_SHP(self) -> Path:
        return self.WOF_DIR / "whosonfirst-data-admin-cm-locality-point.shp"

    # =========================================================
    # RGPH 2005 CENSUS DATA - ARRONDISSEMENT LEVEL
    # Source: cmr-2005-rec_v4.7_repertoire_actualise_villages_cameroun.pdf
    # These are the official 2005 census figures from the village repertoire
    # =========================================================

    ARRONDISSEMENT_POPULATION_2005: Dict[str, int] = field(default_factory=lambda: {
        # ========== ADAMAOUA (pages 10-31) ==========
        "NGAOUNDAL": 52867, "TIBATI": 72081, "GALIM TIGNERE": 25739, "MAYO BALEO": 15873,
        "KONTCHA": 6938, "TIGNERE": 34167, "BANKIM": 70132, "BANYO": 93880,
        "MAYO-DARLE": 23054, "DIR": 34284, "DJOHONG": 24445, "NGAOUI": 24196,
        "MEIGANGA": 88745, "BELEL": 37663, "MBE": 17478, "NGAOUNDERE I": 78277,
        "NGAOUNDERE II": 84959, "NGAOUNDERE III": 17527, "MARTAP": 24815, "NGAN-HA": 28726,
        "NYAMBAKA": 28726,

        # ========== CENTRE (pages 32-98) ==========
        "BIBEY": 4875, "LEMBE YEZOUM": 7207, "MBANDJOCK": 21076, "MINTA": 11406,
        "NANGA-EBOKO": 29814, "NKOTENG": 19797, "NSEM": 6177, "BATSCHENGA": 9303,
        "EBEBDA": 21368, "ELIG-MFOMO": 16161, "EVODOULA": 18899, "LOBO": 10157,
        "MONATELE": 36933, "OBALA": 78929, "OKOLA": 41081, "SA'A": 53219,
        "BAFIA": 72717, "BOKITO": 40228, "DEUK": 11485, "KIIKI": 8519,
        "KON-YAMBETTA": 8692, "MAKENENE": 16564, "NDIKINIMEKI": 17462, "NITOUKOU": 48312,
        "OMBESSA": 25640, "MBANGASSINA": 41180, "NGAMBE-TIKAR": 12489, "NGORO": 13892,
        "NTUI": 25618, "YOKO": 12332, "AFANLOUM": 17879, "ASSAMBA": 48012,
        "AWAE": 15888, "EDZENDOUAN": 44362, "ESSE": 16822, "MFOU": 37209,
        "NKOLAFAMBA": 14494, "SOA": 30588, "AKONO": 8511, "BIKOK": 16278,
        "MBANKOMO": 20305, "NGOUMOU": 13923, "YAOUNDE I": 281586, "YAOUNDE II": 336381,
        "YAOUNDE III": 252501, "YAOUNDE IV": 477350, "YAOUNDE V": 265087, "YAOUNDE VI": 268971,
        "YAOUNDE VII": 97997, "BIYOUHA": 3386, "BONDJOCK": 8431, "BOT-MAKAK": 17089,
        "DIBANG": 9063, "ESEAK": 23242, "MAKAK": 29135, "MATOMB": 11512,
        "MESSONDO": 14139, "NGUIBASSAL": 46852, "NGOG MAPUBI": 9137, "AKOEMAN": 5397,
        "AKONOLINGA": 4756, "AYOS": 22899, "ENDOM": 14789, "MENGANG": 8031,
        "NYAKOKOMBO": 11227, "DZENG": 9412, "MBALMAYO": 62808, "MENGUEME": 7527,
        "NGOMEDZAP": 2150, "NKOLMETET": 13647,

        # ========== EST (pages 99-132) ==========
        "GARI GOMBO": 15978, "MOLOUNDOU": 18174, "SALAPOUMBE": 17240, "YOKADOUMA": 63962,
        "ABONG-MBANG": 29005, "BEBEND": 9335, "DIMAKO": 12894, "DJA": 10431,
        "DOUMAINTANG": 7956, "DOUME": 18429, "LOMIE": 18952, "MBOANZ": 13608,
        "MBOMA": 8120, "MESSAMENA": 26153, "MESSOK": 11213, "NGOYLA": 4424,
        "NGUELEMENDOUKA": 21097, "SOMALOMO": 4902, "BATOURI": 67007, "BOMBE": 16147,
        "KETTE": 31129, "MBANG": 25603, "MBOTORO": 7674, "NDEM-NAM": 10411,
        "NDELELE": 26127, "BELABO": 30953, "BERTOUA I": 52355, "BERTOUA II": 52355,
        "BETARE-OYA": 41173, "DIANG": 15795, "GAROUA-BOULAI": 41388, "MANDJOU": 17097,
        "NGOURA": 34489,

        # ========== EXTREME-NORD (pages 132-218) ==========
        "BOGO": 95230, "GAZAWA": 27395, "MAROUA I": 134934, "MAROUA II": 108902,
        "MAROUA III": 86574, "MERI": 86834, "DARGALA": 33142, "NDOUKOULA": 32091,
        "PETTE": 37125, "BLANGOUA": 50398, "DARAK": 23901, "FOTOKOL": 36893,
        "GOULFEY": 58117, "HILE-ALIFA": 18425, "KOUSSERI": 101246, "LOGONE BIRNI": 52589,
        "ZINA": 25572, "MAKARI": 10484, "WAZA": 15013, "DATCHEKA": 31545,
        "GOBO": 53119, "GUERE": 38328, "KAI-KAI": 55366, "KALFOU": 26203,
        "KARHAY": 42963, "MAGA": 85100, "TCHATIBALI": 32063, "VELE": 41693,
        "WINA": 30702, "YAGOUA": 91979, "GUIDIGUIS": 43632, "KAELE": 105504,
        "MINDIF": 50530, "MOULVOUDAYE": 82368, "MOUTOURWA": 40197, "PORHI": 38809,
        "TAIBONG": 43606, "KOLOFATA": 77857, "MORA": 179777, "TOKOMBERE": 91256,
        "BOURHA": 88585, "HINA": 43755, "KOZA": 81076, "MAYO-MOSKOTA": 73716,
        "MOGODE": 112905, "MOKOLO": 242274, "SOULEDE ROUA": 57660,

        # ========== LITTORAL (pages 218-247) ==========
        "BARE-BAKEM": 16485, "DIBOMBARI": 17141, "ABO": 25018, "LOUM": 39707,
        "MANJO": 34230, "MBANGA": 35415, "MOMBO": 5530, "MELONG": 54279,
        "NJOMBE-PENJA": 31792, "NKONGSAMBA I": 52434, "NKONGSAMBA II": 37154,
        "NKONGSAMBA III": 15795, "NLONAKO": 14261, "NKONDJOCK": 17428,
        "NORD MAKOMBE": 3999, "YABASSI": 12999, "YINGUI": 2304, "DIZANGUE": 17086,
        "EDEA I": 64761, "EDEA II": 13539, "MOUANKO": 9162, "NDOM": 10340,
        "NYANON": 12517, "NGAMBE": 6210, "MASSOK-SONGLOULOU": 5044, "POUMA": 13475,
        "DIBAMBA": 5350, "NGWEI": 4831, "DOUALA I": 223214, "DOUALA II": 261407,
        "DOUALA III": 646347, "DOUALA IV": 250626, "DOUALA V": 544919, "DOUALA VI": 5464,
        "MANOKA": 5464,

        # ========== NORD (pages 248-298) ==========
        "BIBEMI": 13319, "DEMBO": 15816, "LAGDO": 14212, "GAROUA I": 120232,
        "GAROUA II": 117841, "GAROUA III": 27229, "BASCHEO": 26743, "DEMSA": 37282,
        "TOUROUA": 40674, "PITOA": 76715, "TCHEBOA": 92658, "MAYO HOURNA": 21445,
        "BEKA": 31595, "POLI": 37882, "FIGUIL": 67997, "GUIDER": 223503,
        "MAYO OULO": 99826, "REY-BOUBA": 116192, "TCHOLLIRE": 47296, "MADINGRING": 57347,
        "TOUBORO": 154366,

        # ========== NORD-OUEST (pages 298-322) ==========
        "BELO": 40757, "BUM": 17838, "FUNDONG": 45831, "NJINIKOM": 20461,
        "JAKIRI": 47022, "KUMBO": 83479, "MBVEN": 20289, "NKUM": 44059,
        "NONI": 39400, "OKU": 87720, "AKO": 40349, "MISAJE": 22641,
        "NDU": 73955, "NKAMBE": 63032, "NWA": 69954, "FUNGOM": 58666,
        "FURU-AWA": 13997, "MENCHUM VALLEY": 50235, "WUM": 39100, "BAFUT": 57930,
        "BALI": 30375, "BAMENDA 1": 28359, "BAMENDA 2": 184277, "BAMENDA 3": 110253,
        "SANTA": 64391, "TUBAH": 48542, "BATIBO": 44619, "MBENGWI": 31591,
        "NGIE": 17697, "NJIKWA": 16634, "WIDIKUM-MENKA": 28152, "BABESSI": 49208,
        "BALIKUMBAT": 68537, "NDOP": 69603,

        # ========== OUEST (pages 323-364) ==========
        "BABADJOU": 36929, "BATCHAM": 83817, "GALIM": 51014, "MBOUDA": 120650,
        "BAFANG": 29821, "BAKOU": 5255, "BANA": 10254, "BANDJA": 30931,
        "KEKEM": 31542, "BANWA": 11693, "BANKA": 25290, "BAHAM": 19680,
        "BAMENDJOU": 34269, "BATIE": 10942, "BANGOU": 15787, "BAYANGAM": 13397,
        "POUMOUGNE": 40637, "DJEBEM": 10987, "DSCHANG": 101385, "FOKOUE": 9576,
        "NKONG-NI": 53367, "PENKA-MICHEL": 65135, "SANCHOU": 37479, "FONGO TONGO": 18822,
        "BAFOUSSAM I": 98339, "BAFOUSSAM II": 121282, "BAFOUSSAM III": 81835,
        "BANGANGTE": 63595, "BASSAMBA": 2814, "BAZOU": 14912, "TONGA": 13528,
        "BANGOURAIN": 30877, "FOUMBAN": 106309, "FOUMBOT": 76486, "KOUOPTAMO": 48772,
        "KOUTABA": 49171, "MAGBA": 35628, "MALENTOUEN": 45121, "MASSANGAM": 38736,
        "NJIMOM": 23983,

        # ========== SUD (pages 365-397) ==========
        "BENGBIS": 13075, "DJOUM": 18050, "MEYOMESSALA": 31366, "MINTOM": 6130,
        "OVENG": 6007, "SANGMELIMA": 82513, "ZOETELE": 30583, "MEYOMESSI": 9227,
        "BIWONG-BANE": 13151, "BIWONG-BULU": 12867, "EBOLOWA I": 40538, "EBOLOWA II": 55957,
        "EFOULAN": 8905, "MENGONG": 17222, "MVANGAN": 16114, "NGOULEMAKONG": 14675,
        "AKOM II": 8802, "NIETE": 23921, "BIPINDI": 14118, "CAMPO": 6923,
        "KRIBI I": 29886, "KRIBI II": 40679, "LOKOUNDJE": 22681, "LOLODORF": 14326,
        "MVENGUE": 17757, "AMBAM": 41089, "MA'AN": 12448, "OLAMZE": 8528,
        "KYE OSSI": 17120,

        # ========== SUD-OUEST (pages 398-425) ==========
        "BUEA": 131325, "WEST COAST": 12725, "LIMBE I": 93255, "LIMBE II": 16401,
        "LIMBE III": 8554, "MUYUKA": 86268, "TIKO": 117884, "BANGEM": 21411,
        "NGUTI": 27151, "TOMBEL": 57017, "ALOU": 35855, "FONTEM": 39706,
        "WABANE": 38175, "AKWAYA": 85914, "EYUMODJOCK": 35999, "MAMFE CENTRAL": 31641,
        "UPPER BANYANG": 27485, "KUMBA I": 68095, "KUMBA II": 62878, "KUMBA III": 35358,
        "KONYE": 44711, "MBONGE": 115692, "BAMUSSO": 19230, "EKONDO-TITI": 56503,
        "DIKOMBA BALUE": 13364, "IDABATO": 3482, "ISANGELE": 3476, "KOMBO ABEDIMO": 2146,
        "KOMBO ITINDI": 2958, "MUNDEMBA": 14385, "TOKO": 7035,
    })

    # =========================================================
    # RGPH 2010 DATA - ARRONDISSEMENT LEVEL
    # Source: partition_population_Cameroun_departement_arrondissement_district_en_2010_par_sexe.pdf
    # These are the official 2010 population figures
    # =========================================================

    ARRONDISSEMENT_POPULATION_2010: Dict[str, int] = field(default_factory=lambda: {
        # ========== ADAMAOUA (from PDF page 1-5) ==========
        "NGAOUNDAL": 25853, "TIBATI": 22869, "GALIM TIGNERE": 5233, "MAYO BALEO": 3507,
        "KONTCHA": 3290, "TIGNERE": 11085, "BANKIM": 11372, "BANYO": 30730,
        "MAYO-DARLE": 7493, "DIR": 5148, "DJOHONG": 4145, "NGAOUI": 12831,
        "MEIGANGA": 38096, "BELEL": 5555, "MBE": 3585, "NGAOUNDERE": 152698,

        # ========== CENTRE (from PDF pages 7-14) ==========
        "MBANDJOCK": 18771, "MINTA": 2151, "NANGA-EBOKO": 18282, "BIBEY": 1057,
        "LEMBE YEZOUM": 776, "NSEM": 873, "NKOTENG": 17743, "EBEBDA": 2770,
        "ELIG-MFOMO": 996, "EVODOULA": 2236, "MONATELE": 10324, "OBALA": 29054,
        "BATSCHENGA": 3308, "OKOLA": 3725, "LOBO": 1091, "SA'A": 9895,
        "BAFIA": 47471, "BOKITO": 4273, "DEUK": 17068, "MAKENENE": 13974,
        "NDIKINIMEKI": 8874, "NITOUKOU": 13106, "OMBESSA": 3816, "MBANGASSINA": 4306,
        "NGAMBE-TIKAR": 3562, "NGORO": 3293, "NTUI": 10500, "YOKO": 3093,
        "AWAE": 3427, "ASSAMBA": 891, "ESSE": 2360, "AFANLOUM": 401,
        "EDZENDOUAN": 4132, "MFOU": 10533, "NKOLAFAMBA": 3681, "SOA": 15456,
        "AKONO": 3168, "BIKOK": 14147, "MBANKOMO": 3429, "NGOUMOU": 5240,
        "YAOUNDE 1": 281586, "YAOUNDE 2": 336381, "YAOUNDE 3": 252501,
        "YAOUNDE 4": 477350, "YAOUNDE 5": 265087, "YAOUNDE 6": 268971,
        "BOT MAKAK": 4257, "NGUIBASSAL": 576, "DIBANG": 12256, "ESEKA": 17904,
        "MAKAK": 8392, "BONDJOCK": 10465, "MATOMB": 2234, "MESSONDO": 11325,
        "BIYOUHA": 16518, "NGOG MAPUBI": 10605, "AKONOLINGA": 19282, "MENGANG": 2144,
        "AYOS": 8654, "NYAKOKOMBO": 6173, "ENDOM": 17588, "DZENG": 667,
        "MBALMAYO": 5281, "AKOEMAN": 2770, "MENGUEME": 8234, "NKOLMETET": 15297,
        "NGOMEDZAP": 2150,

        # ========== EST (from PDF pages 21-24) ==========
        "GARI GOMBO": 4588, "MOLOUNDOU": 4421, "SALAPOUMBE": 2947, "YOKADOUMA": 21091,
        "ABONG-MBANG": 15663, "BEBEND": 11256, "DIMAKO": 6112, "DJA": 3489,
        "DOUMAINTANG": 591, "DOUME": 6093, "LOMIE": 4266, "MBOANZ": 1613,
        "MBOMA": 7263, "MESSAMENA": 3180, "MESSOK": 1627, "NGOYLA": 1271,
        "NGUELEMENDOUKA": 3549, "SOMALOMO": 973, "BATOURI": 31683, "BOMBE": 8228,
        "KETTE": 4951, "MBANG": 7323, "MBOTORO": 10285, "NDEM-NAM": 595,
        "NDELELE": 4199, "BELABO": 15616, "BERTOUA": 88462, "BETARE-OYA": 82064,
        "DIANG": 2984, "GAROUA-BOULAI": 22410, "NGOURA": 26331,

        # ========== EXTREME-NORD (from PDF pages 29-35) ==========
        "BOGO": 21046, "GAZAWA": 11006, "MAROUA": 20137, "DARGALA": 4086,
        "NDOUKOULA": 1454, "MERI": 2982, "PETTE": 10442, "BLANGOUA": 17454,
        "DARAK": 8614, "FOTOKOL": 11787, "GOULFEY": 5754, "HILE-ALIFA": 3647,
        "KOUSSERI": 89123, "LOGONE BIRNI": 35691, "ZINA": 16908, "MAKARY": 6287,
        "WAZA": 5646, "DATCHEKA": 23831, "GOBO": 13747, "GUERE": 3368,
        "KAI-KAI": 4935, "KALFOU": 3669, "KARHAY": 11788, "MAGA": 15701,
        "TCHATIBALI": 7482, "VELE": 4908, "WINA": 2227, "YAGOUA": 37867,
        "GUIDIGUIS": 15741, "KAELE": 25810, "MINDIF": 8332, "MOULVOUDAYE": 73833,
        "MOUTOURWA": 4570, "PORHI": 18379, "TAIBONG": 3303, "KOLOFATA": 10605,
        "MORA": 39440, "TOKOMBERE": 6147, "BOURHA": 8542, "HINA": 3901,
        "KOZA": 9723, "MAYO-MOSKOTA": 6281, "MOGODE": 8421, "MOKOLO": 33335,
        "SOULEDE ROUA": 1881,

        # ========== LITTORAL (from PDF pages 38-41) ==========
        "BARE-BAKEM": 7512, "DIBOMBARI": 12823, "ABO": 16022, "LOUM": 37537,
        "MANJO": 26758, "MBANGA": 28306, "MOMBO": 4605, "MELONG": 49180,
        "NJOMBE-PENJA": 31090, "NKONGSAMBA": 15280, "NLONAKO": 3412,
        "NKONDJOCK": 4232, "NORD MAKOMBE": 530, "YABASSI": 4288, "YINGUI": 1525,
        "DIZANGUE": 6632, "EDEA": 66581, "MOUANKO": 1604, "NDOM": 2294,
        "NYANON": 2228, "NGAMBE": 2573, "MASSOK-SONGLOULOU": 793, "POUMA": 3154,
        "DOUALA 1": 223214, "DOUALA 2": 261407, "DOUALA 3": 641073, "DOUALA 4": 242821,
        "DOUALA 5": 538449, "MANOKA": 517,

        # ========== NORD (from PDF pages 43-46) ==========
        "BIBEMI": 9140, "DEMBO": 2284, "LAGDO": 21517, "GAROUA": 235996,
        "BASCHEO": 2751, "DEMSA": 7898, "TOUROUA": 8849, "PITOA": 21546,
        "TCHEBOA": 22565, "BEKA": 3606, "POLI": 8462, "FIGUIL": 20226,
        "GUIDER": 52316, "MAYO OULO": 8401, "REY-BOUBA": 6754, "TCHOLLIRE": 10465,
        "MADINGRING": 9551, "TOUBORO": 18583,

        # ========== NORD-OUEST (from PDF pages 49-53) ==========
        "BELO": 10130, "BUM": 2775, "FUNDONG": 7624, "NJINIKOM": 4975,
        "JAKIRI": 9959, "KUMBO": 80212, "MBVEN": 5070, "NONI": 4692,
        "OKU": 28491, "AKO": 5516, "MISAJE": 3601, "NDU": 12531,
        "NKAMBE": 17191, "NWA": 7400, "FUNGOM": 1315, "FURU-AWA": 1501,
        "MENCHUM VALLEY": 7370, "WUM": 27218, "BAFUT": 16388, "BALI": 17612,
        "BAMENDA": 269530, "SANTA": 8128, "TUBAH": 13068, "BATIBO": 10350,
        "MBENGWI": 10961, "NGIE": 1983, "NJIWKA": 5455, "WIDIKUM-MENKA": 7289,
        "BABESSI": 7320, "BALIKUMBAT": 10163, "NDOP": 25740,

        # ========== OUEST (from PDF pages 56-59) ==========
        "BABADJOU": 5243, "BATCHAM": 3301, "GALIM": 5679, "MBOUDA": 46071,
        "BAFANG": 21915, "BAKOU": 1153, "BANA": 2878, "BANDJA": 6167,
        "KEKEM": 17333, "BANWA": 2032, "BANKA": 13026, "BAHAM": 3627,
        "BAMENDJOU": 5351, "BATIE": 1762, "BANGOU": 2794, "BAYANGAM": 1201,
        "POUMOUGNE": 20354, "DJEBEM": 2464, "DSCHANG": 63838, "FOKOUE": 1127,
        "NKONG-NI": 824, "PENKA-MICHEL": 5258, "SANTHOU": 9428, "BAFOUSSAM": 81611,
        "BALENG": 9952, "BAMOUGOUM": 58152, "BANGANGTE": 28011, "BASSAMBA": 2814,
        "BAZOU": 5923, "TONGA": 10807, "BANGOURAIN": 14582, "FOUMBAN": 83522,
        "FOUMBOT": 50716, "KOUOPTAMO": 8009, "KOUTABA": 9410, "MAGBA": 19829,
        "MALENTOUEN": 11661, "MASSANGAM": 8237,

        # ========== SUD (from PDF pages 62-64) ==========
        "BENGBIS": 1605, "DJOUM": 5447, "MEYOMESSALA": 1283, "MINTOM": 1322,
        "OVENG": 639, "SANGMELIMA": 51330, "ZOETELE": 3634, "BIWONG-BANE": 802,
        "EBOLOWA": 64980, "MENGONG": 13837, "MVANGAN": 16959, "NGOULEMAKONG": 2682,
        "AKOM II": 1258, "NIETE": 805, "BIPINDI": 861, "CAMPO": 2492,
        "KRIBI": 59928, "LOLODORF": 4450, "MVENGUE": 1326, "AMBAM": 16060,
        "MA'AN": 904, "OLAMZE": 2042,

        # ========== SUD-OUEST (from PDF pages 68-71) ==========
        "BUEA": 90090, "WEST COAST": 5872, "LIMBE": 84223, "MUYUKA": 28046,
        "TIKO": 101859, "BANGEM": 5712, "NGUTI": 4560, "TOMBEL": 15632,
        "ALOU": 5620, "FONTEM": 7023, "WABANE": 5096, "AKWAYA": 3507,
        "EYUMODJOCK": 2083, "MAMFE": 13046, "UPPER BANYANG": 2046, "KUMBA": 14426,
        "KONYE": 4367, "MBONGE": 5287, "BAMUSSO": 801, "EKONDO-TITI": 15370,
        "DIKOMBA BALUE": 4714, "IDABATO": 1210, "ISANGELE": 1728, "KOMBO ABEDIMO": 754,
        "MUNDEMBA": 5236, "TOKO": 681,
    })

    # =========================================================
    # NATIONAL POPULATION DATA FROM UN (Worldometer)
    # Source: Worldometer / UN Department of Economic and Social Affairs
    # =========================================================

    NATIONAL_POPULATION: Dict[int, int] = field(default_factory=lambda: {
        2005: 17_074_594,
        2010: 19_668_066,
        2015: 22_763_414,
        2020: 26_210_558,
        2025: 29_879_337,
        2026: 30_640_817,
        2030: 33_777_190,
        2035: 37_893_818,
        2040: 42_208_003,
        2045: 46_629_039,
        2050: 51_096_317,
    })

    # Annual growth rates calculated from UN data
    ANNUAL_GROWTH_RATES: Dict[str, float] = field(default_factory=lambda: {
        "2000-2005": 0.0274,
        "2005-2010": 0.0287,
        "2010-2015": 0.0297,
        "2015-2020": 0.0286,
        "2020-2025": 0.0268,
        "2025-2030": 0.0248,
        "2030-2035": 0.0233,
        "2035-2040": 0.0218,
        "2040-2045": 0.0201,
        "2045-2050": 0.0185,
    })

    # Growth rates for 5-year periods
    GROWTH_RATES: Dict[str, float] = field(default_factory=lambda: {
        "2005-2010": 0.0287,
        "2010-2015": 0.0297,
        "2015-2020": 0.0286,
        "2020-2025": 0.0268,
    })

    # Regional growth multipliers (base = 1.0)
    REGIONAL_MULTIPLIERS: Dict[str, float] = field(default_factory=lambda: {
        "CENTRE": 1.12,
        "LITTORAL": 1.15,
        "OUEST": 1.08,
        "SUD": 1.05,
        "EST": 1.08,
        "ADAMAOUA": 1.02,
        "NORD": 1.03,
        "EXTREME-NORD": 1.04,
        "SUD-OUEST": 0.98,
        "NORD-OUEST": 0.97,
    })

    # Department-level population totals (2005 census)
    DEPT_POPULATION_2005: Dict[str, int] = field(default_factory=lambda: {
        "DJEREM": 124948, "FARO ET DEO": 82717, "MAYO BANYO": 187066,
        "MBERE": 171670, "VINA": 317888, "HAUTE-SANAGA": 100352,
        "LEKIE": 286050, "MBAM ET INOUBOU": 188927, "MBAM ET KIM": 105511,
        "MEFOU ET AFAMBA": 126025, "MEFOU ET AKONO": 59017, "MFOUNDI": 188187,
        "NYONG ET KELLE": 129819, "NYONG ET MFOUMOU": 104507, "NYONG ET SO'O": 115960,
        "BOUMBA ET NGOKO": 115354, "HAUT NYONG": 196519, "KADEY": 184098,
        "LOM ET DJEREM": 275784, "DIAMARE": 642227, "LOGONE ET CHARI": 486997,
        "MAYO DANAY": 529061, "MAYO KANI": 404646, "MAYO SAVA": 348890,
        "MAYO TSANAGA": 699971, "MOUNGO": 379241, "NKAM": 36730,
        "SANAGA MARITIME": 162315, "WOURI": 193197, "BENOUE": 85195,
        "FARO": 69477, "MAYO LOUTI": 391326, "MAYO REY": 375201,
        "BOYO": 124887, "BUI": 321969, "DONGA MANTUNG": 269931,
        "MENCHUM": 161998, "MEZAM": 524127, "MOMO": 138693,
        "NGO KETUNJIA": 187348, "BAMBOUTOS": 213838, "HAUT-NKAM": 129323,
        "HAUTS-PLATEAUX": 104678, "KOUNG-KHI": 67021, "MENOUA": 289105,
        "MIFI": 319862, "NDE": 95292, "NOUN": 160169, "DJA ET LOBO": 199485,
        "MVILA": 218734, "OCEAN": 115397, "VALLEE DU NTEM": 88596,
        "FAKO": 294709, "KUPE ET MANENGUBA": 125443, "LEBIALEM": 113736,
        "MANYU": 155011, "MEME": 257343, "NDIAN": 99917
    })

    # Years for simulation
    YEARS: List[int] = field(default_factory=lambda: [2005, 2010, 2015, 2020, 2025])

    # Validation thresholds
    MAX_POPULATION_GROWTH_FACTOR: float = 2.5
    MIN_POPULATION_GROWTH_FACTOR: float = 0.7

    # Postal code configuration
    POSTAL_CODE_DIGITS: int = 5
    ALLOWED_DIGITS: List[int] = field(default_factory=lambda: list(range(1, 10)))

    DEPARTMENT_MAP: Dict[str, str] = {
            # Adamawa (5 departments)
            "DJEREM": "Adamawa", "FARO ET DEO": "Adamawa", "MAYO BANYO": "Adamawa",
            "MBERE": "Adamawa", "VINA": "Adamawa",
            # Centre (10 departments)
            "HAUTE-SANAGA": "Centre", "LEKIE": "Centre", "MBAM ET INOUBOU": "Centre",
            "MBAM ET KIM": "Centre", "MEFOU ET AFAMBA": "Centre", "MEFOU ET AKONO": "Centre",
            "MFOUNDI": "Centre", "NYONG ET KELLE": "Centre", "NYONG ET MFOUMOU": "Centre",
            "NYONG ET SO'O": "Centre",
            # East (4 departments)
            "BOUMBA ET NGOKO": "East", "HAUT NYONG": "East", "KADEY": "East", "LOM ET DJEREM": "East",
            # Extreme-Nord (6 departments)
            "DIAMARE": "Extreme-Nord", "LOGONE ET CHARI": "Extreme-Nord", "MAYO DANAY": "Extreme-Nord",
            "MAYO KANI": "Extreme-Nord", "MAYO SAVA": "Extreme-Nord", "MAYO TSANAGA": "Extreme-Nord",
            # Littoral (4 departments)
            "MOUNGO": "Littoral", "NKAM": "Littoral", "SANAGA MARITIME": "Littoral", "WOURI": "Littoral",
            # North (4 departments)
            "BENOUE": "North", "FARO": "North", "MAYO LOUTI": "North", "MAYO REY": "North",
            # Northwest (7 departments)
            "BOYO": "Northwest", "BUI": "Northwest", "DONGA MANTUNG": "Northwest",
            "MENCHUM": "Northwest", "MEZAM": "Northwest", "MOMO": "Northwest", "NGO KETUNJIA": "Northwest",
            # West (8 departments)
            "BAMBOUTOS": "West", "HAUT-NKAM": "West", "HAUTS-PLATEAUX": "West",
            "KOUNG-KHI": "West", "MENOUA": "West", "MIFI": "West", "NDE": "West", "NOUN": "West",
            # South (4 departments)
            "DJA ET LOBO": "South", "MVILA": "South", "OCEAN": "South", "VALLEE DU NTEM": "South",
            # Southwest (6 departments)
            "FAKO": "Southwest", "KUPE ET MANENGUBA": "Southwest", "LEBIALEM": "Southwest",
            "MANYU": "Southwest", "MEME": "Southwest", "NDIAN": "Southwest"
        }
    ARRONDISSEMENT_MAP: Dict[str, str] = {
            # Adamawa arrondissements
            "NGAOUNDAL": "DJEREM", "TIBATI": "DJEREM",
            "GALIM TIGNERE": "FARO ET DEO", "MAYO BALEO": "FARO ET DEO", "KONTCHA": "FARO ET DEO", "TIGNERE": "FARO ET DEO",
            "BANKIM": "MAYO BANYO", "BANYO": "MAYO BANYO", "MAYO-DARLE": "MAYO BANYO",
            "DIR": "MBERE", "DJOHONG": "MBERE", "NGAOUI": "MBERE", "MEIGANGA": "MBERE",
            "BELEL": "VINA", "MBE": "VINA", "NGAOUNDERE I": "VINA", "NGAOUNDERE II": "VINA",
            "NGAOUNDERE III": "VINA", "MARTAP": "VINA", "NGAN-HA": "VINA", "NYAMBAKA": "VINA",

            # Centre arrondissements
            "BIBEY": "HAUTE-SANAGA", "LEMBE YEZOUM": "HAUTE-SANAGA", "MBANDJOCK": "HAUTE-SANAGA",
            "MINTA": "HAUTE-SANAGA", "NANGA-EBOKO": "HAUTE-SANAGA", "NKOTENG": "HAUTE-SANAGA", "NSEM": "HAUTE-SANAGA",
            "BATSCHENGA": "LEKIE", "EBEBDA": "LEKIE", "ELIG-MFOMO": "LEKIE", "EVODOULA": "LEKIE",
            "LOBO": "LEKIE", "MONATELE": "LEKIE", "OBALA": "LEKIE", "OKOLA": "LEKIE", "SA'A": "LEKIE",
            "BAFIA": "MBAM ET INOUBOU", "BOKITO": "MBAM ET INOUBOU", "DEUK": "MBAM ET KIM",
            "KIIKI": "MBAM ET KIM", "KON-YAMBETTA": "MBAM ET KIM", "MAKENENE": "MBAM ET KIM",
            "NDIKINIMEKI": "MBAM ET KIM", "NITOUKOU": "MBAM ET KIM", "OMBESSA": "MBAM ET KIM",
            "MBANGASSINA": "MEFOU ET AFAMBA", "NGAMBE-TIKAR": "MEFOU ET AFAMBA", "NGORO": "MEFOU ET AFAMBA",
            "NTUI": "MEFOU ET AFAMBA", "YOKO": "MEFOU ET AFAMBA",
            "AFANLOUM": "MEFOU ET AKONO", "ASSAMBA": "MEFOU ET AKONO", "AWAE": "MEFOU ET AKONO",
            "EDZENDOUAN": "MEFOU ET AKONO", "ESSE": "MEFOU ET AKONO", "MFOU": "MEFOU ET AKONO",
            "NKOLAFAMBA": "MEFOU ET AKONO", "SOA": "MEFOU ET AKONO",
            "AKONO": "NYONG ET MFOUMOU", "BIKOK": "NYONG ET MFOUMOU", "MBANKOMO": "NYONG ET MFOUMOU",
            "NGOUMOU": "NYONG ET MFOUMOU",
            "YAOUNDE I": "MFOUNDI", "YAOUNDE II": "MFOUNDI", "YAOUNDE III": "MFOUNDI",
            "YAOUNDE IV": "MFOUNDI", "YAOUNDE V": "MFOUNDI", "YAOUNDE VI": "MFOUNDI", "YAOUNDE VII": "MFOUNDI",
            "BIYOUHA": "NYONG ET KELLE", "BONDJOCK": "NYONG ET KELLE", "BOT-MAKAK": "NYONG ET KELLE",
            "DIBANG": "NYONG ET KELLE", "ESEAK": "NYONG ET KELLE", "MAKAK": "NYONG ET KELLE",
            "MATOMB": "NYONG ET KELLE", "MESSONDO": "NYONG ET KELLE", "NGUIBASSAL": "NYONG ET KELLE",
            "NGOG MAPUBI": "NYONG ET KELLE",
            "AKOEMAN": "NYONG ET SO'O", "AKONOLINGA": "NYONG ET SO'O", "AYOS": "NYONG ET SO'O",
            "ENDOM": "NYONG ET SO'O", "MENGANG": "NYONG ET SO'O", "NYAKOKOMBO": "NYONG ET SO'O",
            "DZENG": "MBAM ET KIM", "MBALMAYO": "NYONG ET SO'O", "MENGUEME": "NYONG ET SO'O",
            "NGOMEDZAP": "NYONG ET SO'O", "NKOLMETET": "NYONG ET SO'O",

            # East arrondissements
            "GARI GOMBO": "BOUMBA ET NGOKO", "MOLOUNDOU": "BOUMBA ET NGOKO",
            "SALAPOUMBE": "BOUMBA ET NGOKO", "YOKADOUMA": "BOUMBA ET NGOKO",
            "ABONG-MBANG": "HAUT NYONG", "BEBEND": "HAUT NYONG", "DIMAKO": "HAUT NYONG",
            "DJA": "HAUT NYONG", "DOUMAINTANG": "HAUT NYONG", "DOUME": "HAUT NYONG",
            "LOMIE": "HAUT NYONG", "MBOANZ": "HAUT NYONG", "MBOMA": "HAUT NYONG",
            "MESSAMENA": "HAUT NYONG", "MESSOK": "HAUT NYONG", "NGOYLA": "HAUT NYONG",
            "NGUELEMENDOUKA": "HAUT NYONG", "SOMALOMO": "HAUT NYONG",
            "BATOURI": "KADEY", "BOMBE": "KADEY", "KETTE": "KADEY", "MBANG": "KADEY",
            "MBOTORO": "KADEY", "NDEM-NAM": "KADEY", "NDELELE": "KADEY",
            "BELABO": "LOM ET DJEREM", "BERTOUA I": "LOM ET DJEREM", "BERTOUA II": "LOM ET DJEREM",
            "BETARE-OYA": "LOM ET DJEREM", "DIANG": "LOM ET DJEREM",
            "GAROUA-BOULAI": "LOM ET DJEREM", "MANDJOU": "LOM ET DJEREM", "NGOURA": "LOM ET DJEREM",

            # Extreme-Nord arrondissements
            "BOGO": "DIAMARE", "GAZAWA": "DIAMARE", "MAROUA I": "DIAMARE",
            "MAROUA II": "DIAMARE", "MAROUA III": "DIAMARE", "MERI": "DIAMARE",
            "DARGALA": "DIAMARE", "NDOUKOULA": "DIAMARE", "PETTE": "DIAMARE",
            "BLANGOUA": "LOGONE ET CHARI", "DARAK": "LOGONE ET CHARI",
            "FOTOKOL": "LOGONE ET CHARI", "GOULFEY": "LOGONE ET CHARI",
            "HILE-ALIFA": "LOGONE ET CHARI", "KOUSSERI": "LOGONE ET CHARI",
            "LOGONE BIRNI": "LOGONE ET CHARI", "ZINA": "LOGONE ET CHARI",
            "MAKARI": "MAYO DANAY", "WAZA": "MAYO DANAY", "DATCHEKA": "MAYO DANAY",
            "GOBO": "MAYO DANAY", "GUERE": "MAYO DANAY", "KAI-KAI": "MAYO DANAY",
            "KALFOU": "MAYO KANI", "KARHAY": "MAYO KANI", "MAGA": "MAYO KANI",
            "TCHATIBALI": "MAYO KANI", "VELE": "MAYO KANI", "WINA": "MAYO KANI",
            "YAGOUA": "MAYO KANI", "GUIDIGUIS": "MAYO SAVA", "KAELE": "MAYO SAVA",
            "MINDIF": "MAYO SAVA", "MOULVOUDAYE": "MAYO SAVA", "MOUTOURWA": "MAYO SAVA",
            "PORHI": "MAYO SAVA", "TAIBONG": "MAYO SAVA", "KOLOFATA": "MAYO TSANAGA",
            "MORA": "MAYO TSANAGA", "TOKOMBERE": "MAYO TSANAGA", "BOURHA": "MAYO TSANAGA",
            "HINA": "MAYO TSANAGA", "KOZA": "MAYO TSANAGA", "MAYO-MOSKOTA": "MAYO TSANAGA",
            "MOGODE": "MAYO TSANAGA", "MOKOLO": "MAYO TSANAGA", "SOULEDE ROUA": "MAYO TSANAGA",

            # Littoral arrondissements
            "BARE-BAKEM": "MOUNGO", "DIBOMBARI": "MOUNGO", "ABO": "MOUNGO",
            "LOUM": "MOUNGO", "MANJO": "MOUNGO", "MBANGA": "MOUNGO",
            "MOMBO": "MOUNGO", "MELONG": "MOUNGO", "NJOMBE-PENJA": "MOUNGO",
            "NKONGSAMBA I": "MOUNGO", "NKONGSAMBA II": "MOUNGO", "NKONGSAMBA III": "MOUNGO",
            "NLONAKO": "MOUNGO", "NKONDJOCK": "NKAM", "NORD MAKOMBE": "NKAM",
            "YABASSI": "NKAM", "YINGUI": "NKAM", "DIZANGUE": "SANAGA MARITIME",
            "EDEA I": "SANAGA MARITIME", "EDEA II": "SANAGA MARITIME", "MOUANKO": "SANAGA MARITIME",
            "NDOM": "SANAGA MARITIME", "NYANON": "SANAGA MARITIME", "NGAMBE": "SANAGA MARITIME",
            "MASSOK-SONGLOULOU": "SANAGA MARITIME", "POUMA": "SANAGA MARITIME",
            "DIBAMBA": "WOURI", "NGWEI": "WOURI", "DOUALA I": "WOURI",
            "DOUALA II": "WOURI", "DOUALA III": "WOURI", "DOUALA IV": "WOURI",
            "DOUALA V": "WOURI", "DOUALA VI": "WOURI", "MANOKA": "WOURI",

            # North arrondissements
            "BIBEMI": "BENOUE", "DEMBO": "BENOUE", "LAGDO": "BENOUE",
            "GAROUA I": "BENOUE", "GAROUA II": "BENOUE", "GAROUA III": "BENOUE",
            "BASCHEO": "BENOUE", "DEMSA": "BENOUE", "TOUROUA": "BENOUE",
            "PITOA": "BENOUE", "TCHEBOA": "BENOUE", "MAYO HOURNA": "BENOUE",
            "BEKA": "FARO", "POLI": "FARO", "FIGUIL": "MAYO LOUTI",
            "GUIDER": "MAYO LOUTI", "MAYO OULO": "MAYO LOUTI", "REY-BOUBA": "MAYO LOUTI",
            "TCHOLLIRE": "MAYO LOUTI", "MADINGRING": "MAYO REY", "TOUBORO": "MAYO REY",

            # Northwest arrondissements (partial - add more as needed)
            "BELO": "BOYO", "BUM": "BOYO", "FUNDONG": "BOYO", "NJINIKOM": "BOYO",
            "JAKIRI": "BUI", "KUMBO": "BUI", "MBVEN": "BUI", "NONI": "BUI", "OKU": "BUI",
            "AKO": "DONGA MANTUNG", "MISAJE": "DONGA MANTUNG", "NDU": "DONGA MANTUNG",
            "NKAMBE": "DONGA MANTUNG", "NWA": "DONGA MANTUNG", "FUNGOM": "MENCHUM",
            "FURU-AWA": "MENCHUM", "MENCHUM VALLEY": "MENCHUM", "WUM": "MENCHUM",
            "BAFUT": "MEZAM", "BALI": "MEZAM", "BAMENDA 1": "MEZAM", "BAMENDA 2": "MEZAM",
            "BAMENDA 3": "MEZAM", "SANTA": "MEZAM", "TUBAH": "MEZAM",
            "BATIBO": "MOMO", "MBENGWI": "MOMO", "NGIE": "MOMO", "NJIKWA": "MOMO",
            "WIDIKUM-MENKA": "MOMO", "BABESSI": "NGO KETUNJIA", "BALIKUMBAT": "NGO KETUNJIA", "NDOP": "NGO KETUNJIA",

            # West arrondissements
            "BABADJOU": "BAMBOUTOS", "BATCHAM": "BAMBOUTOS", "GALIM": "BAMBOUTOS", "MBOUDA": "BAMBOUTOS",
            "BAFANG": "HAUT-NKAM", "BAKOU": "HAUT-NKAM", "BANA": "HAUT-NKAM", "BANDJA": "HAUT-NKAM",
            "KEKEM": "HAUT-NKAM", "BANWA": "HAUTS-PLATEAUX", "BANKA": "HAUTS-PLATEAUX",
            "BAHAM": "HAUTS-PLATEAUX", "BAMENDJOU": "HAUTS-PLATEAUX", "BATIE": "HAUTS-PLATEAUX",
            "BANGOU": "KOUNG-KHI", "BAYANGAM": "KOUNG-KHI", "POUMOUGNE": "KOUNG-KHI",
            "DJEBEM": "MENOUA", "DSCHANG": "MENOUA", "FOKOUE": "MENOUA", "NKONG-NI": "MENOUA",
            "PENKA-MICHEL": "MENOUA", "SANCHOU": "MENOUA", "FONGO TONGO": "MIFI",
            "BAFOUSSAM I": "MIFI", "BAFOUSSAM II": "MIFI", "BAFOUSSAM III": "MIFI",
            "BANGANGTE": "NDE", "BASSAMBA": "NDE", "BAZOU": "NDE", "TONGA": "NDE",
            "BANGOURAIN": "NOUN", "FOUMBAN": "NOUN", "FOUMBOT": "NOUN", "KOUOPTAMO": "NOUN",
            "KOUTABA": "NOUN", "MAGBA": "NOUN", "MALENTOUEN": "NOUN", "MASSANGAM": "NOUN", "NJIMOM": "NOUN",

            # South arrondissements
            "BENGBIS": "DJA ET LOBO", "DJOUM": "DJA ET LOBO", "MEYOMESSALA": "DJA ET LOBO",
            "MINTOM": "DJA ET LOBO", "OVENG": "DJA ET LOBO", "SANGMELIMA": "DJA ET LOBO",
            "ZOETELE": "DJA ET LOBO", "MEYOMESSI": "MVILA", "BIWONG-BANE": "MVILA",
            "BIWONG-BULU": "MVILA", "EBOLOWA I": "MVILA", "EBOLOWA II": "MVILA",
            "EFOULAN": "MVILA", "MENGONG": "MVILA", "MVANGAN": "MVILA", "NGOULEMAKONG": "MVILA",
            "AKOM II": "OCEAN", "NIETE": "OCEAN", "BIPINDI": "OCEAN", "CAMPO": "OCEAN",
            "KRIBI I": "OCEAN", "KRIBI II": "OCEAN", "LOKOUNDJE": "OCEAN", "LOLODORF": "OCEAN",
            "MVENGUE": "OCEAN", "AMBAM": "VALLEE DU NTEM", "MA'AN": "VALLEE DU NTEM",
            "OLAMZE": "VALLEE DU NTEM", "KYE OSSI": "VALLEE DU NTEM",

            # Southwest arrondissements
            "BUEA": "FAKO", "WEST COAST": "FAKO", "LIMBE I": "FAKO", "LIMBE II": "FAKO",
            "LIMBE III": "FAKO", "MUYUKA": "FAKO", "TIKO": "FAKO", "BANGEM": "KUPE ET MANENGUBA",
            "NGUTI": "KUPE ET MANENGUBA", "TOMBEL": "KUPE ET MANENGUBA", "ALOU": "LEBIALEM",
            "FONTEM": "LEBIALEM", "WABANE": "LEBIALEM", "AKWAYA": "MANYU", "EYUMODJOCK": "MANYU",
            "MAMFE CENTRAL": "MANYU", "UPPER BANYANG": "MANYU", "KUMBA I": "MEME",
            "KUMBA II": "MEME", "KUMBA III": "MEME", "KONYE": "MEME", "MBONGE": "MEME",
            "BAMUSSO": "NDIAN", "EKONDO-TITI": "NDIAN", "DIKOMBA BALUE": "NDIAN",
            "IDABATO": "NDIAN", "ISANGELE": "NDIAN", "KOMBO ABEDIMO": "NDIAN",
            "KOMBO ITINDI": "NDIAN", "MUNDEMBA": "NDIAN", "TOKO": "NDIAN",
        }


# Create config instance
config = Config()

# Ensure output directory exists
try:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"⚠️ Could not create output directory: {e}")

# Print configuration info for debugging
print("=" * 70)
print("✅ Configuration Loaded Successfully!")
print("=" * 70)
print(f"📁 Project root: {config.BASE_DIR}")
print(f"📁 Data directory: {config.DATA_DIR}")
print(f"📁 External data: {config.EXTERNAL_DIR}")
print(f"📁 Output directory: {config.OUTPUT_DIR}")
print("=" * 70)
print("\n📊 POPULATION DATA SUMMARY:")
print(f"   • 2005 Arrondissements: {len(config.ARRONDISSEMENT_POPULATION_2005):,}")
print(f"   • 2010 Arrondissements: {len(config.ARRONDISSEMENT_POPULATION_2010):,}")
print(f"   • UN 2005 Population: {config.NATIONAL_POPULATION[2005]:,}")
print(f"   • UN 2010 Population: {config.NATIONAL_POPULATION[2010]:,}")
print(f"   • UN 2025 Population: {config.NATIONAL_POPULATION[2025]:,}")
print("=" * 70)

# Verify critical paths exist
if not config.ADM1_FILE.exists():
    print(f"⚠️ Warning: ADM1 file not found at {config.ADM1_FILE}")
if not config.WOF_LOCALITY_SHP.exists():
    print(f"⚠️ Warning: WOF shapefile not found at {config.WOF_LOCALITY_SHP}")