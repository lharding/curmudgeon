#!/usr/bin/python

import pystache
import glob
import sys
from operator import itemgetter
import os
import shutil
import distutils.dir_util
import datetime

# 0. Configure
cfgFile = 'curmudgeon_conf.py'

# if conf was specified, use it
if len(sys.argv) > 1:
	cfgFile = sys.argv[1]
	
print "Using config file "+cfgFile
execfile(cfgFile)

outpath = os.path.abspath(OUTPUT_DIR)

# 1. Build mustache model

model = {
	'posts': 	[],
	'url_prefix':	URL_PREFIX,
	'page_title':	BLOG_TITLE, 
	'blog_title':	BLOG_TITLE,
	'blog_host':	BLOG_HOST, 
	'now': 		datetime.datetime.now()
}

fnames = glob.glob(POSTS_DIR+'/*/*.'+SUFFIX)

for fname in fnames:
	try:
		post = {}
		print fname
		f = open(fname, 'r')
		lines = f.readlines()
		post['filename'] = fname
		# trim extension and replace with suffix
		post['outfile'] = fname[:-(len(SUFFIX)+1)] + POST_SUFFIX 
		post['title'] = lines[0]
		post['date'] = lines[1]
		post['frontpage'] = True
		post['url_prefix'] = URL_PREFIX
		post['page_title'] = BLOG_TITLE + ' - ' + lines[0]
		post['blog_title'] = BLOG_TITLE
		post['blog_host' ] = BLOG_HOST	
		post['body'] = pystache.render(u''.join(lines[2:]), post)

		model['posts'].append(post)
	except:
		print "Error:", sys.exc_info()[0]
		raise
				
model['posts'] = sorted(model['posts'], key=itemgetter('date'))
model['posts'].reverse()

distutils.dir_util.copy_tree(SKELETON_DIR, outpath)

#change into templates directory because pystache is inflexible
os.chdir(TEMPLATE_DIR)

# 2. Generate frontpage
with open(outpath + '/' + FRONTPAGE_FILE, 'w') as f:
	f.write(pystache.render('{{> frontpage}}', model))

# 3. Generate post pages
for post in model['posts']:
	post['frontpage'] = False #not on frontpage any more
	filename = outpath + '/' + post['outfile']
	pathname = os.path.dirname(filename)
	if not os.path.exists(pathname):
		os.makedirs(pathname)
	
	with open(filename, 'w') as f:
		f.write(pystache.render('{{> post_full}}', post))

# 4. Generate archive file:
with open(outpath + '/' + ARCHIVE_FILE, 'w') as f:
	f.write(pystache.render('{{> archive}}', model))

# 5. Generate feed:
with open(outpath + '/' + FEED_FILE, 'w') as f:
	f.write(pystache.render('{{> feed}}', model))
