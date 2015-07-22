from sqlalchemy.sql import and_, func, text
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import aliased, backref, deferred, mapper, relationship, reconstructor
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_method

try: from rdkit.Chem import Mol, MolFromSmarts
except ImportError: pass

from credoscript import Base, schema
from credoscript import adaptors as credoadaptor
from credoscript.support import requires

# SHOULD BE WRAPPED IN TRY/EXCEPT
Base.metadata.reflect(schema='chembl')

### CHEMBL DEFAULT TABLES ###

class Activity(Base):
	'''
	'''
	__tablename__ = 'chembl.activities'	
	
	Assay = relationship("Assay",
						 primaryjoin="Assay.assay_id==Activity.assay_id",
						 foreign_keys="[Assay.assay_id]",
						 uselist=False, innerjoin=True,
						 backref=backref('Activities', uselist=True))
	
	Doc = relationship("Doc",
					   primaryjoin="Doc.doc_id==Activity.doc_id",
					   foreign_keys="[Doc.doc_id]",
					   uselist=False, innerjoin=True,
					   backref=backref('Activities', uselist=True))
	
	Record = relationship("CompoundRecord",
						  primaryjoin="CompoundRecord.record_id==Activity.record_id",
						  foreign_keys="[CompoundRecord.record_id]",
						  uselist=False, innerjoin=True,
						  backref=backref('Activities', uselist=True))	

	def __repr__(self):
		'''
		'''
		return '<Activity({self.activity_id})>'.format(self=self)

class Assay(Base):
	'''
	'''
	__tablename__ = 'chembl.assays'
	
	AssayType = relationship("AssayType",
							 primaryjoin="AssayType.assay_type==Assay.assay_type",
							 foreign_keys="[AssayType.assay_type]",
							 uselist=False, innerjoin=True)
	
	Assay2Targets = relationship("Assay2Target",
								 primaryjoin="Assay2Target.assay_id==Assay.assay_id",
								 foreign_keys="[Assay2Target.assay_id]", uselist=True, innerjoin=True,
								 backref='Assay')
	
	Source = relationship("Source",
						  primaryjoin="Source.src_id==Assay.src_id",
						  foreign_keys="[Source.src_id]",
						  uselist=False, innerjoin=True)
	
	Targets = relationship("Target",
						   secondary=Base.metadata.tables['chembl.assay2target'],
						   primaryjoin="Assay.assay_id==Assay2Target.assay_id",
						   secondaryjoin="Target.tid==Assay2Target.tid",
						   foreign_keys="[Assay2Target.assay_id,Assay2Target.tid]",
						   uselist=True, innerjoin=True, backref='Assays')
	
	Doc = relationship("Doc",
					   primaryjoin="Doc.doc_id==Assay.doc_id",
					   foreign_keys="[Doc.doc_id]",
					   uselist=False, innerjoin=True, backref='Assays')	
	
	def __repr__(self):
		'''
		'''
		return '<Assay({self.assay_id})>'.format(self=self)
	
	@property
	def Structures(self):
		'''
		'''
		return credoadaptor.StructureAdaptor().fetch_all_by_pubmed_id(self.Doc.pubmed_id)

class Assay2Target(Base):
	'''
	'''
	__tablename__ = 'chembl.assay2target'
	
	Target = relationship("Target",
						  primaryjoin="Target.tid==Assay2Target.tid",
						  foreign_keys="[Target.tid]",
						  uselist=False, innerjoin=True,
						  backref='Assay2Targets')
	
	Curator = relationship("Curator",
						   primaryjoin="Curator.curated_by==Assay2Target.curated_by",
						   foreign_keys="[Curator.curated_by]",
						   uselist=False, innerjoin=True)
	
	ConfidenceScore = relationship("ConfidenceScore",
								   primaryjoin="ConfidenceScore.confidence_score==Assay2Target.confidence_score",
								   foreign_keys="[ConfidenceScore.confidence_score]",
								   uselist=False, innerjoin=True)
	
	RelationshipType = relationship("RelationshipType",
									primaryjoin="RelationshipType.relationship_type==Assay2Target.relationship_type",
									foreign_keys="[RelationshipType.relationship_type]",
									uselist=False, innerjoin=True)

	def __repr__(self):
		'''
		'''
		return '<Assay2Target({self.assay_id}, {self.tid})>'.format(self=self)

