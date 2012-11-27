'''
Created on Nov 21, 2012

@author: ling
'''
from django.db.models.signals import post_save, pre_delete
from webapp.models import Task, Similarity
from django.dispatch.dispatcher import receiver

@receiver(post_save, sender = Similarity)
def post_save_similiarity(sender, instance, signal, created, **kwargs):
    if created:
        sim = instance
        sim.step1.compare_times += 1
        sim.step1.save()
        sim.step2.compare_times += 1
        sim.step2.save()
        
@receiver(pre_delete, sender = Similarity)
def pre_delete_similiarity(sender, instance, signal, **kwargs):
    sim = instance
    sim.step1.compare_times -= 1
    sim.step1.save()
    sim.step2.compare_times -= 1
    sim.step2.save()
