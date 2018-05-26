from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from .forms import Kyokigo_Form
from .kyokigo import kyoki
from django.http import HttpResponse
import datetime
import csv
from django.contrib.auth.mixins import LoginRequiredMixin



def index(request):
    form = Kyokigo_Form(request.POST or None)
    result = []
    kyokigo_n = []
    kyokigo_v = []

    if request.method == 'POST' and form.is_valid():
        form.save()
        keyword = request.POST['text']
        kyokigo_v,kyokigo_n = kyoki(keyword)
        #result = [["kyokigo_n","kyoukigo_v"]]
        result = [["keyword","2018/03/14","10","https://to-kei.net"]]


        return render(request, 'kyokigo/result.html',{'ranks': result,})

    context = {
        'form':form,
    }
    return render(request, 'kyokigo/form.html',context)