class AssayType(Base):
	'''
	'''
	__tablename__ = 'chembl.assay_type'
	
	def __repr__(self):
		'''
		'''
		return '<AssayType({self.asay_type})>'.format(self=self)

class ATCClassification(Base):
	'''
	'''
	__tablename__ = 'chembl.atc_classification'
	
	DefinedDailyDose = relationship("DefinedDailyDose",
									primaryjoin="DefinedDailyDose.atc_code==ATCClassification.level5",
									foreign_keys="[DefinedDailyDose.atc_code]",
									uselist=False, innerjoin=True)
	
class ChEMBLID(Base):
	'''
	'''
	__tablename__ = 'chembl.chembl_id_lookup'	

class CompoundProperty(Base):
	'''
	'''
	__tablename__ = 'chembl.compound_properties'
	
	Structures = relationship("CompoundStructure",
							  primaryjoin="CompoundStructure.molregno==CompoundProperty.molregno",
							  foreign_keys="[CompoundStructure.molregno]",
							  uselist=True, innerjoin=True,
							  backref='CompoundProperty')
	
	Records = relationship("CompoundRecord",
						   primaryjoin="CompoundRecord.molregno==CompoundProperty.molregno",
						   foreign_keys="[CompoundRecord.molregno]",
						   uselist=True, innerjoin=True,
						   backref='CompoundProperty'),	

	def __repr__(self):
		'''
		'''
		return '<CompoundProperty({self.molregno})>'.format(self=self)

class CompoundRecord(Base):
	'''
	'''
	__tablename__ = 'chembl.compound_records'
	
	Source = relationship("Source",
						  primaryjoin="Source.src_id==CompoundRecord.src_id",
						  foreign_keys="[Source.src_id]",
						  uselist=False, innerjoin=True)
	
	def __repr__(self):
		'''
		'''
		return '<CompoundRecord({self.record_id})>'.format(self=self)

class CompoundStructure(Base):
	'''
	'''
	__tablename__ = 'chembl.compound_structures'
	
	def __repr__(self):
		'''
		'''
		return '<CompoundStructure({self.molregno})>'.format(self=self)

class ConfidenceScore(Base):
	__tablename__ = 'chembl.confidence_score_lookup'	

class Curator(Base):
	__tablename__ = 'chembl.curation_lookup'	

class DefinedDailyDose(Base):
	__tablename__ = 'chembl.defined_daily_dose'	

class Doc(Base):
	'''
	'''
	__tablename__ = 'chembl.docs'
	
	def __repr__(self):
		'''
		'''
		return '<Doc({self.doc_id})>'.format(self=self)
	
	@property
	def Structures(self):
		'''
		'''
		return credoadaptor.StructureAdaptor().fetch_all_by_pubmed_id(self.pubmed_id)

class Formulation(Base):
	'''
	'''
	__tablename__ = 'chembl.formulations'
	
	Product = relationship("Product",
						   primaryjoin="Product.product_id==Formulation.product_id",
						   foreign_keys="[Product.product_id]",
						   uselist=False, innerjoin=True,
						   backref=backref('Formulations', uselist=True))	

	def __repr__(self):
		'''
		'''
		return '<Formulation({self.product_id}, {self.ingredient})>'.format(self=self)

