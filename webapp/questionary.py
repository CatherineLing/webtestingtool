'''
Created on Nov 21, 2012

@author: ling
'''
from webapp.models import Step, Similarity
import random
MAX_ATTEMPTS = 10

def get_different_steps():
    for _ in range(MAX_ATTEMPTS):
        step1 = Step.objects.order_by('?')[0]
        step2 = Step.objects.order_by('?')[0]
        if step1.num != step2.num:
            return (step1, step2)
    raise Exception("can not find different steps")

def get_same_steps():
    sim = Similarity.objects.filter(yes__gt = 0).filter(no = 0).order_by('?')[0]
    return (sim.step1, sim.step2)

def select(queryset):
    r = random.random()
    n = len(queryset)
    s = 0
    for i in range(n):
        s += 1.0 / 2 ** (i + 1) / (1.0 - 1.0 / 2 ** n)
        if r < s:
            return queryset[i]
        
    
def get_question():
    step1 = select(Step.objects.filter(task__case__task_num__gt = 1)\
                               .filter(invisiable = False)\
                               .order_by('compare_times'))
    step2 = select(Step.objects.filter(task__case = step1.task.case)\
                                .exclude(task = step1.task)\
                                .filter(num = step1.num)\
                                .order_by('compare_times'))
    return (step1, step2)
                        