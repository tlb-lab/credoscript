import xmlrpclib

class PyMOLViewer(object):
    '''
    '''
    def __init__(self,host='localhost',port=9123):
        self.srv = xmlrpclib.Server('http://%s:%s' % (host,port))

        # self.set('fetch_host','pdbe')

        # FETCH_PATH SETS THE DEFAULT PATH THAT PYMOL USES TO LOAD FILES FROM BEFORE IT TRIES TO DOWNLOAD THEM FROM THE PDB.
        # self.set('fetch_path', PDB_DIR) # NOT WORKING YET, PYMOL ONLY LOADS LOWERCASE FILES

        # SET PYMOL VARIABLES FOR PRETTIER MOLECULES
        self.set('valence', 1)
        self.set('stick_rad', 0.15)
        self.set('line_width', 1)
        self.set('mesh_width', 0.3)

        # DECREASE FONT SIZE
        self.set('label_size', 10)

        # MAKE SPHERES LOOK PRETTIER (WATER, IONS...)
        self.set('sphere_scale', 0.15)

        # DASH PROPERTIES
        self.set('dash_round_ends', 0)
        self.set('dash_gap', 0.25)
        self.set('dash_length', 0.05)

        # COLORS
        self.set_color('maize', (251, 236, 93)) # IONIC VDW
        self.set_color('cream', (255, 253, 208)) # IONIC PROXIMAL

        self.set_color('electric_purple', (191, 0, 255)) # METAL COMPLEX VDW CLASH
        self.set_color('medium_purple', (147, 112, 219)) # METAL COMPLEX VDW

        self.set_color('amber', (255, 191, 0))
        self.set_color('peach', (255, 229, 180))

        self.set_color('electric_blue', (125, 249, 255)) #
        self.set_color('baby_blue', (224, 255, 255))

        self.set_color('emerald', (80, 200, 120))
        self.set_color('moss_green', (173, 200, 173))

        self.set_color('rose', (255, 0, 127))
        self.set_color('brilliant_rose', (246, 83, 166))
        self.set_color('thulian_pink', (222, 111, 161))

        self.set_color('neon_red', (255, 0, 102))

        # DNA
        self.set('cartoon_ladder_mode', 1)
        self.set('cartoon_ring_finder', 1)
        self.set('cartoon_ring_mode', 3)
        self.set('cartoon_nucleic_acid_mode', 4)
        self.set('cartoon_ring_transparency', 0.5)

        self.maxQuality()

    def maxQuality(self):
        '''
        Enables maximum quality by default.
        '''
        self.set('line_smooth',1)
        self.set('antialias',2)
        self.set('cartoon_fancy_helices',1)
        self.set('depth_cue',1)
        self.set('specular',1)
        self.set('surface_quality',1)
        self.set('stick_quality',15)
        self.set('sphere_quality',2)
        self.set('cartoon_sampling',14)
        self.set('ribbon_sampling',10)
        self.set('transparency_mode',2)
        self.set('stick_ball',1)
        self.set('stick_ball_ratio', 1.5)
        self.srv.do("rebuild")

    def qute(self, *args):
        '''
        '''
        self.srv.do('set_color oxygen, [1.0,0.4,0.4]')
        self.srv.do('set_color nitrogen, [0.5,0.5,1.0]')
        self.remove("solvent")

        self.color('grey', '(symbol c)')
        self.srv.do('bg white')
        self.set("light_count",10)
        self.set("spec_count",1)
        self.set("shininess",10)
        self.set("specular",0.25)
        self.set("ambient",0)
        self.set("direct",0)
        self.set("reflect",1.5)
        self.set("ray_shadow_decay_factor",0.1)
        self.set("ray_shadow_decay_range", 2)
        self.unset("depth_cue")

    def cartoonish(self):
        '''
        '''
        self.srv.do('bg white')
        self.show('cartoon','polymer')
        self.set('cartoon_side_chain_helper','1')
        self.set('stick_ball',0)
        self.set_bond('stick_radius','0.05','polymer')
        self.show('sticks','polymer')

    def align(self, source, target, object='alignment'):
        '''
        '''
        self.srv.do("super %s, %s, object=%s" % (source, target, object))

    def alter(self,sel,exp):
        '''
        alter changes one or more atomic properties over a selection using the
        python evaluator with a separate name space for each atom.
        '''
        self.srv.do('alter %s, %s' % (sel,exp))

    def clear(self):
        '''
        Removes every object from PyMOL
        '''
        self.srv.deleteAll()

    def count_atoms(self, sel):
        '''
        returns a count of atoms in a selection.
        '''
        return self.srv.countAtoms(sel)

    def create(self, name, sel):
        '''
        '''
        self.srv.do("create %s, (%s)" % (name, sel))

    def color(self,color,obj=None):
        '''
        color color-name
        color color-name, object-name
        color color-name, (selection)
        '''
        if obj: self.srv.do('color %s, %s' % (color,obj))
        else: self.srv.do('color %s' % color)

    def clip(self,mode,distance,selection=''):
        '''{}, distance [,selection [,state ]]
        '''
        if mode in ('near','far','move','slab','atoms'):
            self.srv.do('clip %s, %s, %s' % (mode,distance,selection))

    def cylinder(self,end1,end2,rad,color1,id='cylinder',color2=None,extend=1):
        '''
        '''
        self.srv.cylinder(end1,end2,rad,color1,id,color2,extend)

    def delete(self, sel):
        '''
        '''
        self.srv.do('delete %s' % sel)

    def disable(self, name):
        '''
        Disables display of an object and all currently visible representations.
        '''
        self.srv.do('disable %s' % name)

    def distance(self,name,sel1,sel2):
        '''
        '''
        self.srv.do('distance %s, %s, %s' % (name,sel1,sel2))

    def extract(self,name,sel):
        '''
        extract name, selection [, source_state [, target_state ]]

        extract removes the atom selection from an object and creates it as its
        own object. This allows one to gain independent control over atoms in a
        scene by extracting them from the original object. For example, one can
        extract the hetero-atoms to their own object for independent manipulation.
        '''
        self.srv.do('extract %s, %s' % (name,sel))

    def fetch(self, pdbs, async=0):
        '''
        Loads structures from the PDB into PyMOL.
        '''
        if isinstance(pdbs, str): self.srv.do('fetch %s, async=%s' % (pdbs, async))
        else: self.srv.do('fetch %s, async=%s' % (' '.join(pdbs), async))

    def fit(self, sel_a, sel_b):
        '''
        Fit superimposes the model in the first selection on to the model in the second selection.
        Only matching atoms in both selections will be used for the fit.
        '''
        self.srv.do('fit %s, %s' % (sel_a, sel_b))

    def get_names(self, what='all', enabled_only=1):
        '''
        cmd.get_names( [string: "objects"|"selections"|"all"|"public_objects"|"public_selections"] )
        '''
        return self.srv.getNames(what,enabled_only)

    def grid_slot(self, slot, obj):
        '''
        Sets the grid slot location for a given object.
        '''
        self.set('grid_slot %s, %s' % (slot,obj))

    def group(self, name, *members, **kwargs):
        '''
        The Group command creates or updates a "group" object.
        The grouped objects are collected underneath a + sign in the object tree.
        '''
        action = kwargs.get('action','')
        members = map(str, members)

        if not action: self.srv.do('group %s, %s' % (name, ' '.join(members)))
        else: self.srv.do('group %s, %s' % (name, action))

    def hide(self,repr,obj=''):
        '''
        '''
        self.srv.do('hide %s, %s' % (repr,obj))

    def label(self,sel,label):
        '''
        '''
        self.srv.do("label %s, '%s'" % (sel,label))

    def load(self,file, obj=None):
        '''
        '''
        if not obj: self.srv.loadFile(file)
        else: self.srv.loadFile(file,obj)

    def loadPDBString(self, data, obj, colorscheme='', replace=1):
        '''
        Loads a molecule from a pdb string.
        Arguments:
            data:        the PDB block
            objName:     name of the object to create
            colorScheme: (OPTIONAL) name of the color scheme to use
                         for the molecule (should be either 'std' or one of the
                         color schemes defined in pymol.utils)
            replace:     (OPTIONAL) if an object with the same name already
                         exists, delete it before adding this one
        '''
        self.srv.loadPDB(data, obj, colorscheme, replace)

    def loadMolBlock(self, data, obj, colorscheme='', replace=1):
        '''
        Loads a molecule from a SDF Mol Block.
        Arguments:
            data:        the mol block
            objName:     name of the object to create
            colorScheme: (OPTIONAL) name of the color scheme to use
                         for the molecule (should be either 'std' or one of the
                         color schemes defined in pymol.utils)
            replace:     (OPTIONAL) if an object with the same name already
                         exists, delete it before adding this one
        '''
        self.srv.loadMolBlock(data, obj, colorscheme, replace)

    def orient(self, obj):
        '''
        '''
        self.srv.do('orient %s' % obj)

    def order(self, names, sort='yes', location=''):
        '''
        order allows you to change ordering of names in the control panel.
        1.  names-list: a space separated list of names
        2. sort: yes or no
        3. location: top, current, or bottom
        '''
        if type(names) == list: names = ' '.join(names)

        self.srv.do('order %s, %s %s' % (names, sort, location))

    def png(self, file, dpi=72):
        '''
        png writes a png format image file of the current image to disk.
        '''
        self.srv.do('png %s, dpi=%s' % (file, dpi))

    def pseudoatom(self, obj, pos, **kwargs):
        '''
        pseudoatom adds a pseudoatom to a molecular object, and will create the
        molecular object if it does not yet exist.
        '''
        chain = kwargs.get('chain',' ')
        res_num = kwargs.get('res_num','-1')
        res_name = kwargs.get('res_name','DUM')
        name = kwargs.get('name','DUM')
        color = kwargs.get('color','grey')
        element = kwargs.get('element','c')
        vdw = kwargs.get('vdw', 1.4)

        cmd = "pseudoatom %s, pos=[%s], segi='', name=%s, chain=%s, resi=%s, resn=%s, color=%s, elem=%s, vdw=%s"

        self.srv.do(cmd % (obj, ', '.join(map(str,pos)), name, chain, res_num, res_name, color, element, vdw))

    def rebuild(self):
        '''
        '''
        self.srv.do('rebuild')

    def remove(self, sel):
        '''
        '''
        self.srv.do('remove %s' % sel)

    def reset_cgo(self,id):
        '''
        '''
        self.srv.resetCGO(id)

    def select(self,name,sel):
        '''
        select creates a named selection from an atom selection.
        '''
        self.srv.do('select %s, %s' % (name,sel))

    def set(self,prop,val,obj=''):
        '''
        set is one of the most utilized commands. PyMOL representations, states,
        options, etc. are changed with set. Briefly, set changes one of the
        PyMOL state variables.
        '''
        self.srv.set(prop,val,obj)

    def set_bond(self, setting, value, sel=''):
        '''
        '''
        self.srv.do('set_bond %s, %s, %s' % (setting, value, sel))

    def set_color(self, name, rgb):
        '''
        '''
        self.srv.do('set_color %s, %s' % (name, rgb))

    def show(self,repr,obj=''):
        '''
        '''
        self.srv.do('show %s, %s' % (repr,obj))

    def spectrum(self, expression, palette, selection, minimum, maximum):
        '''
        '''
        self.srv.do('spectrum %s,palette=%s,selection=%s,minimum=%s,maximum=%s' % (expression,palette,selection,minimum,maximum))

    def sphere(self,coords,radius,color=(0.5,0.5,0.5),id='sphere',extend=1):
        '''
        Adds a sphere as CGO object to the specified location.
        '''
        self.srv.sphere(coords,radius,color,id,extend)

    def unset(self,prop,sel=''):
        '''
        '''
        self.srv.do('unset %s, %s' % (prop,sel))

    def zoom(self,sel,buf=2.0,state=0,complete=1):
        '''
        '''
        what = '%s, %s, %s, %s' % (sel,buf,state,complete)
        self.srv.zoom(what)
