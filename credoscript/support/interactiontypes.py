"""
Each contact in CREDO is classified based on the kind of macromolecular interaction
it takes part in. This file serves as a namespace containing the structural_interaction_type_bm
used in the contacts table. The structural_interaction_type_bm is created by first
shifting the bit mask of the first entity type bit mask by six positions to make
room for the second; the second
"""

try:
    from itertools import combinations_with_replacement
except ImportError:
    def combinations_with_replacement(iterable, r):
        """
        combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
        """
        pool = tuple(iterable)
        n = len(pool)
        if not n and r:
            return
        indices = [0] * r
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(range(r)):
                if indices[i] != n - 1:
                    break
            else:
                return
            indices[i:] = [indices[i] + 1] * (r - i)
            yield tuple(pool[i] for i in indices)

def show_bit_mask(bit_mask):
    """
    """
    return '{:012b}'.format(bit_mask)

# tuple list in the form entity / entity type bit mask
l = [('PRO',32), ('DNA',16), ('RNA',8), ('SAC',4), ('LIG',2), ('WAT',1), ('UNK',0)]

# create combinations of entity types
for (a, aval), (b, bval) in combinations_with_replacement(l, 2):

    struct_int_type_ab = (aval << 6) + bval
    struct_int_type_ba = (bval << 6) + aval

    exec("{0}_{1} = {2}".format(a, b, struct_int_type_ab))
    exec("{0}_{1} = {2}".format(b, a, struct_int_type_ba))

# remove unused variables so they will not appear in import
del a,b,aval,bval,struct_int_type_ab,struct_int_type_ba,l