'''
Created on Oct 15, 2012

@author: ling
'''
import os, sys
sys.path.append('/usr/local/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'webtestingtool.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()