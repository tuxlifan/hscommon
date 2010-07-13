# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from __future__ import unicode_literals

import re
import yaml
import markdown

from hsutil import io
from hsutil.path import Path

MAIN_CONTENTS = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	{meta}
    <title>{title}</title>
    <link rel="SHORTCUT ICON" href="/favicon.ico" />
    <link rel="stylesheet" href="{relpath}hardcoded.css" type="text/css" />
  </head>
  <body>
    <div class="mainlogo">
      <a href="http://www.hardcoded.net"><img src="{relpath}images/hs_title.png" alt="HS Logo" /></a>
    </div>
    <div class="maincontainer">
      <table>
      <tr valign="top">
		<td><h1>{title}</h1>{contents}</td>
        <td class="menuframe">
          <div class="menu">
			  {menu}
          </div>
        </td>
      </tr>
      </table>
    </div>
  </body>
</html>
"""

MENU_CONTENTS = """
<a class="{menuclass}" href="{relpath}{link}">{name}</a>
<span class="titleline"> </span>
<span class="titledescrip">{desc}</span>
"""

CHANGELOG = """
<table class="hardcoded">
<tr class="header">
<td>Version</td>
<td style="width:56pt;">Date</td>
<td>Description</td>
</tr>
{contents}
</table>
"""

CHANGELOG_ITEM = """
<tr>
<td>{version}</td>
<td>{date}</td>
<td>{description}</td>
</tr>
"""

def tixgen(tixurl):
    """This is a filter *generator*. tixurl is a url pattern for the tix with a {0} placeholder
    for the tix #
    """
    urlpattern = tixurl.format('\\1') # will be replaced buy the content of the first group in re
    R = re.compile(r'#(\d+)')
    repl = '[#\\1]({0})'.format(urlpattern)
    return lambda text: R.sub(repl, text)

class Page(object):
    def __init__(self, pagedata, pagespath):
        self.name = pagedata['name']
        self.basename = Path(self.name)[-1]
        self.basepath = Path(self.name)[:-1]
        self.path = pagespath + self.basepath + '{0}.md'.format(self.basename)
        self.title = pagedata['title']
        self.relpath = '../' * len(self.basepath)
        self.meta = ''
    
    def render(self, destpath, menu, env):
        dest = destpath + self.basepath + '{0}.htm'.format(self.basename)
        if not io.exists(dest[:-1]):
            io.makedirs(dest[:-1])
        mdcontents = unicode(io.open(self.path).read(), 'utf-8')
        mdcontents = mdcontents.format(**env)
        main_contents = markdown.markdown(mdcontents)
        rendered = MAIN_CONTENTS.format(meta=self.meta, title=self.title, relpath=self.relpath,
            menu=menu, contents=main_contents)
        fp = io.open(dest, 'w')
        fp.write(rendered.encode('utf-8'))
        fp.close()
    

class MainPage(Page):
    def __init__(self, pagedata, pagespath):
        Page.__init__(self, pagedata, pagespath)
        self.menutitle = pagedata['menutitle']
        self.menudesc = pagedata.get('menudesc', self.title)
        self.subpages = [Page(data, pagespath) for data in pagedata.get('subpages', [])]
    
    def build_menu(self, pages):
        menu_items = []
        for page in pages:
            menuclass = 'menuitem_selected' if page is self else 'menuitem'
            link = '{0}.htm'.format(page.name)
            contents = MENU_CONTENTS.format(menuclass=menuclass, relpath=self.relpath, link=link,
            name=page.menutitle, desc=page.menudesc)
            menu_items.append(contents)
        return ''.join(menu_items)
    
    def render(self, destpath, pages, env):
        menu = self.build_menu(pages)
        for page in self.subpages:
            page.render(destpath, menu, env)
        Page.render(self, destpath, menu, env)
    

def render_changelog(changelog, tixurl):
    items = []
    tix = tixgen(tixurl)
    for item in changelog:
        date = item['date']
        version = item['version']
        description = markdown.markdown(tix(item['description']))
        rendered = CHANGELOG_ITEM.format(date=date, version=version, description=description)
        items.append(rendered)
    rendered_items = ''.join(items)
    return CHANGELOG.format(contents=rendered_items)

def gen(basepath, destpath, profile=None):
    basepath = Path(basepath)
    destpath = Path(destpath)
    configpath = basepath + 'conf.yaml'
    confall = yaml.load(io.open(configpath))
    conf = confall['base']
    if profile and profile in confall:
        conf.update(confall[profile])
    tixurl = conf['tixurl']
    changelogpath = basepath + conf['changelog']
    changelogdata = yaml.load(io.open(changelogpath))
    changelog = render_changelog(changelogdata, tixurl)
    if 'env' in conf:
        envpath = basepath + conf['env']
        env = yaml.load(io.open(envpath))
    else:
        env = {}
    env['changelog'] = changelog
    pagespath = basepath + conf['pages']
    pagedatas = yaml.load(io.open(pagespath))
    pages = [MainPage(pagedata, pagespath=pagespath[:-1]) for pagedata in pagedatas]
    skelpath = basepath + Path(conf['skeleton'])
    if not io.exists(destpath):
        print "Copying skeleton"
        io.copytree(skelpath, destpath)
    pages[0].meta = conf.get('firstpage_meta', '')
    for i, page in enumerate(pages):
        print "Rendering {0}".format(page.name)
        page.render(destpath, pages, env)
