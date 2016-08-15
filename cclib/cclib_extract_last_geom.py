#!/usr/bin/env python

"""cclib_extract_last_geom.py: Extract the last geometry from any
quantum chemical output file (not just geometry optimizations) using
cclib. Name is the same stub, with the file extension replaced by
'.xyz'.
"""

from __future__ import print_function

import os.path

import cclib
from cclib.parser.utils import PeriodicTable

from qchem_make_opt_input_from_opt import \
    (form_molecule_section, form_molecule_section_from_fragments,
     parse_fragments_from_molecule, parse_user_input)


def getargs():
    """Get command-line arguments."""

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('outputfilename', nargs='+')

    parser.add_argument('--fragment', action='store_true')
    parser.add_argument('--trajectory', action='store_true')
    parser.add_argument('--suffix')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = getargs()

    pt = PeriodicTable()

    for outputfilename in args.outputfilename:

        job = cclib.parser.ccopen(outputfilename)
        try:
            data = job.parse()
        except Exception as e:
            print('no output made: {} in {}'.format(e, outputfilename))
            continue

        element_list = [pt.element[Z] for Z in data.atomnos]
        last_geometry = data.atomcoords[-1]

        stub = os.path.splitext(outputfilename)[0]
        if args.suffix:
            xyzfilename = ''.join([stub, '.', args.suffix, '.xyz'])
        else:
            xyzfilename = ''.join([stub, '.xyz'])

        if args.trajectory:
            cclib.writer.ccwrite(data, outputdest=xyzfilename, allgeom=True)
        else:
            with open(xyzfilename, 'w') as fh:
                fh.write(str(len(last_geometry)) + '\n')
                fh.write('\n')
                molecule_section = form_molecule_section(element_list, last_geometry, data.charge, data.mult)
                fh.write('\n'.join(molecule_section[1:]))
                fh.write('\n')
                print(xyzfilename)

            if args.fragment:
                # If this is from a Q-Chem fragment calculation, print a single
                # fragment "XYZ" file as well.
                if isinstance(job, cclib.parser.qchemparser.QChem):
                    user_input = parse_user_input(outputfilename)
                    charges, multiplicities, start_indices = parse_fragments_from_molecule(user_input['molecule'])
                    charges.insert(0, data.charge)
                    multiplicities.insert(0, data.mult)
                    molecule_section = form_molecule_section_from_fragments(element_list, last_geometry, charges, multiplicities, start_indices)

                    if args.suffix:
                        fragxyzfilename = ''.join([stub, '.', args.suffix, '.xyz_frag'])
                    else:
                        fragxyzfilename = ''.join([stub, '.xyz_frag'])

                    with open(fragxyzfilename, 'w') as fh:
                        fh.write('\n'.join(molecule_section))
                        fh.write('\n')
                        print(fragxyzfilename)
