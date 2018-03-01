# coding: utf-8

import pandas as pd
import numpy as np
import random
import string
import math

from tmtk.study import Study

the_bio_glossary = [
    "Abscisic acid", "Abscission", "Absolute zero", "Absorption (skin)", "Absorption spectrum",
    "Abyssal zone", "Acclimatization", "Acid precipitation", "Acoelomate", "Actin", "Action potential",
    "Activation energy", "Active site", "Active transport", "Autotrophic", "Adenosine triphosphate",
    "Adenylate cyclase", "Aerobic organism", "Aerobiology", "Agriculture", "Agrobiology", "Amino acid",
    "Amniote", "Anatomy", "Aneuploidy", "Antibiotic", "Transfer RNA", "Anticodon", "Arachnology",
    "Selective breeding", "Asexual reproduction", "Astrobiology", "Atom", "Autoimmunity", "B cell",
    "Bacteria", "Bacteriophage", "Barr body", "Basal body", "Behavioral ecology", "Benthic zone", "Bile",
    "Fission", "Biocatalysis", "Biochemistry", "Biodiversity", "Bioengineering", "Bioenergetics",
    "Biogeography", "Bioinformatics", "Biological organization", "Biology", "Biomass", "Biomathematics",
    "Biome", "Biomechanics", "Biomedical engineering", "Biomedical research", "Biomimetic", "Biomolecule",
    "Bionics", "Biophysics", "Biotechnology", "Bipedal", "Blastocyst", "Blood", "Blood-brain barrier", "Botany",
    "Bowman's capsule", "Building biology", "Light-independent reactions", "Coupling to other metabolic pathways",
    "Capsid", "Carbon fixation", "Carbonate", "Cell", "Cell biology", "Cell membrane", "Cell nucleus",
    "Cell plate", "Cell theory", "Centriole", "Centroid", "Centrosome", "Chemical bond", "Chemical compound",
    "Chemical equilibrium", "Chemical kinetics", "Chemical reaction", "Chemistry", "Chloride", "Chloroplast",
    "Cholesterol", "Chromate", "Chromosome", "Cloning", "Conservation biology", "Cryobiology",
    "Cyclin-dependent kinase", "Cytosine", "Dalton", "Darwinian fitness", "Deciduous",
    "Dehydration reaction", "Denaturation", "Dendrite", "Denitrification", "Deoxyribonucleic acid",
    "Deoxyribose", "Depolarization", "Desmosome", "DNA", "DNA replication", "DNA sequencing", "Dynein", "Ecdysone",
    "Ecological efficiency", "Ecological niche", "Ecological pyramid", "Ecological succession", "Ecology",
    "Ecophysiology", "Ecosystem", "Ecotype", "Ectoderm", "Ectotherm", "Effector", "Plasma cell",
    "Efferent", "Egg", "Electric potential", "Electrochemical gradient", "Electromagnetic spectrum",
    "Electron", "Electron acceptor", "Electron carrier", "Electron donor", "Electron microscope", "Electron shell",
    "Electron transport chain", "Electronegativity", "Chemical element", "Embryo", "Embryo sac", "Embryology",
    "Enantiomer", "Endangered species", "Endemism", "Endemic species", "Endergonic reaction", "Endocrine gland",
    "Endocrine system", "Endocytosis", "Endoderm", "Endodermis", "Endoplasmic reticulum", "Endosperm",
    "Endosymbiotic theory", "Endotherm", "Entomology", "Environmental biology", "Enzyme", "Epicotyl",
    "Epidemiology", "Epigenetics", "Epinephrine", "Epiphyte", "Epistasis", "Estrogen", "Ethology", "Eukaryote",
    "Evolution", "Evolutionary biology", "Exocytosis", "Exon", "Exponential growth", "Expressivity (genetic)",
    "External fertilization", "Facultative anaerobic organism", "Foetus", "FIRST", "Food chain", "Founder effect",
    "Ganglion ", "Gene", "Gene pool", "Genetic code", "Genetic drift", "Genetics", "Genetic variation", "Genome",
    "Guanine", "Gular", "Habitat", "Hadron", "Hermaphrodite", "Herpetology", "Heterosis", "Histology",
    "Hormone", "Human nutrition", "Hydrocarbon", "Ichthyology", "Immune response", "Immunogloblin",
    "Incomplete dominance", "Insulin", "Interferon", "Integrative biology", "Interleukin", "Internal fertilization",
    "International System of Units", "Invertebrate", "Ion", "Ionic bond", "Isomer", "Isotonic solutions",
    "Isotope", "Jejunum", "Krebs cycle", "Lacteal", "Lagging strand", "Larva", "Law of independent assortment",
    "Lepton", "Leukocyte", "Ligament", "Light-independent reactions", "Linked genes", "Lipid", "Lipoprotein",
    "M phase", "Macroevolution", "Macromolecule", "Macronutrient", "Macrophage", "Mammalogy", "Marine biology",
    "Mass balance", "Mass density", "Mass number", "Mast cell", "Medulla oblongata", "Meiosis", "Membrane potential",
    "Meson", "Messenger RNA", "Metaphase", "Microbiology", "Microevolution", "Microtome", "Mitosis", "Molarity",
    "Mole", "Molecule", "Molecular biology", "Molecular physics", "Monomer", "Motor neuron", "Mucous membrane",
    "Multicellular organism", "Muon", "Mycology", "Myofibril", "Myosin", "Natural selection", "Neurobiology",
    "Neuromuscular junction", "Neuron", "Neurotransmitter", "Neutrino", "Nucleic acid", "Nucleic acid sequence",
    "Nucleobase", "Nucleoid", "Nucleolus", "Nucleotide", "Organ", "Organism", "Oncology", "Ornithology",
    "Osmosis", "Paleontology", "Parallel evolution", "Parasitology", "Pathobiology", "Pathology", "pH", "Pharmacology",
    "Phenotype", "Pheromone", "Phloem", "Physiology", "Phytochemistry", "Phytopathology", "Placebo", "Plant nutrition",
    "Plasmolysis", "Pollination", "Polygene", "Polymer", "Polymerase chain reaction", "Polyploid",
    "Population biology", "Population ecology", "Population genetics", "Predation", "Primase", "Progesterone",
    "Prokaryote", "Protein", "Psychobiology", "Quark", "Reproduction", "RNA", "Sexual reproduction", "SI units",
    "Sociobiology", "Soil biology", "Soil microbiology", "Species", "Speciation", "Stem cell", "Steroid",
    "Structural biology", "Symbiogenesis", "Synthetic biology", "Systematics", "T cell", "Testosterone", "Thymine",
    "Transcription", "Transfer RNA", "Translation", "Trophic level", "Unicellular organism",
    "Uracil", "Urea", "Uric acid", "Urine", "Uterus", "Vacuole", "Valence", "Valence band",
    "Valence bond theory", "Valence electron", "Valence shell", "Vasodilation", "Vegetative reproduction",
    "Vesicle", "Vestigiality", "Virology", "Virus", "Water potential", "White Blood Cell",
    "Whole genome sequencing", "Wobble base pair", "Wood", "Xanthophyll", "Xylem", "Yeast artificial chromosome",
    "Yolk", "Zoology", "Zygote", "Biology"]

