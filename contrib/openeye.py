    @requires.openeye
    def rocs2d(self, *args, **kwargs):
        '''
        Returns
        -------

        Requires
        --------
        '''
        min_hvy_atoms = kwargs.get('min_hvy_atoms',7)
        limit = kwargs.get('limit',20)

        # SET ROCS2D QUERY
        statement = text("""
                         SELECT  openeye.set_rocs2d_query(oeb)
                         FROM    pdbchem.chem_comp_properties
                         WHERE   het_id = :het_id
                         """).params(het_id=self.het_id)

        success = session.execute(statement).scalar()

        if not success: return None

        statement = text("""
                         SELECT  cp.*
                         FROM    pdbchem.chem_comp_properties cp
                         WHERE   num_hvy_atoms > :min_hvy_atoms
                         ORDER BY openeye.rocs2d(oeb) DESC NULLS LAST
                         LIMIT :limit
                         """)

        return session.query(ChemComp).from_statement(statement).params(min_hvy_atoms=min_hvy_atoms,
                                                                               limit=limit).all()