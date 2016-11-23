'''
USAGE:

> awe make_sourcelist_high_s_n.py $KIDSOBJECT

with argument:
1) a KiDS OBJECT to make SourceList's from.

OPTIONAL ARGUMENT that will be used in SourceList query as filename.like, in
order to find exactly 4 SourceList's with given OBJECT and filename:
2) string of the SourceList attribute name, e.g. containing KiDS-CAT version,
KiDS DataRelease version, SourceList version, enclosed within asterisks (i.e. *)
FULL EXAMPLE:

> awe make_sourcelist_high_s_n.py 'KIDS_129.0_-0.5' '*KCv1.6*INTDR3v4*'
'''

from astro.main.SourceList import SourceList
from astro.main.sourcecollection.SourceListWrapper import SourceListWrapper
from astro.main.sourcecollection.FilterSources import FilterSources
from astro.main.sourcecollection.SelectSources import SelectSources

import sys
import subprocess
from datetime import date
import traceback

def make_filtered_sourcelist(sl):
    # Write filter of current SourceList to log file.
    with open(filename_log, 'a') as fp:
        fp.write(
          '%s\n' % sl.filter.name
        )

    # Make a SourceListWrapper from the selected SourceList.
    slw = SourceListWrapper()
    slw.set_sourcelist(sl)
    slw.commit()
    with open(filename_log, 'a') as fp:
        fp.write(
          'SourceListWrapper SCID %i\n' % slw.SCID
        )

    # Filter the sources with low signal-to-noise.
    fs = FilterSources()
    fs.parent_collection = slw
    fs.set_query('"FLUX_APER_10" / "FLUXERR_APER_10" > 5')
    fs.commit()
    with open(filename_log, 'a') as fp:
        fp.write(
          'FilterSources SCID %i\n' % fs.SCID
        )

    # Make a SelectSources and store into a new SourceList.
    ss = SelectSources()
    ss.parent_collection = slw
    ss.selected_sources = fs
    ss.commit()
    with open(filename_log, 'a') as fp:
        fp.write(
          'SelectSources SCID %i\n' % ss.SCID
        )
    ss.store_data(optimize=False)
    with open(filename_log, 'a') as fp:
        fp.write(
          'SourceList with high S/N sources SLID %i\n\n' % ss.sourcelist_data.SLID
        )

if __name__ == '__main__':
    try:
        kids_object = sys.argv[1]
    except:
        traceback.print_exc()

        print __doc__

        exit()

    try:
        sl_filename = sys.argv[2]
    except:
        sl_filename = None
        message = '''\nWARNING: No SourceList attribute name entered. Expecting
to find exactly 4 SourceList's in database.\n'''
        print message

    # Set filename for log file, and remove any previous ones with same filename.
    filename_log = '%s-%s-make_sourcelist_high_s_n.log' %\
      (date.today().isoformat().replace('-', ''), kids_object)
    subprocess.call('rm -rf %s' % filename_log, shell=True)

    if not sl_filename:
        sls = (SourceList.OBJECT == kids_object)
    else:
        sls = (SourceList.OBJECT == kids_object) &\
          (SourceList.filename.like(sl_filename))

    if len(sls) != 4:
        message = '\nQuery found %s SourceLists for %s; need exactly 4. Please try again.' %\
          (len(sls), kids_object)
        print message
        exit()

    lst = []
    filters = ['OCAM_i_SDSS', 'OCAM_r_SDSS', 'OCAM_g_SDSS', 'OCAM_u_SDSS']
    for i in filters:
        try:
            lst.append(
              [j for j in sls if j.filter.name == i][0]
            )
            message = '\nUsing %s name %s, SLID %i.' %\
              (i, lst[-1].name, lst[-1].SLID)
            print message
        except:
            traceback.print_exc()

            with open(filename_log, 'a') as fp:
                traceback.print_exc(file=fp)

            exit()

    sl_i, sl_r, sl_g, sl_u = lst[0], lst[1], lst[2], lst[3]

    for i in sl_i, sl_r, sl_g, sl_u:
        try:
            message = '%s filtering sources...' % i.filter.name
            print message

            make_filtered_sourcelist(i)

        except:
            traceback.print_exc()

            with open(filename_log, 'a') as fp:
                traceback.print_exc(file=fp)

            exit()