the_space_glossary = [
    "Absolute magnitude", "Accretion disk", "Active galactic nucleus", "Albedo feature", "metallicity",
    "Apoapsis", "Earth's atmosphere", "Appulse", "Asterism ", "spectroscopic binary",
    "Astronomical unit", "North Pole", "spherical coordinate system", "event horizon", "deuterium",
    "spherical astronomy", "electromagnetic spectrum", "Comet tail", "Jupiter",
    "International Astronomical Union", "celestial equator", "Double star", "brown dwarf",
    "late-type star", "Orbital eccentricity", "axial tilt", "electromagnetic radiation",
    "stellar evolution", "attenuation", "field galaxy", "gravitational field", "Lambertian",
    "interstellar cloud", "Mars", "Interstellar medium", "red shift", "evolutionary track",
    "Jeans instability", "solar wind", "hydrogen-1", "Meteor", "meteorite", "Meteor shower", "Metallicity",
    "comet", "molecular hydrogen", "celestial body", "Moving group", "star cluster", "subatomic particle",
    "Number density", "OB association", "Convection zone", "molecular cloud",
    "Opposition", "Orbital elements", "Astronomical Unit", "Periapsis", "Jupiter",
    "Planetary differentiation", "general relativity", "Proper motion", "pre-main-sequence star",
    "Beta Cephei variable", "celestial equator", "Coalescence", "optical depth",
    "Keplerian orbit", "radial velocity", "Starfield", "Stellar atmosphere",
    "MK spectral classification", "Ptolemy", "Synodic period", "Syzygy",
    "Retrograde motion", "Tidal locking", "occultation", "North Pole", "Type Ia supernova", "Zenith",
]