class Molecule(Base):
	'''
	'''
	__tablename__ = 'chembl.molecule_dictionary'
	
	Property = relationship("CompoundProperty",
							primaryjoin="CompoundProperty.molregno==Molecule.molregno",
							foreign_keys="[CompoundProperty.molregno]",
							uselist=False, backref='Molecule')
	
	Records = relationship("CompoundRecord",
						   primaryjoin="CompoundRecord.molregno==Molecule.molregno",
						   foreign_keys="[CompoundRecord.molregno]",
						   uselist=True, backref='Molecule')
	
	Activities = relationship("Activity",
							  collection_class=attribute_mapped_collection("assay_id"),
							  primaryjoin="Activity.molregno==Molecule.molregno",
							  foreign_keys="[Activity.molregno]",
							  uselist=True, backref='Molecule')
	
	Structure = relationship("CompoundStructure",
							 primaryjoin="CompoundStructure.molregno==Molecule.molregno",
							 foreign_keys="[CompoundStructure.molregno]",
							 uselist=False, backref='Molecule')
	
	Formulations = relationship("Formulation",
								primaryjoin="Formulation.molregno==Molecule.molregno",
								foreign_keys="[Formulation.molregno]",
								uselist=True, backref='Molecule')
	
	Synonyms = relationship("MoleculeSynonym",
							collection_class=attribute_mapped_collection("syn_type"),
							primaryjoin="MoleculeSynonym.molregno==Molecule.molregno",
							foreign_keys="[MoleculeSynonym.molregno]",
							uselist=True, backref='Molecule')
	
	Hierarchy = relationship("MoleculeHierarchy",
							 primaryjoin="MoleculeHierarchy.molregno==Molecule.molregno",
							 foreign_keys="[MoleculeHierarchy.molregno]",
							 uselist=False, backref='Molecule')
	
	Assays = relationship("Assay",
						  secondary=Base.metadata.tables['chembl.compound_records'],
						  primaryjoin="Molecule.molregno==CompoundRecord.molregno",
						  secondaryjoin="CompoundRecord.doc_id==Assay.doc_id",
						  foreign_keys="[CompoundRecord.molregno,CompoundRecord.doc_id]",
						  uselist=True, innerjoin=True, backref='Molecules')
	
	def __repr__(self):
		'''
		'''
		return '<Molecule({self.molregno})>'.format(self=self)
		
	@property
	def DosedComponent(self):
		'''
		'''
		return MoleculeAdaptor().fetch_dosed_component_by_molregno(self.molregno)
	
	@property
	def Targets(self):
		'''
		'''
		return TargetAdaptor().fetch_all_by_molregno(self.molregno)
	
	@property
	def Ligands(self):
		'''
		'''
		return credoadaptor.LigandAdaptor().fetch_all_by_chembl_id(self.chembl_id)
	
	def get_activities(self, *expressions):
		'''
		'''
		return ActivityAdaptor().fetch_all_by_molregno(self.molregno,*expressions)
	
	def get_activity_cliffs(self, *expressions):
		'''
		'''
		return ActivityCliffAdaptor().fetch_all_by_molregno(self.molregno, *expressions)

class MoleculeHierarchy(Base):
	'''
	'''
	__tablename__ = 'chembl.molecule_hierarchy'
	
	@property
	def Active(self):
		'''
		'''
		return MoleculeAdaptor().fetch_by_molregno(self.active_molregno)

class MoleculeSynonym(Base):
	'''
	'''
	__tablename__ = 'chembl.molecule_synonyms'
	
	def __repr__(self):
		'''
		'''
		return '<MoleculeSynonym({self.molregno}, {self.synonyms}, {self.syn_type})>'.format(self=self)

class OrganismClass(Base):
    __tablename__ = 'chembl.organism_class'	   

class Product(Base):
	'''
	'''
	__tablename__ = 'chembl.products'
	
	def __repr__(self):
		'''
		'''
		return '<Product({self.product_id}, {self.trade_name})>'.format(self=self)

class ProteinTherapeutic(Base):
	'''
	'''
	__tablename__ = 'chembl.protein_therapeutics'
	
	Molecule = relationship("Molecule",
							primaryjoin="Molecule.molregno==ProteinTherapeutic.molregno",
							foreign_keys="[Molecule.molregno]",
							uselist=False, innerjoin=True),	

	def __repr__(self):
		'''
		'''
		return '<ProteinTherapeutic({self.molregno})>'.format(self=self)
	
	@property
	def Chains(self):
		'''
		'''
		md5 = func.md5(self.protein_sequence.upper())
		return credoadaptor.ChainAdaptor().fetch_all_by_seq_md5(md5)

class RelationshipType(Base):
	__tablename__ = 'chembl.relationship_type'	

class ResearchCode(Base):
	__tablename__ = 'chembl.research_codes'	

class Source(Base):
	'''
	'''
	__tablename__ = 'chembl.source'
	
	def __repr__(self):
		'''
		'''
		return '<Source({self.src_id})>'.format(self=self)

class Target(Base):
	'''
	'''
	__tablename__ = 'chembl.target_dictionary'
	
	Classes = relationship("TargetClass",
						   primaryjoin="TargetClass.tid==Target.tid",
						   foreign_keys="[TargetClass.tid]",
						   uselist=True, innerjoin=True, backref='Target')
	
	Type = relationship("TargetType",
						primaryjoin="TargetType.target_type==Target.target_type",
						foreign_keys="[TargetType.target_type]",
						uselist=False, innerjoin=True),	

	def __repr__(self):
		'''
		'''
		return '<Target({self.tid})>'.format(self=self)
	
	@property
	def Chains(self):
		'''
		'''
		return credoadaptor.ChainAdaptor().fetch_all_by_uniprot(self.protein_accession)

