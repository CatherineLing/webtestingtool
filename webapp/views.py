# Create your views here.
from django.forms.models import ModelForm
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django import forms

from webapp.tasks import runscript
from webapp.models import Case, Task, Step, Similarity
from webapp.parser import parse
from celery.result import AsyncResult
import json
from webapp.questionary import get_question, get_same_steps,\
    get_different_steps
import random
from django.http import HttpResponseRedirect


def case_list(request):
    cases = Case.objects.all()
    for case in cases:
        tasks = Task.objects.filter(case = case)
        case.state = ','.join([AsyncResult(task.taskid).state for task in tasks])
    return render_to_response(
        "webapp/case_list.html",
        locals(),
        context_instance = RequestContext(request))
    
class CaseForm(ModelForm):
    htmlfile = forms.FileField(label = "HtmlScript", required = False)
    use_firefox = forms.BooleanField(label = "Firefox", initial = True, required = False)
    use_chromium = forms.BooleanField(label = "Chromium", initial = True, required = False)
#    use_safari = forms.BooleanField(label = "Safari", initial = True, required = False)
#    use_camino = forms.BooleanField(label = "Camino", initial = True, required = False)
#    use_opera = forms.BooleanField(label = "Opera", initial = True, required = False)
#    use_ie = forms.BooleanField(label = "IE", initial = True, required = False)

    class Meta:
        model = Case
        exclude = ('url', 'script', 'invisiable_steps', 'task_num')

def get_similarity(current_step, browser_choices):
    for browser1, _ in browser_choices:
        for browser2, _ in browser_choices:
            try:
                step1_id = current_step[browser1].id
                step2_id = current_step[browser2].id
                if step1_id < step2_id:
                    s = Similarity.objects.get(step1 = current_step[browser1], step2 = current_step[browser2])
                else:
                    continue
                if s.no > s.yes / 2.0:
                    return False
            except:
                return None
    return True

def case_result(request, case_id):
    case = Case.objects.get(id = case_id)
    
    browser_choices = Task.BROWSER_CHOICES
    browser_steps = {}
    for browser, _ in browser_choices:
        browser_steps[browser] = Step.objects.filter(task__case = case, task__browser = browser).order_by('num')
    num_steps = max([len(bs) for bs in browser_steps.values()])
    if case.invisiable_steps != None and case.invisiable_steps != "":
        invisiable_steps = json.loads(case.invisiable_steps)
    else:
        invisiable_steps = []
    steps = []
    for i in range(num_steps):
        if not i in invisiable_steps:
            current_step = {}
            for browser, _ in browser_choices:
                if i < len(browser_steps[browser]):
                    current_step[browser] = browser_steps[browser][i]
                    

            sim = get_similarity(current_step, browser_choices)
            steps.append((i, [(browser, current_step.get(browser, None)) for browser, _ in browser_choices], sim)) 

    if request.method == 'POST':
        for browser, _ in browser_choices:
            for i in range(num_steps):
                if '%snotes_%d'%(browser, i) in request.POST:
                    notes = request.POST['%snotes_%d'%(browser, i)]
                    step = Step.objects.get(task__case = case, task__browser = browser.upper(), num = i)
                    if step != None:
                        step.notes = notes
                        step.save()
        for i in range(num_steps):
            visiable = "save_%d"%i in request.POST
            if visiable:
                for browser, _ in browser_choices:
                    step = Step.objects.get(task__case = case, task__browser = browser.upper(), num = i)
                    step.invisiable = False
                    step.save()
            else:
                invisiable_steps.append(i)
                for browser, _ in browser_choices:
                    step = Step.objects.get(task__case = case, task__browser = browser.upper(), num = i)
                    step.invisiable = True
                    step.save()
        case.invisiable_steps = json.dumps(invisiable_steps)
        case.save()
                
        return redirect('case_result', case_id = case_id)

    return render_to_response(
        "webapp/case_result.html",
        locals(),
        context_instance = RequestContext(request))
    
