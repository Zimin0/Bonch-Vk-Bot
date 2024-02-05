import requests
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from social_core.utils import setting_name

from .battlenet.oauth2 import BattleNetOAuth2
from users.models import User, GameAccount, Platform

NAMESPACE = getattr(
    settings, setting_name('URL_NAMESPACE'), None) or 'social_battlenet'

err_text = (
    "У нас не получилось привязать Battle.net к вашему аккаунту, "
    "убедитель в том что вы переходите по ссылке из бота вк. "
    "И что у нас на устройстве можно сохрянять данные cookies."
)


class IndexView(View):

    def get(self, request):
        core_id = request.GET.get('id')
        html = HttpResponse(render(request, 'auth_battlenet.html'))
        html.set_cookie(key="cyber_piter_id", value=str(core_id))
        return html


class LoginView(View):

    def get(self, request):
        bnet = BattleNetOAuth2()
        url, state = bnet.get_authorization_url()
        request.session['state'] = state
        return HttpResponseRedirect(url)


class CompleteView(View):

    def get(self, request):
        core_id = request.COOKIES.get("cyber_piter_id")
        if core_id == "None":
            return HttpResponse(err_text)
        user = User.objects.filter(id=core_id).first()
        if not user:
            return HttpResponse(err_text)

        if request.GET.get('code'):
            if request.GET.get('state') and request.session.get('state'):
                if request.GET['state'] == request.session['state']:
                    bnet = BattleNetOAuth2()
                    data = bnet.retrieve_access_token(request.GET['code'])
                    params = {
                        "region": "us",
                        "access_token": data['access_token'],
                    }
                    url = "https://oauth.battle.net/oauth/userinfo"
                    response = requests.get(url, params=params).json()

                    if 'battletag' in response:
                        platform = Platform.objects.filter(
                            name="Battle.net").first()
                        battle_tag = response['battletag'].split('#')
                        user_acc = GameAccount(
                            nick_name=battle_tag[0],
                            user=user,
                            platform=platform,
                            platform_token=data['access_token']
                        )
                        try:
                            user_acc.save()
                        except IntegrityError:
                            print("Аккаунт уже привязан")
                        return redirect(
                            "https://vk.com/im?sel=-67877749")
        return HttpResponse(err_text)
