from django.db import models

# Create your models here.
class Case(models.Model):
    url = models.URLField()
    script = models.CharField(max_length = 100 * 1024)
    invisiable_steps = models.CharField(max_length = 255, blank = True, null = True)
    task_num = models.IntegerField(default = 0)

    def __unicode__(self):
        return unicode(self.url)
    
class Task(models.Model):
    BROWSER_CHOICES = (
        ('F', 'Firefox'),
        ('C', 'Chromium'),
#        ('S', 'Safari'),
#        ('A', 'Camino'),
#        ('O', 'Opera'),
#        ('I', 'IE'),
    )
    
    case = models.ForeignKey(Case)
    browser = models.CharField(max_length = 1, choices = BROWSER_CHOICES) 
    taskid = models.CharField(max_length = 50, blank = True, null = True)
    
    def __unicode__(self):
        return u"(%s)%s"%(self.browser, self.case)
    
class Step(models.Model):
    task = models.ForeignKey(Task)
    num = models.IntegerField()
    command = models.CharField(max_length = 255)
    param1 = models.CharField(max_length = 1024)
    param2 = models.CharField(max_length = 1024)
    picture = models.CharField(max_length = 20, blank = True, null = True)
    notes = models.CharField(max_length = 255, blank = True, null = True)
    invisiable = models.BooleanField(default = False)
    compare_times = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return u"%s---%s"%(self.task, self.command)

class Similarity(models.Model):
    step1 = models.ForeignKey(Step, related_name = "step1")
    step2 = models.ForeignKey(Step, related_name = "step2")
    yes = models.IntegerField(default = 0)
    no = models.IntegerField(default = 0)
    