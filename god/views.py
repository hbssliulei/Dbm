from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from models import Game

class IndexView(generic.ListView):
    model = Game
    template_name = 'index.html'

def test(request):
    gs = Game.objects.get(pk=16)
    ips = "11.11.11.11,22.22.22.22".split(",")
    gs.black_list.extend(ips)
    gs.save()
    return HttpResponse(gs.black_list)