the_wrestling_glossary = [
    "A-show", "A-team", "Abort", "Ace", "Agent", "Alliance", "Angle", "Apter mag", "B-show", "B-team",
    "Babyface", "Beat down", "Blading", "Blind tag", "Blown spot", "Blow off", "Blow up", "Book", "Botch",
    "Bump", "Burial", "Business", "Bust open", "C-show", "Call", "Card", "Carry", "Championship advantage",
    "Cheap heat", "Cheap pop", "Cheap shot", "Clean finish", "Clean wrestling", "Closet champion", "Color",
    "Comeback", "Crimson mask", "Cross-promotion", "Dark match", "Deathmatch wrestling", "Dirt sheet",
    "Double team", "Double turn", "Draw", "Drop", "Dusty finish", "Enforcer", "Face",
    "Face-in-peril (also playing Ricky Morton)", "Face of the company", "Fall", "Fallout show",
    "False comeback", "False finish", "Feud", "Fighting champion", "Finish", "Finisher", "Five moves of doom",
    "Foreign object", "Gas", "Gassed", "Gig", "Gimmick", "Glorified jobber", "Go away heat", "Go home",
    "Go-home show", "Going into business for him/herself", "Gold", "Go over", "Gorilla position", "Green",
    "Gusher", "Hardcore wrestling", "Hardway", "Head drop", "Heat", "Heel", "Highspot", "Hollywood",
    "Hooker", "Hoss", "Hotshot", "Hot tag", "House", "House show", "Impromptu match",
    "independent promotion (also indie promotion)", "Interbrand", "Interpromotional", "Interference",
    "Invasion storyline", "IWC", "Jerk the curtain", "Job", "Jobber", "Jobber to the stars", "Juice",
    "Jumping ship", "Kayfabe", "Kick-out", "Legit", "Lemon", "Lock up (also link up)", "Low-carder",
    "Lumberjack (m)", "Lumberjill (f)", "Lucha libre", "Lucharesu", "Main event", "Manager", "Mark", "Mechanic",
    "Mid-carder", "Missed spot", "Money mark", "Money match", "Monster", "Mouthpiece", "Muta scale", "Near-fall",
    "No contest", "No-sell", "No-show", "Nuclear heat", "Number one contender", "Over", "Over-sell", "Paper",
    "Paper champion", "Parts Unknown", "Payoff", "Payralbe Extreme", "Pinfall", "Pipe bomb", "Plant", "Policeman",
    "Pop", "Potato", "Powdering", "Program", "Promo", "Pull apart", "Put Over", "Puroresu", "Push",
    "Rasslin (also wrasslin, Southern style, or more specifically, Memphis style)", "Receipt",
    "Ref bump", "Rematch (or return) clause", "Repackage", "Rest hold", "Rib", "Ring general",
    "Ring psychology", "Ring rat", "Ring rust", "Rub", "Run-in", "Rushed finish", "Sandbag", "Schmoz",
    "School", "Screwjob", "Sell", "Shoot", "Shoot style", "Signature move", "Skit", "Slow burn",
    "Smark", "Smart", "Snug", "Spot", "Spotfest", "Squared circle", "Squash", "Stable", "Stiff",
    "Sting money", "Strap", "Stretching", "Strike", "Strong style", "Swerve", "Tap out", "Tease",
    "TitanTron", "Transitional champion", "Turn", "Tweener", "Unified", "Vacant", "Valet", "Vanilla Midget",
    "Vignette", "Visual fall", "Work (noun)", "Work (verb)", "Worker", "Worked shoot", "Workrate",
    "Wrestlers Court", "X Division", "X signal", "X-Pac heat", "Young lion"
]


class RandomNormal:
    def __init__(self, mean, sigma, around=False):
        self.mean = mean
        self.sigma = sigma
        self.round = around

    def pick(self, x):
        array = pd.Series(np.random.normal(self.mean, self.sigma, x))
        if self.round:
            array = array.astype(int)
        return array

    def __repr__(self):
        return '<(RandomNormal(mean={}, sigma={})>'.format(self.mean, self.sigma)


class RandomChoice:
    def __init__(self, choices, probabilities=None):
        self.choices = choices
        self.probabilities = probabilities

    def pick(self, x):
        return pd.Series(np.random.choice(a=self.choices, size=x, p=self.probabilities))

    def __repr__(self):
        return '<(RandomChoice(choices={}, probabilities={})>'.format(self.choices, self.probabilities)