class TargetClass(Base):
	__tablename__ = 'chembl.target_class'	

class TargetType(Base):
	__tablename__ = 'chembl.target_type'	

class Version(Base):
	__tablename__ = 'chembl.version'	

### LOCAL TABLES ###

class ActivityCliff(object):
    '''
    '''
    def __repr__(self):
        '''
        '''
        return '<ActivityCliff({self.assay_id}, {self.activity_bgn_id}, {self.activity_end_id})>'.format(self=self)

class CompoundSmiles(Base):
	'''
	Table used to store the isomeric SMILES strings produced with OEChem.
	'''
	__tablename__ = 'chembl.compound_smiles'
	
	@hybrid_method
	def like(self, smiles):
		'''
		Returns an SQL function expression that uses the PostgreSQL trigram index
		to compare the SMILES strings.
		'''
		warn("Trigram functions at the instance level are not implemented.", UserWarning)
	
	@like.expression
	def like(self, smiles):
		'''
		Returns an SQL function expression that uses the PostgreSQL trigram index
		to compare the SMILES strings.
		'''
		return self.ism.op('%%')(smiles)

class CompoundRDMol(Base):
	'''
	'''
	__tablename__ = 'chembl.compound_rdmols'
	
	@reconstructor
	def init_on_load(self):
		'''
		Turns the rdmol column that is returned as a SMILES string back into an
		RDMol Base.
		'''
		self.rdmol = Mol(str(self.rdmol))
	
	@hybrid_method
	def contains(self, smiles):
		'''
		Returns true if the given SMILES string is a substructure of this RDMol.
		Uses a client-side RDKit installation.
	
		Returns
		-------
		contains : boolean
			True if the rdmol molecule attribute contains the specified substructure
			in SMILES format.
		'''
		return self.rdmol.HasSubstructMatch(MolFromSmiles(str(smiles)))
	
	@contains.expression
	def contains(self, smiles):
		'''
		Returns a RDKit cartridge substructure query in form of an SQLAlchemy binary
		expression.
	
		Returns
		-------
		expression : sqlalchemy.sql.expression._BinaryExpression
			SQL expression that can be used to query ChemCompRDMol for substructure
			hits.
		'''
		return self.rdmol.op('OPERATOR(rdkit.@>)')(smiles)
	
	@hybrid_method
	@requires.rdkit
	def contained_in(self, smiles):
		'''
		Returns true if the given SMILES string is a superstructure of this RDMol.
		Uses a client-side RDKit installation.
	
		Returns
		-------
		contains : boolean
			True if the rdmol molecule attribute is contained in the specified
			substructure in SMILES format.
		'''
		return MolFromSmiles(smiles).HasSubstructMatch(self.rdmol)
	
	@contained_in.expression
	def contained_in(self, smiles):
		'''
		Returns a RDKit cartridge superstructure query in form of an SQLAlchemy binary
		expression.
	
		Returns
		-------
		expression : sqlalchemy.sql.expression._BinaryExpression
			SQL expression that can be used to query ChemCompRDMol for superstructure
			hits.
		'''
		return self.rdmol.op('OPERATOR(rdkit.<@)')(smiles)
	
	@hybrid_method
	@requires.rdkit
	def matches(self, smarts):
		'''
		Returns true if the RDMol matches the given SMARTS query. Uses a client-side
		RDKit installation.
	
		Returns
		-------
		matches : boolean
			True if the rdmol molecule attribute matches the given SMARTS query.
		'''
		return self.rdmol.HasSubstructMatch(MolFromSmarts(smarts))
	
	@matches.expression
	def matches(self, smarts):
		'''
		Returns a SMARTS match query in form of an SQLAlchemy binary expression.
	
		Returns
		-------
		expression : sqlalchemy.sql.expression._BinaryExpression
			SQL expression that can be used to query ChemCompRDMol for SMARTS matches.
		'''
		return self.rdmol.op('OPERATOR(rdkit.@>)')(func.rdkit.qmol_in(smarts))

