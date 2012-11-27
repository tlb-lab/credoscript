"""
This extension contains the entities for the UniProt SIFt clustering of all
ligands in CREDO.
"""
from xml.etree.ElementTree import Element, SubElement

from sqlalchemy.orm import aliased, backref, relationship
from sqlalchemy.sql.expression import and_, or_

from credoscript import Base
from credoscript.mixins.base import paginate

class LigandUniProtSIFtNode(Base):
    """
    A LigandUniProtSIFtNode is a node resulting from hierarchical clustering of the
    Structural Interaction Fingerprints (SIFts) of all ligands bound to proteins
    having the same UniProt accession. SIFts are summed up per UniProt residue
    and the manhattan distance used to calculate the distance between SIFts.

    Terminal nodes are always ligands and returned as such.

    Attributes
    ----------
    id : int
        Primary key of this object.
    uniprot : char
        UniProt accession of this tree.
    node : int
        Node identifier in this tree.
    links : int
        Node identifier of the left child of this node.
    rechts : int
        Node identifier of the right child of this node.
    size : int
        Number of leaves (terminal nodes, ligands) attached to this node.
    distance : float
        The node's distance.

    Mapped Attributes
    ----------
    Root : LigandUniProtSIFtNode
        Root node of the clustering tree for this uniprot accession.
    Parent : LigandUniProtSIFtNode
        Parent of this node in the hierarchical clustering tree.
    Children : list
        List of child nodes (children).
    Left : LigandUniProtSIFtNode
        Left child node in the hierarchical clustering tree.
    Right : LigandUniProtSIFtNode
        Right child node in the hierarchical clustering tree.
    Leaves : list
        List of all terminal nodes (leaves), i.e. ligands, below this node.
    """
    __tablename__ = 'credo.ligand_uniprot_sift_nodes'

    # the parent node
    Parent = relationship("LigandUniProtSIFtNode",
                          primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode.uniprot,\
                                       or_(LigandUniProtSIFtNode.links==LigandUniProtSIFtNode.node, \
                                           LigandUniProtSIFtNode.rechts==LigandUniProtSIFtNode.node))",
                          foreign_keys="[LigandUniProtSIFtNode.uniprot, LigandUniProtSIFtNode.links, LigandUniProtSIFtNode.links]",
                          uselist=False, innerjoin=True)

    LeftNode = relationship("LigandUniProtSIFtNode",
                            primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode.uniprot, \
                                              LigandUniProtSIFtNode.node==LigandUniProtSIFtNode.links)",
                            foreign_keys="[LigandUniProtSIFtNode.uniprot,LigandUniProtSIFtNode.node]",
                            uselist=False, innerjoin=True)

    RightNode = relationship("LigandUniProtSIFtNode",
                             primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode.uniprot, \
                                               LigandUniProtSIFtNode.node==LigandUniProtSIFtNode.rechts)",
                             foreign_keys="[LigandUniProtSIFtNode.uniprot,LigandUniProtSIFtNode.node]",
                             uselist=False, innerjoin=True)

    Property = relationship("LigandUniProtSIFtNodeProperty",
                             primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNodeProperty.uniprot, \
                                               LigandUniProtSIFtNode.node==LigandUniProtSIFtNodeProperty.node)",
                             foreign_keys="[LigandUniProtSIFtNodeProperty.uniprot,LigandUniProtSIFtNodeProperty.node]",
                             uselist=False, lazy='joined')

    _Children = relationship("LigandUniProtSIFtNode",
                            primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode.uniprot, \
                                         or_(LigandUniProtSIFtNode.node==LigandUniProtSIFtNode.links, \
                                             LigandUniProtSIFtNode.node==LigandUniProtSIFtNode.rechts))",
                            foreign_keys="[LigandUniProtSIFtNode.uniprot,LigandUniProtSIFtNode.node]",
                            uselist=True, innerjoin=True)

    # only used internally to fetch nodes via ligand_id
    _Node2Ligand = relationship("LigandUniProtSIFtNode2Ligand",
                                primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode2Ligand.uniprot, \
                                                  or_(LigandUniProtSIFtNode.links==LigandUniProtSIFtNode2Ligand.node, \
                                                      LigandUniProtSIFtNode.rechts==LigandUniProtSIFtNode2Ligand.node))",
                                foreign_keys="[LigandUniProtSIFtNode2Ligand.uniprot, LigandUniProtSIFtNode2Ligand.node]",
                                uselist=False, innerjoin=True)

    # returns the ligands of the node if it has leaves
    Ligands = relationship("Ligand",
                           secondary=Base.metadata.tables['credo.ligand_uniprot_sift_node_to_ligand'],
                           primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode2Ligand.uniprot, \
                                        or_(LigandUniProtSIFtNode.links==LigandUniProtSIFtNode2Ligand.node, \
                                            LigandUniProtSIFtNode.rechts==LigandUniProtSIFtNode2Ligand.node))",
                           secondaryjoin="LigandUniProtSIFtNode2Ligand.ligand_id==Ligand.ligand_id",
                           foreign_keys="[LigandUniProtSIFtNode2Ligand.uniprot, LigandUniProtSIFtNode2Ligand.node, Ligand.ligand_id]",
                           uselist=True, lazy='dynamic',
                           backref=backref('LigandUniProtSIFtNode', uselist=False, innerjoin=True))

    LeftLigand = relationship("Ligand",
                              secondary=Base.metadata.tables['credo.ligand_uniprot_sift_node_to_ligand'],
                              primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode2Ligand.uniprot, \
                                                LigandUniProtSIFtNode.links==LigandUniProtSIFtNode2Ligand.node)",
                              secondaryjoin="LigandUniProtSIFtNode2Ligand.ligand_id==Ligand.ligand_id",
                              foreign_keys="[LigandUniProtSIFtNode2Ligand.uniprot, LigandUniProtSIFtNode2Ligand.node, Ligand.ligand_id]",
                              uselist=False)

    RightLigand = relationship("Ligand",
                               secondary=Base.metadata.tables['credo.ligand_uniprot_sift_node_to_ligand'],
                               primaryjoin="and_(LigandUniProtSIFtNode.uniprot==LigandUniProtSIFtNode2Ligand.uniprot, \
                                                 LigandUniProtSIFtNode.rechts==LigandUniProtSIFtNode2Ligand.node)",
                               secondaryjoin="LigandUniProtSIFtNode2Ligand.ligand_id==Ligand.ligand_id",
                               foreign_keys="[LigandUniProtSIFtNode2Ligand.uniprot, LigandUniProtSIFtNode2Ligand.node, Ligand.ligand_id]",
                               uselist=False)

    def __repr__(self):
        return "<LigandUniProtSIFtNode(%r, %r)>" % (self.uniprot, self.node)

    @property
    def is_node(self):
        """
        """
        return self.node < 0

    @property
    def is_leaf(self):
        """
        """
        return not self.is_node

    @property
    def Root(self):
        """
        """
        return self.query.filter_by(uniprot=self.uniprot, is_root=True).first()

    @property
    def Left(self):
        """
        """
        # left node is a cluster
        if self.links < 0: return self.LeftNode
        else: return self.LeftLigand

    @property
    def Right(self):
        """
        """
        if self.rechts < 0: return self.RightNode
        else: return self.RightLigand

    @property
    def Children(self):
        """
        Returns the children of this node which can be either nodes or leaves
        (ligands).
        """
        # both children are nodes
        if self.links < 0 and self.rechts < 0:
            return self._Children

        # ligand/node
        elif self.links >= 0 and self.rechts < 0:
            return (self.LeftLigand, self.RightNode)

        # node/ligand
        elif self.links < 0 and self.rechts >= 0:
            return (self.LeftNode, self.RightLigand)

        # both children are ligands
        else: return self.Ligands

    @property
    def Leaves(self):
        """
        Returns all the leaves (ligands) of this node.
        """
        return LigandUniProtSIFtNodeAdaptor().fetch_all_leaves(self.ligand_uniprot_sift_node_id)

    def _clade(self, distance=0):
        """
        Recursive method that will traverse the UniProt SIFt cluster and return
        an XML clade element containing the annotated tree.

        :param distance: The distance argument is used to provide the children
                         of this node with its distance.
        """
        def ligclade(ligand, distance):
            """
            Returns an annotated clade element for a ligand.
            """
            element = Element('clade')

            # name for the node that will be displayed in the tree
            name = SubElement(element, 'name')
            name.text = ligand.path[:17]

            # branch length: obtained from the parent
            branch_length = SubElement(element, 'branch_length')
            branch_length.text = "{:.2f}".format(distance)

            # additional annotation: the uri element is used to make the node
            # clickable, it will link to the credimus ligand page
            annotation = SubElement(element, 'annotation')
            uri = SubElement(annotation, 'uri')
            uri.text = "/ligands/{}".format(ligand.ligand_id)

            # chart options for this ligand node
            chart = SubElement(element, 'chart')
            interaction = SubElement(chart, 'interaction')

            # interaction types as internal arc chart
            if ligand.is_drug_target_int: interaction.text = 'drugtarget'
            elif ligand.is_enzyme_cmpd: interaction.text = 'enzymecmpd'

            # background color to highlight the compound type
            chemcomps = ligand.ChemComps.all()

            if len(chemcomps) == 1:
                chemcomp = chemcomps.pop()

                if chemcomp.is_approved_drug: name.attrib['bgStyle'] = 'appdrug'
                elif chemcomp.is_nucleotide: name.attrib['bgStyle'] = 'nucleotide'
                elif chemcomp.is_drug: name.attrib['bgStyle'] = 'drug'
                elif chemcomp.is_lead: name.attrib['bgStyle'] = 'lead'
                elif chemcomp.is_drug_like: name.attrib['bgStyle'] = 'druglike'
                elif chemcomp.is_solvent: name.attrib['bgStyle'] = 'solvent'

            else:
                name.attrib['bgStyle'] = 'heteropeptide'

            # binding site property
            bindingsite = SubElement(chart, 'bindingsite')

            if ligand.BindingSite.has_mut_res: bindingsite.text = 'mutated'
            elif ligand.BindingSite.has_mod_res: bindingsite.text = 'modified'
            elif ligand.BindingSite.has_non_std_res: bindingsite.text = 'nonstd'

            # normalized maximum ligand p(Kd,Ki,IC50) as bar chart
            # we normalize it between 0 and 100 to make the differences more visible
            # in the bar chart. Logarithmic values are hard to distinguish
            activity = SubElement(chart, 'activity')
            effs = ligand.Effs

            # we use 1 nM (9) as ceiling, 1mM (3) as floor
            norm_pkd = max(((eff.p - 3) / (9.0-3)) * 100 for eff in effs) if effs else 0
            activity.text = str(norm_pkd)

            return element

        clade = Element('clade')

        # every node has a branch length (root is 0)
        branch_length = SubElement(clade, 'branch_length')
        branch_length.text = "{:.2f}".format(distance)

        if self.links < 0: node = self.LeftNode._clade(self.distance)
        else: node = ligclade(self.LeftLigand, self.distance)

        clade.append(node)

        if self.rechts < 0: node = self.RightNode._clade(self.distance)
        else: node = ligclade(self.RightLigand, self.distance)

        clade.append(node)

        return clade

    def phyloxml(self, **kwargs):
        """
        Returns the root element of UniProt SIFt cluster tree in PhyloXML format.
        """
        root = Element('phyloxml')
        phylogeny = SubElement(root, 'phylogeny')
        phylogeny.set('rooted', 'true')

        # rendering options
        render = SubElement(phylogeny, 'render')
        parameters = SubElement(render, 'parameters')
        circular = SubElement(parameters, 'circular')
        buffer_radius = SubElement(circular, 'bufferRadius')
        buffer_radius.text = kwargs.get(str('buffer_radius'),'0.4')

        # charting options for this tree
        charts = SubElement(render, 'charts')

        # create internal arcs in the tree to display the compound class: drug,
        # endogenous, etc.
        interaction = SubElement(charts, 'interaction')
        interaction.attrib = {'type': 'binary', 'thickness': '10',
                              'isInternal': 'true', 'bufferInner': '0'}

        # binding site property binary arcs
        bindingsite = SubElement(charts, 'bindingsite')
        bindingsite.attrib = {'type': 'binary', 'thickness': '7.5'}

        # ligand efficiency bar charts
        activity = SubElement(charts, 'activity')
        activity.attrib = {'type': 'bar', 'fill':'#000', 'width':'0.4'}

        # styling of elements: charts, arcs, backgrounds
        styles = SubElement(render, 'styles')
        drugtarget = SubElement(styles, 'drugtarget', {'fill': '#75BBE4', 'stroke':'#DDD'})
        enzymecmpd = SubElement(styles, 'enzymecmpd', {'fill': '#DEF1CC', 'stroke':'#DDD'})
        bar_chart = SubElement(styles, 'barChart', {'fill':'#999', 'stroke-width':'0'})

        # chemical component types
        appdrug = SubElement(styles, 'appdrug', {'fill': '#3296CB', 'stroke':'#3296CB'})
        drug = SubElement(styles, 'drug', {'fill': '#75BBE4', 'stroke':'#75BBE4'})
        lead = SubElement(styles, 'lead', {'fill': '#A9D6F0', 'stroke':'#A9D6F0'})
        druglike = SubElement(styles, 'druglike', {'fill': '#CDE9F4', 'stroke':'#CDE9F4'})
        solvent = SubElement(styles, 'solvent', {'fill': '#FFFACD', 'stroke':'#FFFACD'})
        heteropeptide = SubElement(styles, 'heteropeptide', {'fill': '#FBD5A5', 'stroke':'#FBD5A5'})
        nucleotide = SubElement(styles, 'nucleotide', {'fill': '#DEF1CC', 'stroke':'#DEF1CC'})

        # binding site properties
        mutated = SubElement(styles, 'mutated', {'fill': '#E75559', 'stroke':'#DDD'})
        modified = SubElement(styles, 'modified', {'fill': '#F98892', 'stroke':'#DDD'})
        nonstd = SubElement(styles, 'nonstd', {'fill': '#FDCDD7', 'stroke':'#DDD'})

        clade = SubElement(phylogeny, 'clade')
        clade.append(self._clade())

        return root