class RandomStudy(Study):

    def __init__(self, subjects=0, numerical=0, categorical=0, max_depth=None, sparsity: float=0.0):
        """
        Creates a randomly generated study.

        :param subjects:
        :param numerical:
        :param categorical:
        :param max_depth:
        :param float sparsity:
        """
        super().__init__()
        self._n_subjects = subjects
        self.study_id = 'RANDOM_STUDY_{}'.format(random.randint(1000, 9999))
        self._ids = {'SUBJ_ID', 'AGE', 'GENDER', 'RACE'}
        self._subject_ids = ["{}_SUBJECT{}".format(self.study_id, i) for i in range(self._n_subjects)]
        self._max_depth = max_depth
        self._sparsity = sparsity
        total_columns = numerical + categorical
        proportion_numerical = numerical / total_columns

        step_size = 500
        steps_n = int(math.ceil(total_columns / step_size))

        print('Files to create: {}'.format(steps_n))
        for i in range(steps_n):
            columns_for_file = min(total_columns - step_size * i, step_size)
            numerical = int(math.ceil(proportion_numerical * columns_for_file))
            categorical = int(math.ceil((1 - proportion_numerical) * columns_for_file))
            first = i == 0

            new_df = self.create_clinical_df(numerical, categorical, first)
            self.Clinical.add_datafile(filename='random_clinical_data{}.tsv'.format(i + 1), dataframe=new_df)
            del new_df

        self.Clinical.apply_blueprint(self._build_blueprint())

    def create_clinical_df(self, numerical=0, categorical=0, first=False):

        clinical_dict = {'SUBJ_ID': ["{}_SUBJECT{}".format(self.study_id, i) for i in range(self._n_subjects)]}

        if numerical and first:
            clinical_dict["AGE"] = RandomNormal(mean=50, sigma=15).pick(self._n_subjects)
            numerical -= 1

        if categorical and first:
            clinical_dict["GENDER"] = RandomChoice(['Male', 'Female'], [0.48, 0.52]).pick(self._n_subjects)
            clinical_dict["RACE"] = RandomChoice(['ELf', 'Smurf', 'Orc', 'Cowboy', 'Android']).pick(self._n_subjects)
            categorical -= 2

        for i in range(numerical):
            series = RandomNormal(mean=random.randint(i+2 * 20, i+2 * 40),
                                  sigma=random.randint(i+1 * 3, i+1 * 5)
                                  ).pick(self._n_subjects)
            clinical_dict[self.new_id()] = series.apply(self._crazy_monkey)

        for i in range(max(categorical, 0)):
            series = RandomChoice(random.sample(the_bio_glossary, random.randint(1, 9))
                                  ).pick(self._n_subjects)
            clinical_dict[self.new_id()] = series.apply(self._crazy_monkey)

        return_df = pd.DataFrame(clinical_dict)

        del clinical_dict
        return return_df

    def new_id(self, size=8):
        new_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
        if new_id not in self._ids:
            self._ids.add(new_id)
            return new_id
        else:
            # try again.
            return self.new_id()

    def _crazy_monkey(self, value):
        """
        Returns input or pd.np.nan, based on chance.
        """
        return value if random.random() > self._sparsity else pd.np.nan

    @staticmethod
    def _get_combined_parent():
        space = random.sample(the_space_glossary, 1)
        wrestling = random.sample(the_wrestling_glossary, 1)

        return " ".join(space + wrestling)

    def _build_blueprint(self):
        """ Generate random concept tree template dictionary for a list of ids """
        path_de_dup = {}
        template_dict = {}

        def get_path_label():
            new_path = random.sample(parents, 1)[0]
            new_label = random.sample(the_bio_glossary, 1)[0]

            if new_label not in path_de_dup.get(new_path, {}):
                try:
                    path_de_dup.get(new_path).add(new_label)
                except AttributeError:
                    path_de_dup[new_path] = {new_label}
                return new_path, new_label
            else:
                return get_path_label()

        if len(set(self._ids)) != len(self._ids):
            raise Exception("Duplicate IDs provided")
        parents = self._build_parents(len(self._ids))
        for _id in self._ids:
            path, label = get_path_label()
            template_dict[_id] = {'path': path,
                                  'label': label
                                  }

        template_dict['GENDER'] = {'path': 'Demographics', 'label': 'Gender'}
        template_dict['AGE'] = {'path': 'Demographics', 'label': 'Age'}
        template_dict['RACE'] = {'path': 'Demographics', 'label': 'Race'}
        template_dict['SUBJ_ID'] = {'path': 'Demographics', 'label': 'SUBJ_ID'}

        return template_dict

    def _build_parents(self, n):
        """ generate random list of parents proportional to n """
        parents = [['']]
        total_parents = int(n / 5 + 1)
        parents_list = [self._get_combined_parent() for _ in range(total_parents)]

        overflow = []

        for parent in parents_list:
            random_pick = random.randint(0, len(parents) - 1)

            append_to = parents[random_pick].copy()

            if self._max_depth and (len(append_to) + 1) > self._max_depth:
                overflow.append(append_to + [parent])
            else:
                # Add create copy and add current path to list of possible parents
                parents.append(append_to + [parent])

        parents += overflow
        parents.remove([''])
        return ['\\'.join(parent) for parent in parents]
