'''
Created on Oct 6, 2012

@author: lingxingjian
'''
import celery

from selenium import selenium
from webtestingtool.settings import MEDIA_ROOT
from webapp.models import Task, Step
from celery.exceptions import SoftTimeLimitExceeded

@celery.task(soft_time_limit=90, name='webapp.tasks.runscript')
def runscript(case, browser, url, scripts):
    sel = None
    try:
        if browser == "F":
            browser_full = "*firefox"
        elif browser == "C":
#            browser_full = r"*googlechrome C:\Program Files\Google\Chrome\Application\chrome.exe"
            browser_full = "*googlechrome"
        elif browser == "S":
            browser_full = "*safari"
        elif browser == "O":
            browser_full = "*opera"
        elif browser == "I":
            browser_full = "*iexploreproxy"
            
        print "Browser:", browser_full
    
        Task.objects.filter(case = case, browser = browser).delete()
        task = Task(case = case, browser = browser, taskid = runscript.request.id)
        task.save()
        
        sel = selenium("localhost", 4444, browser_full, url)
        try:
            sel.start()
            sel.window_focus()
            sel.window_maximize()
            for num, (cmd, param1, param2) in zip(range(len(scripts)), scripts):
                sel.do_command(cmd, [param1, param2])
                filename = '%s/records/%s_%d.png'%(MEDIA_ROOT, runscript.request.id, num)
                fileurl = "/media/records/%s_%d.png"%(runscript.request.id, num)
                Step(task = task, num = num, command = cmd, param1 = param1, param2 = param2, picture = fileurl).save()
                sel.capture_screenshot(filename)
        except Exception as e:
            print e
            raise e
        finally:
            sel.stop()
    except SoftTimeLimitExceeded:
        print "time limit exceeded..."
        if sel != None:
            sel.stop()

