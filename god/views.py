#-*- coding:utf-8 -*-
from django.shortcuts import render, get_list_or_404, render_to_response
from django.http import HttpResponse
from django.views import generic
from models import Game, Assets, dbBackup
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import json
import time, datetime

def global_setting(request):
    return {'SITE_NAME': settings.SITE_NAME}

def get_asset_ip(game):
     return list(set([i['ip'] for i in game.assets_set.values('ip').exclude(ip__in=game.black_list)]))


def get_max_date(game):
    try:
        new_date = max([i.get("curdate").strftime("%Y-%m-%d") for i in game.dbbackup_set.filter(backup_type=0).values('curdate').distinct()])
    except ValueError:
        new_date = None
    return new_date

def get_time(game):
    try:
        new_time = max([i['inc'] for i in game.dbbackup_set.values('inc')])
    except ValueError:
        new_time = None

    return new_time

class IndexView(generic.ListView):
    model = Game
    template_name = 'index.html'
    context_object_name = 'game_name_list'

    def get_queryset(self):
        game_name_list = [game['game_name'] for game in Game.objects.filter(status=0).values("game_name")]
        return game_name_list

def get_db_backup_data(request):
    result = []

    #获取项目
    games = Game.objects.filter(status=0)

    #获取各项目的机器ip
    for game in games:
        ret = {}

        ips = get_asset_ip(game)

        new_date = get_max_date(game)

        if new_date:
            full_backup_fail_ips = list(set(ips) - set(i['ip'] for i in game.dbbackup_set.filter(game=game, backup_type=0, curdate=new_date).values('ip').exclude(ip__in=game.black_list)))
        else:
            full_backup_fail_ips = list(set(ips) - set(i['ip'] for i in game.dbbackup_set.filter(game=game, backup_type=0).values('ip').exclude(ip__in=game.black_list)))


        new_time = get_time(game)
        if new_time:
            inc_backup_fail_ips = list(set(ips) - set([i['ip'] for i in game.dbbackup_set.filter(backup_type=1, game=game, inc=new_time).values('ip').exclude(ip__in=game.black_list)]))
        else:
            inc_backup_fail_ips = ips

        ret["name"] = game.game_name
        ret["name_cn"] = game.game_cn
        ret["date"] = new_date
        ret['time'] = new_time
        ret["ips"] = len(ips)
        ret["full_fail"] = full_backup_fail_ips
        ret['inc_fail'] = inc_backup_fail_ips

        result.append(ret)

    return HttpResponse(json.dumps(result))


def get_game_backup(request, game):

    game = Game.objects.get(game_name=game)
    ips = get_asset_ip(game)


    #获取该项目所有的ip
    backup_ips = game.dbbackup_set.values("ip").distinct().exclude(ip__in=game.black_list)

    #获取所有ip的完整备份的最后一次备份
    full_backup_fail_result = []

    #full_backup_data = game.dbbackup_set.filter(backup_type=0).values("ip", "curdate").exclude(ip__in=game.black_list)

    full_backup_fail_ips = list(set(ips) - set([i['ip'] for i in game.dbbackup_set.filter(backup_type=0, curdate=get_max_date(game)).values("ip").exclude(ip__in=game.black_list)]))

    if full_backup_fail_ips:
        for full_backup_ip in full_backup_fail_ips:
            full_backup_fail_ret = {}
            try:
                full_fail_data = game.dbbackup_set.filter(backup_type=0, ip=full_backup_ip).values().order_by("-curdate")[0]
            except:
                full_fail_data = None


            full_backup_fail_ret['game'] = game.game_cn
            full_backup_fail_ret['ip'] = full_backup_ip
            if full_fail_data:
                full_backup_fail_ret['date'] = full_fail_data['curdate']
            else:
                full_backup_fail_ret['date'] = "未备份"
            full_backup_fail_ret['type'] = "完整备份"


            full_backup_fail_result.append(full_backup_fail_ret)

    paginator = Paginator(full_backup_fail_result, 10)
    page = request.GET.get("page")
    try:
        full_content = paginator.page(page)
    except (EmptyPage, InvalidPage):
        full_content = paginator.page(1)


    inc_backup_fail_result = []

    inc_backup_fail_ips = list(set(ips) - set([i['ip'] for i in game.dbbackup_set.filter(backup_type=1, inc=get_time(game)).values("ip").exclude(ip__in=game.black_list)]))

    for inc_fail_ip in inc_backup_fail_ips:
        inc_backup_fail_ret = {}
        try:
            inc_fail_data = game.dbbackup_set.filter(backup_type=1, ip=inc_fail_ip).values().order_by("-inc")[0]
        except:
            inc_fail_data = None

        inc_backup_fail_ret['game'] = game.game_cn
        inc_backup_fail_ret['ip'] = inc_fail_ip
        inc_backup_fail_ret['type'] = "增量备份"
        if inc_fail_data:
            inc_backup_fail_ret['date'] = inc_fail_data['curdate']
            inc_backup_fail_ret["time"] = inc_fail_data['inc']
        else:
            inc_backup_fail_ret['date'] = "未备份"
            inc_backup_fail_ret['time'] = "未备份"

        inc_backup_fail_result.append(inc_backup_fail_ret)

    paginator = Paginator(inc_backup_fail_result, 10)
    page = request.GET.get("page")
    try:
        inc_content = paginator.page(page)
    except (EmptyPage, InvalidPage):
        inc_content = paginator.page(1)

    return render_to_response('detail.html', locals())


def test(request):
    gs = Game.objects.get(pk=16)
    ips = "11.11.11.11,22.22.22.22".split(",")
    gs.black_list.extend(ips)
    gs.save()
    return HttpResponse(gs.black_list)

