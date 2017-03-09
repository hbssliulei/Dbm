#-*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

import json
import datetime
import requests

from django.conf import settings
from models import Game, Assets, dbBackup

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

def global_setting(request):
    return {'SITE_NAME': settings.SITE_NAME}

def get_asset_ip(game):
    return list(set([i['ip'] for i in game.assets_set.values('ip').exclude(ip__in=game.black_list)]))


def get_max_date(game):
    try:
        new_date = max([i.get("curdate") for i in game.dbbackup_set.filter(backup_type=0).values('curdate').distinct()])
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
        #game_name_list = [game['game_name'] for game in Game.objects.filter(status=0).values("game_name")]
        game_name_list = [game.get("game__game_name") for game in Assets.objects.select_related().values("game__game_name").distinct()]
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


            full_backup_fail_ret['game_cn'] = game.game_cn
            full_backup_fail_ret['game_name'] = game.game_name
            full_backup_fail_ret['ip'] = full_backup_ip
            if full_fail_data:
                full_backup_fail_ret['date'] = full_fail_data['curdate'].strftime("%Y-%m-%d")
            else:
                full_backup_fail_ret['date'] = "未备份"
            full_backup_fail_ret['type'] = "完整备份"


            full_backup_fail_result.append(full_backup_fail_ret)

    full_backup_fail_result.sort()

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

        inc_backup_fail_ret['game_cn'] = game.game_cn
        inc_backup_fail_ret['game_name'] = game.game_name
        inc_backup_fail_ret['ip'] = inc_fail_ip
        inc_backup_fail_ret['type'] = "增量备份"
        if inc_fail_data:
            inc_backup_fail_ret['date'] = inc_fail_data['curdate'].strftime("%Y-%m-%d")
            inc_backup_fail_ret["time"] = inc_fail_data['inc']
        else:
            inc_backup_fail_ret['date'] = "未备份"
            inc_backup_fail_ret['time'] = "未备份"

        inc_backup_fail_result.append(inc_backup_fail_ret)

    inc_backup_fail_result.sort()

    paginator = Paginator(inc_backup_fail_result, 10)
    page = request.GET.get("page")
    try:
        inc_content = paginator.page(page)
    except (EmptyPage, InvalidPage):
        inc_content = paginator.page(1)

    return render_to_response('detail.html', locals())


@csrf_exempt
@require_http_methods(['POST'])
def saveDB(request):

    game_list = Game.objects.all()

    #从资产里拉到各项目的ip
    for game in game_list:
        url = "http://xxx.xxx.com/api?t=ip&game={}&status=1".format(game.game_name)

        ips = ( ip.get("ip") for ip in json.loads(requests.get(url).text))

        assetsIps = [ip.get("ip") for ip in game.assets_set.filter(datetime=TODAY).values("ip")]


        for ip in ips:
            if ip not in assetsIps:
                inAsset = game.assets_set.create(ip=ip, datetime=TODAY)

    ip = request.POST.get("ip")
    curdate = request.POST.get("curdate")
    inc = request.POST.get("name").split(".")[0].split("_")[1]
    status = request.POST.get("status")
    game_name = Assets.objects.select_related().filter(ip=ip, datetime=TODAY).values("game__game_name")[0].get("game__game_name")

    game = Game.objects.get(game_name=game_name)

    try:
        line = game.dbbackup_set.create(ip=ip, curdate=curdate, inc=inc, backup_type=status)
    except Exception as e:
        return HttpResponse("fail")
    return HttpResponse("ok")

def addTestIp(request):
    """
    该接口可为各项目添加测试机器ip
    """
    game_name = request.GET.get('game')
    ip = request.GET.get('ip')

    game = Game.objects.get(game_name=game_name)
    game.black_list.append(ip.encode("utf-8"))
    game.save()

    return HttpResponseRedirect(reverse('god:get_game_backup', args=[game_name]))

@csrf_exempt
@require_http_methods(['POST'])
def online(request):
    game_name = request.POST.get("game_name")
    game_cn = request.POST.get("game_cn")
    black_list = request.POST.get("black_list")

    if not Game.objects.filter(game_name=game_name).exists():
        add_ret = Game(game_name=game_name, game_cn=game_cn, black_list=black_list)
        try:
            add_ret.save()
        except Exception as e:
            print e
            return HttpResponse("fail")
        return HttpResponse("ok")
    else:
        return HttpResponse("exist")

@csrf_exempt
@require_http_methods(['POST'])
def offline(request, game):
    """
    当项目下线时，可调用该接口更改该项目的状态
    """
    try:
        game = Game.objects.filter(game_name=game).update(status=1)
    except Exception as e:
        return HttpResponse(e)

    return HttpResponse("ok")

def checkBackupStatus(request):

    game_list = Game.objects.all()

    one_hour_ago = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%H%M")

    backupResult = {}

    for game in game_list:
        url = "http://xxx.xxx.com/api?t=ip&game={}&status=1".format(game.game_name)
        ips = [ ip.get("ip") for ip in json.loads(requests.get(url).text) ]
        try:
            checkTime = game.dbbackup_set.filter(curdate=TODAY, backup_type=1).values("inc").order_by("-inc")[1].get("inc")
        except Exception:
            checkTime = None

        assetsIps = [ip.get("ip") for ip in game.assets_set.values("ip").exclude(ip__in=game.black_list)]

        backupIp = [ip.get("ip").encode("utf-8") for ip in game.dbbackup_set.filter(curdate=TODAY, backup_type=1, inc=checkTime).values("ip")]

        backupResult[game.game_name] = list(set(assetsIps) - set(backupIp))

    backupFailNum = 0
    for game, ips in backupResult.items():
        backupFailNum += len(ips)

    return HttpResponse(backupFailNum)