def case_delete(request, case_id):
    Case.objects.get(id = case_id).delete()
    return redirect('case_list')
  
def case_scheme(request, case_id):
    case = Case.objects.get(id = case_id)
    script = json.loads(case.script)

    return render_to_response(
        "webapp/case_scheme.html",
        locals(),
        context_instance = RequestContext(request))
    
def case_detail(request, case_id):
    if case_id == '0':
        case = Case()
        script = []
    else:
        case = Case.objects.get(id = case_id)
        script = json.loads(case.script)
    
    if request.method == 'POST':
        form = CaseForm(request.POST, request.FILES, instance = case)

        if form.is_valid():
            if 'htmlfile' in request.FILES:
                htmlscript = request.FILES['htmlfile'].read()
                url, script = parse(htmlscript)
                case.url = url
                case.script = json.dumps(script)

            case.task_num = 0

            if request.POST.get('use_firefox', False):
                result = runscript.delay(case, "F", case.url, script)
                case.task_num += 1
            if request.POST.get('use_chromium', False):
                result = runscript.delay(case, "C", case.url, script)
                case.task_num += 1
#            if request.POST.get('use_safari', False):
#                result = runscript.delay(case, "S", case.url, script)
            if request.POST.get('use_opera', False):
                result = runscript.delay(case, "O", case.url, script)
                case.task_num += 1
            if request.POST.get('use_ie', False):
                result = runscript.delay(case, "I", case.url, script)
                case.task_num += 1

            case.save()
        
            return redirect('case_scheme', case_id = case.id)
    else:
        form = CaseForm(instance = case)
       
    return render_to_response(
        "webapp/case_detail.html",
        locals(),
        context_instance = RequestContext(request))

def questionary_start(request):
    if request.method == 'POST':
        request.session.clear()
        request.session['test'] = 3
        request.session['questionary'] = 10
        request.session['credential'] = True

        return HttpResponseRedirect('questionary')
    else:
        return render_to_response(
            "webapp/questionary_start.html",
            locals(),
            context_instance = RequestContext(request))
        
def questionary(request):
    if request.method == 'POST':
        step1_id = request.POST['step1_id']
        step2_id = request.POST['step2_id']
        result = request.POST.get('result', None)
        if result == "True":
            result = True
        elif result == "False":
            result = False
        expected_result = request.POST['expected_result']
        if expected_result == "True":
            expected_result = True
        elif expected_result == "False":
            expected_result = False
        elif expected_result == "None":
            expected_result = None
        
        
        if result != None:
            if expected_result == None:
                step1 = Step.objects.get(id = min([step1_id, step2_id]))
                step2 = Step.objects.get(id = max([step1_id, step2_id]))
                
                sim, _ = Similarity.objects.get_or_create(
                        step1 = step1,
                        step2 = step2)
                if result == True:
                    sim.yes += 1
                elif result == False:
                    sim.no += 1
                sim.save()
                
                step1.compare_times += 1; step1.save()
                step2.compare_times += 1; step2.save()
                
            else:
                if expected_result != result:
                    request.session['credential'] = False
                    
                    
            
#            request.session['result'].append((step1_id, step2_id, result, expected_result))
#            request.session['num'] = num

    step1 = step2 = None        
    if request.session['test'] > 0 and request.session['credential'] == True:
        try:
            if random.random() < .5:
                expected_result = True
                step1, step2 = get_same_steps()
            else:
                expected_result = False
                step1, step2 = get_different_steps()
            request.session['test'] -= 1
        except:
            request.session['test'] = 0
        
    if request.session['questionary'] > 0 \
        and request.session['credential'] == True:
        if step1 == None or step2 == None:
            expected_result = None
            step1, step2 = get_question()
            
            request.session['questionary'] -= 1
        
        return render_to_response(
            "webapp/questionary.html",
            locals(),
            context_instance = RequestContext(request))
    else:
        return render_to_response(
            "webapp/questionary_end.html",
            locals(),
            context_instance = RequestContext(request))
        

        