class CompoundRDFP(Base):
    '''
    '''
    __tablename__ = 'chembl.compound_rdfps'	



# CUSTOM SELECT FOR ACTIVITY CLIFFS THAT WILL BE MAPPED AGAINST A CLASS
A1, A2 = metadata.tables['chembl.activities'].alias(), metadata.tables['chembl.activities'].alias()
FP1, FP2 = metadata.tables['chembl.compound_rdfps'].alias(), metadata.tables['chembl.compound_rdfps'].alias()

join = A1.join(A2, A2.c.assay_id==A1.c.assay_id).join(FP1, FP1.c.molregno==A1.c.molregno).join(FP2, FP2.c.molregno==A2.c.molregno)

delta_tanimoto = 1 - func.rdkit.tanimoto_sml(FP1.c.circular_fp, FP2.c.circular_fp)
delta_activity = func.abs(func.log(A1.c.standard_value) - func.log(A2.c.standard_value)).label('delta_activity')
sali = (delta_activity / delta_tanimoto).label('sali')

whereclause = and_(A1.c.activity_id != A2.c.activity_id,
                   A1.c.molregno < A2.c.molregno,
                   A1.c.standard_type == A2.c.standard_type,
                   A1.c.standard_value > 0, A2.c.standard_value > 0,
                   A1.c.standard_flag > 0, A2.c.standard_flag > 0,
                   A1.c.standard_units == 'nM', A2.c.standard_units == 'nM',
                   A1.c.relation == '=', A1.c.relation == '=',
                   sali >= 1.5)

activity_cliffs = select([A1.c.assay_id,
                          A1.c.activity_id.label('activity_bgn_id'), A2.c.activity_id.label('activity_end_id'),
                          A1.c.molregno.label('molregno_bgn'), A2.c.molregno.label('molregno_end'),
                          delta_tanimoto.label('delta_tanimoto'), delta_activity, sali],
                         from_obj=[join], whereclause=whereclause).order_by("sali DESC").alias(name='activity_cliffs')

mapper(ActivityCliff, activity_cliffs, properties={
    'Assay': relationship(Assay,
                          primaryjoin=Assay.assay_id==activity_cliffs.c.assay_id,
                          foreign_keys=[Assay.assay_id], uselist=False, innerjoin=True,
                          backref=backref('ActivityCliffs',uselist=True, innerjoin=True)),
    'ActivityBgn': relationship(Activity,
                                primaryjoin=Activity.activity_id==activity_cliffs.c.activity_bgn_id,
                                foreign_keys=[Activity.activity_id], uselist=False, innerjoin=True),
    'ActivityEnd': relationship(Activity,
                                primaryjoin=Activity.activity_id==activity_cliffs.c.activity_end_id,
                                foreign_keys=[Activity.activity_id], uselist=False, innerjoin=True),
    'MoleculeBgn': relationship(Molecule,
                                primaryjoin=Molecule.molregno==activity_cliffs.c.molregno_bgn,
                                foreign_keys=[Molecule.molregno], uselist=False, innerjoin=True),
    'MoleculeEnd': relationship(Molecule,
                                primaryjoin=Molecule.molregno==activity_cliffs.c.molregno_end,
                                foreign_keys=[Molecule.molregno], uselist=False, innerjoin=True,)
    })

### ADAPTORS ###

class ActivityAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Activity)
    
    def fetch_by_activity_id(self, activity_id):
        '''
        '''
        return self.query.get(activity_id)
    
    def fetch_all_by_molregno(self, molregno, *expressions):
        '''
        '''
        return self.query.filter(and_(Activity.molregno==molregno, *expressions)).all()

class ActivityCliffAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(ActivityCliff)
        
    def fetch_all_by_molregno(self, molregno, *expressions):
        '''
        '''
        bgn = self.query.filter(and_(ActivityCliff.molregno_bgn==molregno, *expressions))
        end = self.query.filter(and_(ActivityCliff.molregno_end==molregno, *expressions))

        return bgn.union(end).order_by(ActivityCliff.sali.desc()).limit(1000).all()

class AssayAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Assay)
    
    def fetch_by_assay_id(self, assay_id):
        '''
        '''
        return self.query.get(assay_id)
    
    def fetch_by_chembl_id(self, chembl_id):
        '''
        '''
        return self.query.filter(Assay.chembl_id==chembl_id).first()
    
    def fetch_all_by_pubmed_id(self, pubmed_id):
        '''
        '''
        return self.query.join('Doc').filter(Doc.pubmed_id==pubmed_id).all()

class DocAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Doc)
    
    def fetch_by_doc_id(self, doc_id):
        '''
        '''
        return self.query.get(doc_id)
    
    def fetch_by_chembl_id(self, chembl_id):
        '''
        '''
        return self.query.filter(Doc.chembl_id==chembl_id).first()

    def fetch_all_by_pubmed_id(self, pubmed_id):
        '''
        '''
        return self.query.filter(Doc.pubmed_id==pubmed_id).all()

class MoleculeAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Molecule)
    
    def fetch_by_molregno(self, molregno):
        '''
        '''
        return self.query.get(molregno)
    
    def fetch_by_chembl_id(self, chembl_id):
        '''
        '''
        return self.query.filter(Molecule.chembl_id==chembl_id).first()
    
    def fetch_all_by_synonym(self, synonym):
        '''
        '''
        return self.query.join('Synonyms').filter(func.lower(MoleculeSynonym.synonyms)==synonym.lower()).all()

    def fetch_active_by_molregno(self, molregno):
        '''
        '''
        query = self.query.join(MoleculeHierarchy, MoleculeHierarchy.molregno==Molecule.molregno)
        query = query.filter(MoleculeHierarchy.active_molregno==molregno)
        
        return query.first()
    
    def fetch_parent_by_molregno(self, molregno):
        '''
        '''
        query = self.query.join(MoleculeHierarchy, MoleculeHierarchy.molregno==Molecule.molregno)
        query = query.filter(MoleculeHierarchy.parent_molregno==molregno)
        
        return query.first()
    
    def fetch_dosed_component_by_molregno(self, molregno):
        '''
        '''
        query = self.query.join('Formulations')
        
        molecule = session.query(MoleculeHierarchy.molregno.label('molregno')).filter(MoleculeHierarchy.molregno==molregno)
        parent = session.query(MoleculeHierarchy.molregno.label('molregno')).filter(MoleculeHierarchy.parent_molregno==molregno)
        active = session.query(MoleculeHierarchy.molregno.label('molregno')).filter(MoleculeHierarchy.active_molregno==molregno)
        
        subquery = molecule.union(parent,active).subquery()
        
        query = query.join(subquery, subquery.c.molregno==Molecule.molregno)
        
        return query.first()
    
    def fetch_by_inchi_key(self, inchi_key):
        '''
        '''
        query = self.query.join('Structure')
        query = query.filter(CompoundStructure.standard_inchi_key==inchi_key)
        
        return query.first()
    
    @requires.rdkit_catridge
    def fetch_all_by_substruct(self, smi, *expressions, **kwargs):
        '''
        Returns all molecules in ChEMBL that have the given SMILES
        substructure.

        Parameters
        ----------
        smi : str
            SMILES string of the substructure to be used for substructure
            searching.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Molecule, CompoundRDMol

        Returns
        -------
        molecules : list
            List of molecules that have the given substructure.

        Examples
        --------

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        limit = kwargs.get('limit', 100)
        
        query = self.query.join(CompoundRDMol, CompoundRDMol.molregno==Molecule.molregno)
        query = query.filter(and_(CompoundRDMol.contains(smi), *expressions))
        
        return query.limit(limit).all()
    
    @requires.rdkit_catridge
    def fetch_all_by_superstruct(self, smiles, *expressions, **kwargs):
        '''
        Returns all molecules in ChEMBL that have the given SMILES superstructure.

        Parameters
        ----------
        smiles : string
            SMILES string of the superstructure to be used for superstructure
            searching.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Molecule, CompoundRDMol

        Returns
        -------
        molecules : list
            List of molecules that have the given superstructure.

        Examples
        --------

        Requires
        --------
        .. important:: `RDKit <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        limit = kwargs.get('limit', 100)
        
        query = self.query.join(CompoundRDMol, CompoundRDMol.molregno==Molecule.molregno)
        query = query.filter(and_(CompoundRDMol.contained_in(smiles), *expressions))
        
        return query.limit(limit).all()
    
    @requires.rdkit_catridge
    def fetch_all_by_sim(self, smi, threshold=0.5, fp='circular', *expressions, **kwargs):
        '''
        Returns all molecules that match the given SMILES string with at
        least the given similarity threshold using chemical fingerprints.

        Parameters
        ----------
        smi : str
            The query rdmol in SMILES format.
        threshold : float, default=0.5
            The similarity threshold that will be used for searching.
        fp : {'circular','atompair','torsion'}
            RDKit fingerprint type to be used for similarity searching.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Molecule, CompoundRDFP

        Returns
        -------
        hits : list
            List of tuples in the form (Molecule, similarity)

        Examples
        --------

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        limit = kwargs.get('limit', 25)
        
        if fp == 'circular':
            query = func.rdkit.morganbv_fp(smi,2).label('queryfp')
            target = CompoundRDFP.circular_fp

        elif fp == 'torsion':
            query = func.rdkit.torsionbv_fp(smi).label('queryfp')
            target = CompoundRDFP.torsion_fp

        elif fp == 'atompair':
            query = func.rdkit.atompairbv_fp(smi).label('queryfp')
            target = CompoundRDFP.atompair_fp

        else:
            msg = "The fingerprint type [{0}] does not exist.".format(fp)
            raise RuntimeError(msg)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SET rdkit.tanimoto_threshold=:threshold").execution_options(autocommit=True).params(threshold=threshold))

        tanimoto = func.rdkit.tanimoto_sml(query, target).label('tanimoto')
        index = func.rdkit.tanimoto_sml_op(query,target)

        query = session.query(Molecule, tanimoto)
        query = query.join(CompoundRDFP, CompoundRDFP.molregno==Molecule.molregno)
        query = query.filter(and_(index, *expressions)).order_by('tanimoto DESC')

        return query.limit(limit).all()
    
    def fetch_all_by_trgm_sim(self, smiles, *expressions, **kwargs):
        '''
        Returns all molecules that are similar to the given SMILES string
        using trigam similarity (similar to LINGO).

        Parameters
        ----------
        threshold : float, default=0.6
            Similarity threshold that will be used for searching.
        limit : int, default=25
            Maximum number of hits that will be returned.

        Returns
        -------
        resultset : list
            List of tuples (Molecule, similarity) containing the Molecules
            and the calculated trigram similarity.

        Queried Entities
        ----------------
        Molecule

        Examples
        --------

        Requires
        --------
        .. important:: `pg_trgm  <http://www.postgresql.org/docs/current/static/pgtrgm.html>`_ PostgreSQL extension.
        '''
        threshold = kwargs.get('threshold', 0.6)
        limit = kwargs.get('limit', 25)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SELECT set_limit(:threshold)").execution_options(autocommit=True).params(threshold=threshold))

        similarity = func.similarity(CompoundSmiles.ism,smiles).label('similarity')

        query = session.query(Molecule, similarity)
        query = query.join(CompoundSmiles, CompoundSmiles.molregno==Molecule.molregno)
        query = query.filter(and_(CompoundSmiles.like(smiles), *expressions))
        
        # KNN-GIST
        query = query.order_by(CompoundSmiles.ism.op('<->')(smiles)).limit(limit)

        return query.all()

class ProductAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Product)
    
    def fetch_by_product_id(self, product_id):
        '''
        '''
        return self.query.get(product_id)
    
    def fetch_all_by_trade_name(self, trade_name):
        '''
        '''
        return self.query.filter(Product.trade_name==trade_name.upper()).all()

class ProteinTherapeuticAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(ProteinTherapeutic)
    
    def fetch_by_molregno(self, molregno):
        '''
        '''
        return self.query.get(molregno)

    def fetch_all_by_protein_sequence(self, sequence):
        '''
        '''
        return self.query.filter(ProteinTherapeutic.protein_sequence==sequence).all()

class TargetAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Target)
    
    def fetch_by_target_id(self, target_id):
        '''
        '''
        return self.query.get(target_id)
        
    def fetch_by_chembl_id(self, chembl_id):
        '''
        '''
        return self.query.filter(Target.chembl_id==chembl_id).first()
    
    def fetch_by_uniprot(self, uniprot):
        '''
        '''
        return self.query.filter(Target.protein_accession==uniprot).first()
    
    def fetch_all_by_molregno(self, molregno, *expressions):
        '''
        '''
        query = self.query.join('Assay2Targets','Assay','Activities')
        query = query.filter(and_(Activity.molregno==molregno, *expressions))
        
        return query.all()