class LigandUniProtSIFtNode2Ligand(Base):
    __tablename__ = 'credo.ligand_uniprot_sift_node_to_ligand'

    Ligand = relationship("Ligand",
                          primaryjoin="Ligand.ligand_id==LigandUniProtSIFtNode2Ligand.ligand_id",
                          foreign_keys="[Ligand.ligand_id]",
                          uselist=False, innerjoin=True)

class LigandUniProtSIFtNodeProperty(Base):
    __tablename__ = 'credo.ligand_uniprot_sift_node_properties'

class LigandUniProtSIFtNodeAdaptor(object):
    """
    """
    def __init__(self, paginate=False, dynamic=False, per_page=100, options=()):
        """
        """
        self.query = LigandUniProtSIFtNode.query
        self.paginate = paginate
        self.dynamic = dynamic
        self.per_page = per_page

        # add options to this query: can be joinedload, undefer etc.
        for option in options:
            self.query = self.query.options(option)

    def fetch_by_ligand_uniprot_sift_node_id(self, ligand_uniprot_sift_node_id):
        """
        """
        return self.query.get(ligand_uniprot_sift_node_id)

    def fetch_root_by_uniprot(self, uniprot):
        """
        """
        return self.query.filter_by(uniprot=uniprot, is_root=True).first()

    def fetch_by_uniprot_node(self, uniprot, node):
        """
        """
        return self.query.filter_by(uniprot=uniprot, node=node).first()

    def fetch_by_ligand_id(self, ligand_id):
        """
        """
        query = self.query.join('_Node2Ligand')
        return query.filter(LigandUniProtSIFtNode2Ligand.ligand_id==ligand_id).first()

    @paginate
    def fetch_all_parents(self, ligand_uniprot_sift_node_id, *expr, **kwargs):
        """
        Returns all parent nodes of this node.
        """
        descendants = self.query.filter_by(ligand_uniprot_sift_node_id=ligand_uniprot_sift_node_id)
        descendants = descendants.cte(name="descendants", recursive=True)
        desc_alias = aliased(descendants, name="d")

        end = self.query.join(desc_alias,
                              and_(desc_alias.c.uniprot==LigandUniProtSIFtNode.uniprot,
                                   or_(desc_alias.c.node==LigandUniProtSIFtNode.links,
                                       desc_alias.c.node==LigandUniProtSIFtNode.rechts)))

        descendants = descendants.union_all(end)

        query = self.query.join(descendants,
                                descendants.c.ligand_uniprot_sift_node_id==LigandUniProtSIFtNode.ligand_uniprot_sift_node_id)

        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_children(self, ligand_uniprot_sift_node_id, *expr, **kwargs):
        """
        Returns all descending nodes of this node.
        """
        descendants = self.query.filter_by(ligand_uniprot_sift_node_id=ligand_uniprot_sift_node_id)
        descendants = descendants.cte(name="descendants", recursive=True)
        desc_alias = aliased(descendants, name="d")

        end = self.query.join(desc_alias,
                              and_(desc_alias.c.uniprot==LigandUniProtSIFtNode.uniprot,
                                   or_(desc_alias.c.links==LigandUniProtSIFtNode.node,
                                       desc_alias.c.rechts==LigandUniProtSIFtNode.node)))

        descendants = descendants.union_all(end)

        query = self.query.join(descendants,
                                descendants.c.ligand_uniprot_sift_node_id==LigandUniProtSIFtNode.ligand_uniprot_sift_node_id)

        query = query.filter(and_(*expr))

        return query

    @paginate
    def fetch_all_leaves(self, ligand_uniprot_sift_node_id, *expr, **kwargs):
        """
        """
        descendants = self.query.filter_by(ligand_uniprot_sift_node_id=ligand_uniprot_sift_node_id)
        descendants = descendants.cte(name="descendants", recursive=True)
        desc_alias = aliased(descendants, name="d")

        end = self.query.join(desc_alias,
                              and_(desc_alias.c.uniprot==LigandUniProtSIFtNode.uniprot,
                                   or_(desc_alias.c.links==LigandUniProtSIFtNode.node,
                                       desc_alias.c.rechts==LigandUniProtSIFtNode.node)))

        descendants = descendants.union_all(end)

        query = Ligand.query.join(LigandUniProtSIFtNode2Ligand,
                                  LigandUniProtSIFtNode2Ligand.ligand_id==Ligand.ligand_id)
        query = query.join(descendants,
                           and_(descendants.c.uniprot==LigandUniProtSIFtNode2Ligand.uniprot,
                                or_(descendants.c.links==LigandUniProtSIFtNode2Ligand.node,
                                    descendants.c.rechts==LigandUniProtSIFtNode2Ligand.node)))

        query = query.filter(and_(*expr))

        return query

from credoscript.models.ligand import Ligand
