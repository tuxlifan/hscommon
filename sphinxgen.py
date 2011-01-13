# Created By: Virgil Dupras
# Created On: 2011-01-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
import shutil
import re

from .build import print_and_do, read_changelog_file, filereplace

CHANGELOG_FORMAT = """
{version} ({date})
----------------------

{description}
"""

def tixgen(tixurl):
    """This is a filter *generator*. tixurl is a url pattern for the tix with a {0} placeholder
    for the tix #
    """
    urlpattern = tixurl.format('\\1') # will be replaced buy the content of the first group in re
    R = re.compile(r'#(\d+)')
    repl = '`#\\1 <{}>`__'.format(urlpattern)
    return lambda text: R.sub(repl, text)

def gen(basepath, buildpath, destpath, changelogpath, tixurl, confrepl=None):
    """Generate sphinx docs with all bells and whistles.
    
    basepath: The base sphinx source path.
    buildpath: The path shinx source will be copied to for in-source replacements
    destpath: The final path of html files
    changelogpath: The path to the changelog file to insert in changelog.rst.
    tixurl: The URL (with one formattable argument for the tix number) to the ticket system.
    confrepl: Dictionary containing replacements that have to be made in conf.py. {name: replacement}
    """
    if confrepl is None:
        confrepl = {}
    if op.exists(buildpath):
        shutil.rmtree(buildpath)
    shutil.copytree(basepath, buildpath)
    changelog = read_changelog_file(changelogpath)
    tix = tixgen(tixurl)
    rendered_logs = []
    for log in changelog:
        description = tix(log['description'])
        rendered = CHANGELOG_FORMAT.format(version=log['version'], date=log['date'],
            description=description)
        rendered_logs.append(rendered)
    confrepl['version'] = changelog[0]['version']
    filereplace(op.join(buildpath, 'changelog.rst'), changelog='\n'.join(rendered_logs))
    filereplace(op.join(buildpath, 'conf.py'), **confrepl)
    cmd = 'sphinx-build "{}" "{}"'.format(buildpath, destpath)
    print_and_do(cmd)
