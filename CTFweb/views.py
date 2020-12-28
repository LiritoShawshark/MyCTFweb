# -*- coding:utf-8 -*-
import math
import os
import random

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse, StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from CTFweb import models
from django.template.defaulttags import register


def home(request):
    login_name = ''
    if request.session.get('id'):
        user = models.User.objects.get(id=request.session.get('id'))
        login_name = user.username
    user_list = models.User.objects.all()[:3]
    team_list = models.Team.objects.all()[:3]
    return render(request, 'new_main.html', locals())


def help(request):
    return render(request, 'HELP_DOC.html')


def regist(request):
    if request.session.get('id') != None:   # 只有不在登录状态时才可以进行注册
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        noway = ["*", "(", ")", "=", "'", '"', "\\", "/", ",", '.', '%', '$', '&', '|']
        for n in noway:
            if n in username:
                message = "用户名中包含敏感字符"
                return render(request, 'Register.html', {"message": message})
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        stu_id = request.POST.get('stu_id')
        if password1 != password2:
            message = '两次密码不相同'
            return render(request, 'Register.html', {"message": message})
        for n in noway:
            if n in password1:
                message = "密码中包含敏感字符"
                return render(request, 'Register.html', {"message": message})
        if len(username) < 4 or len(username) > 15:
            message = '用户名请在4~15位间'
            return render(request, 'Register.html', {"message": message})
        if len(password1) < 6 or len(password1) > 15:
            message = '密码请在6~15位间'
            return render(request, 'Register.html', {"message": message})
        if len(stu_id) != 10:
            message = '学号错误'
            return render(request, 'Register.html', {"message": message})
        if models.User.objects.filter(stu_id=stu_id):
            message = '学号重复'
            return render(request, 'Register.html', {"message": message})
        if models.User.objects.filter(username=username).exists():
            message = '该用户名已被注册'
            return render(request, 'Register.html', {"message": message})
        new_User = models.User()
        new_User.username = username
        new_User.password = password1
        new_User.stu_id = stu_id
        new_User.save()
        request.session['id'] = new_User.id
        return redirect('/')
    return render(request, 'Register.html')


def logout(request):
    request.session.flush()
    return redirect('/')


def login(request):

    if request.session.get('id') != None:   # 只有不在登录状态时才可以进行注册
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            username = username.strip()
            password = password.strip()
            try:
                user = models.User.objects.get(username=username)
            except:
                message = '该用户名不存在'
                return render(request, 'LogIn.html', locals())
            if user.password == password:
                request.session['id'] = user.id
                return redirect('/')
            else:
                message = '密码错误'
                return render(request, 'LogIn.html', locals())
    return render(request, 'LogIn1.html')


def forget(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        stu_id = request.POST.get('stu_id')
        if not models.User.objects.filter(username=username).exists():
            message = '用户名不存在'
            return render(request, 'forget.html', locals())
        user = models.User.objects.get(username=username)
        if stu_id != user.stu_id:
            message = 'student id错误'
            return render(request, 'forget.html', locals())
        message = user.password
        return render(request, 'forget.html', locals())
    return render(request, 'forget.html')


def reset(request):
    if request.session.get('id') == None:
        return redirect('/')
    user = models.User.objects.get(id=request.session.get('id'))
    if request.method == 'POST':
        username = request.POST.get('username')
        stu_id = request.POST.get('stu_id')
        old_password = request.POST.get('pw1')
        new_password = request.POST.get('pw2')
        user = models.User.objects.get(id=request.session.get('id'))
        if user.username != username:
            message = '用户名错误'
            return render(request, 'reset.html', locals())
        if user.stu_id != stu_id:
            message = 'student id错误'
            return render(request, 'reset.html', locals())
        if user.password != old_password:
            message = '原密码错误'
            return render(request, 'reset.html', locals())
        user.password = new_password
        user.save()
        message = '密码修改成功'
        return render(request, 'reset.html', locals())
    return render(request, 'reset.html', locals())


def info(request):
    login_name = ''
    user_id = 0
    if request.method == 'GET':
        user_id = request.GET.get('id')
    if user_id == 0:
        return redirect('/')
    web = len(models.Problem.objects.filter(type=1))
    misc = len(models.Problem.objects.filter(type=2))
    pwn = len(models.Problem.objects.filter(type=3))
    crypto = len(models.Problem.objects.filter(type=4))
    reverse = len(models.Problem.objects.filter(type=5))
    if request.session.get('id'):
        user = models.User.objects.get(id=request.session.get('id'))
        me = user
        login_name = me.username
        is_myself = 1
        user_id = int(user_id)
        if user_id != user.id:
            user = models.User.objects.get(id=user_id)
            is_myself = 0
    else:
        user = models.User.objects.get(id=int(user_id))
        is_myself = 0
    if user.answers != 0:
        web_percent = round(user.web / user.answers * 100, 2)
        crypto_percent = round(user.crypto / user.answers * 100, 2)
        misc_percent = round(user.misc / user.answers * 100, 2)
        pwn_percent = round(user.pwn / user.answers * 100, 2)
        reverse_percent = round(100 - web_percent - crypto_percent - misc_percent - pwn_percent, 2)
    return render(request, 'personal1.html', locals())


def team(request):
    if request.session.get('id') == None:
        return redirect('/')
    user = models.User.objects.get(id=request.session.get('id'))
    web_list = models.Problem.objects.filter(type=1)
    misc_list = models.Problem.objects.filter(type=2)
    pwn_list = models.Problem.objects.filter(type=3)
    crypto_list = models.Problem.objects.filter(type=4)
    reverse_list = models.Problem.objects.filter(type=5)
    web = len(web_list)
    misc = len(misc_list)
    pwn = len(pwn_list)
    crypto = len(crypto_list)
    reverse = len(reverse_list)
    if user.team == None:
        login_name = user.username
        team_list = models.Team.objects.all()
        return render(request, 'no_team.html', locals())
    teammate_list = models.User.objects.filter(team=user.team)
    application_list = models.user_application.objects.filter(team=user.team)
    if user.team.leader == user.username:
        return render(request, 'leader_team.html', locals())
    else:
        return render(request, 'not_leader_team.html', locals())


def teamCreate(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if user.team != None:
        return redirect('/team/')
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        motto = request.POST.get('motto')
        same_name = models.Team.objects.filter(team_name=team_name)
        if same_name:
            message = '该队名已被注册'
            return render(request, 'no_team.html', {"message": message})
        new_Team = models.Team()
        new_Team.team_name = team_name
        new_Team.motto = motto
        new_Team.leader = user.username
        new_Team.answers = user.answers
        new_Team.scores = user.scores         # 创建时将组长的分数计入
        new_Team.save()
        user.team = new_Team
        user.save()
        pro_list_try = models.Answer_Ship.objects.filter(user=user).exists()
        if pro_list_try:
            pro_list = models.Answer_Ship.objects.filter(user=user)
            for pro in pro_list:
                new_ship = models.Problem_Team_Ship()
                new_ship.team = new_Team
                new_ship.problem = pro.problem
                new_ship.save()
                if pro.problem.type == 1:
                    new_Team.web += 1
                elif pro.problem.type == 2:
                    new_Team.misc += 1
                elif pro.problem.type == 3:
                    new_Team.pwn += 1
                elif pro.problem.type == 4:
                    new_Team.crypto += 1
                elif pro.problem.type == 5:
                    new_Team.reverse += 1
            new_Team.save()
    return redirect('/team/')


def teamJoin(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if user.team != None:
        return redirect('/team/')
    if models.user_application.objects.filter(user=user).exists():
        team = models.user_application.objects.get(user=user).team
        return HttpResponse("You are applying for team:'" + team.team_name + "'")
    if request.method == 'GET':
        team_id = request.GET.get('id')
        team = models.Team.objects.get(id=int(team_id))
        if team.member_num == 5:
            return HttpResponse('this team is full')
        application = models.user_application()
        application.team = team
        application.user = user
        application.save()
        return HttpResponse("Apply successfully.Please wait for leader's permission.")


def agree(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if user.team.leader != user.username:
        return redirect('/team/')
    if request.method == 'GET':
        applicant_name = request.GET.get('agree')
        applicant = models.User.objects.get(username=applicant_name)
        apply_team = user.team
        applicant.team = apply_team
        user.team.member_num += 1
        user.team.scores += applicant.scores
        user.team.save()
        applicant.save()
        user_pro_try = models.Answer_Ship.objects.filter(user=applicant).exists()
        if user_pro_try:
            user_pro_list = models.Answer_Ship.objects.filter(user=applicant)
            for user_pro in user_pro_list:
                exist = 0
                team_pro_try = models.Problem_Team_Ship.objects.filter(team=apply_team).exists()
                if team_pro_try:
                    team_pro_list = models.Problem_Team_Ship.objects.filter(team=apply_team)
                    for team_pro in team_pro_list:
                        if user_pro.problem.id == team_pro.problem.id:
                            exist = 1
                            break
                if exist == 1:
                    ship = models.Problem_Team_Ship.objects.get(team=apply_team, problem=user_pro.problem)
                    ship.answer_member_num += 1
                    ship.save()
                else:
                    new_ship = models.Problem_Team_Ship()
                    new_ship.team = apply_team
                    new_ship.problem = user_pro.problem
                    new_ship.save()
                    if user_pro.problem.type == 1:
                        apply_team.web += 1
                    elif user_pro.problem.type == 2:
                        apply_team.misc += 1
                    elif user_pro.problem.type == 3:
                        apply_team.pwn += 1
                    elif user_pro.problem.type == 4:
                        apply_team.crypto += 1
                    elif user_pro.problem.type == 5:
                        apply_team.reverse += 1
                    apply_team.answers += 1
                    apply_team.save()
        application = models.user_application.objects.get(user=applicant, team=apply_team)
        application.delete()
        if user.team.member_num == 5:
            application_list = models.user_application.objects.filter(team=user.team)
            for apply in application_list:
                apply.delete()
        return HttpResponse("operate successfully")


def deny(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if user.team.leader != user.username:
        return redirect('/team/')
    if request.method == 'GET':
        applicant_name = request.GET.get('deny')
        applicant = models.User.objects.get(username=applicant_name)
        application = models.user_application.objects.get(user=applicant, team=user.team)
        application.delete()
        return HttpResponse("operate successfully")


def rank(request):
    login_name = ''
    if request.session.get('id'):
        user = models.User.objects.get(id=request.session.get('id'))
        login_name = user.username
    if request.method == 'GET':
        type = request.GET.get('type')
        page = request.GET.get('page')
        rank_type = int(type)
        rank_page = int(page)
        front = rank_page - 1
        behind = rank_page + 1
        if front == 0:
            front = 1
        rank_list = []
        page1 = rank_page * 5 - 4
        page2 = rank_page * 5 - 3
        page3 = rank_page * 5 - 2
        page4 = rank_page * 5 - 1
        page5 = rank_page * 5 - 0
        if rank_type == 1:
            rank_list = models.User.objects.all()
            rank_pages_num = math.ceil(len(rank_list)/5)
            if rank_pages_num == 0:
                if rank_page != 1:
                    return redirect('../rank/?type=1&page=1')
            else:
                if rank_page <= 0 or rank_page > rank_pages_num:
                    return redirect('../rank/?type=1&page=1')
            if behind == rank_pages_num + 1:
                behind = rank_pages_num
            rank_pages_list = []
            for i in range(rank_pages_num):
                rank_pages_list.append(i+1)
            rank_list = models.User.objects.all()[(rank_page-1)*5:rank_page*5]
            return render(request, 'rank1.html', locals())
        elif rank_type == 2:
            rank_list = models.Team.objects.all()
            rank_pages_num = math.ceil(len(rank_list) / 5)
            if rank_pages_num == 0:
                if rank_page != 1:
                    return redirect('../rank/?type=2&page=1')
            else:
                if rank_page <= 0 or rank_page > rank_pages_num:
                    return redirect('../rank/?type=2&page=1')
            if behind == rank_pages_num + 1:
                behind = rank_pages_num
            rank_pages_list = []
            for i in range(rank_pages_num):
                rank_pages_list.append(i + 1)
            rank_list = models.Team.objects.all()[(rank_page - 1) * 5:rank_page * 5]
            return render(request, 'rank1.html', locals())


def problems(request, pro_type):
    login_name = ''
    if request.session.get('id'):
        user = models.User.objects.get(id=request.session.get('id'))
        login_name = user.username
    if pro_type == 'web':
        problem_list = models.Problem.objects.filter(type=1)
    elif pro_type == 'misc':
        problem_list = models.Problem.objects.filter(type=2)
    elif pro_type == 'pwn':
        problem_list = models.Problem.objects.filter(type=3)
    elif pro_type == 'crypto':
        problem_list = models.Problem.objects.filter(type=4)
    elif pro_type == 'reverse':
        problem_list = models.Problem.objects.filter(type=5)
    else:
        problem_list = models.Problem.objects.all()
    return render(request, 'problems.html', locals())


def team_name_rewrite(request):
    user = models.User.objects.get(id=request.session.get('id'))
    team = models.Team.objects.get(leader=user.username)
    if request.method == 'POST':
        newname = request.POST.get('newname')
        team.team_name = newname
        team.save()
    return redirect('/team/')


def team_motto_rewrite(request):
    user = models.User.objects.get(id=request.session.get('id'))
    team = models.Team.objects.get(leader=user.username)
    if request.method == 'POST':
        motto = request.POST.get('newmotto')
        team.motto = motto
        team.save()
    return redirect('/team/')


def dismiss(request):
    user = models.User.objects.get(id=request.session.get('id'))
    team = models.Team.objects.get(leader=user.username)
    member_list = models.User.objects.filter(team=team)
    pro_ship_list = models.Problem_Team_Ship.objects.filter(team=team)
    for member in member_list:
        member.team = None
    for pro_ship in pro_ship_list:
        pro_ship.delete()
    team.delete()
    return redirect('/')


def quit_team(request):
    user = models.User.objects.get(id=request.session.get('id'))
    user.team.scores -= user.scores
    user.team.member_num -= 1
    user_pro_list_try = models.Answer_Ship.objects.filter(user=user).exists()
    if user_pro_list_try:
        user_pro_list = models.Answer_Ship.objects.filter(user=user)
        for user_pro in user_pro_list:
            team_pro_ship = models.Problem_Team_Ship.objects.get(team=user.team, problem=user_pro.problem)
            team_pro_ship.answer_member_num -= 1
            if team_pro_ship.answer_member_num == 0:
                if user_pro.problem.type == 1:
                    user.team.web -= 1
                elif user_pro.problem.type == 2:
                    user.team.misc -= 1
                elif user_pro.problem.type == 3:
                    user.team.pwn -= 1
                elif user_pro.problem.type == 4:
                    user.team.crypto -= 1
                elif user_pro.problem.type == 5:
                    user.team.reverse -= 1
                team_pro_ship.delete()
                user.team.answers -= 1
                user.team.save()
    user.team.save()
    user.team = None
    user.save()
    return redirect('/')


def kick_out(request):
    if not request.session.get('id'):
        return redirect('/')
    user = models.User.objects.get(id=request.session.get('id'))
    if not user.team:
        return redirect('/')
    if not user.username == user.team.leader:
        return redirect('/team/')
    if request.method == 'GET':
        user_name = request.GET.get("kick")
        kicked_user = models.User.objects.get(username=user_name)

        kicked_user.team.scores -= user.scores
        kicked_user.team.member_num -= 1
        if models.Answer_Ship.objects.filter(user=kicked_user).exists():
            kicked_user_pro_list = models.Answer_Ship.objects.filter(user=user)
            for kicked_user_pro in kicked_user_pro_list:
                team_pro_ship = models.Problem_Team_Ship.objects.get(team=user.team, problem=kicked_user_pro.problem)
                team_pro_ship.answer_member_num -= 1
                if team_pro_ship.answer_member_num == 0:
                    if kicked_user_pro.problem.type == 1:
                        kicked_user.team.web -= 1
                    elif kicked_user_pro.problem.type == 2:
                        kicked_user.team.misc -= 1
                    elif kicked_user_pro.problem.type == 3:
                        kicked_user.team.pwn -= 1
                    elif kicked_user_pro.problem.type == 4:
                        kicked_user.team.crypto -= 1
                    elif kicked_user_pro.problem.type == 5:
                        kicked_user.team.reverse -= 1
                    team_pro_ship.delete()
                    kicked_user.team.answers -= 1
                    kicked_user.team.save()
        kicked_user.team.save()
        kicked_user.team = None
        kicked_user.save()
        return HttpResponse('kick out successfully')


def name_rewrite(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if request.method == 'POST':
        name = request.POST.get('newname')
        if models.User.objects.filter(username=name).exists():
            return HttpResponse('用户名存在')
        if user.team.leader == user.username:
            user.team.leader = name
            user.team.save()
        user.username = name
        user.save()
    return redirect('/info/?id=' + str(user.id))


def motto_rewrite(request):
    user = models.User.objects.get(id=request.session.get('id'))
    if request.method == 'POST':
        motto = request.POST.get('newmotto')
        user.motto = motto
        user.save()
    return redirect('/info/?id=' + str(user.id))


def problem(request):
    login_name = ''
    is_answered = 0
    if request.session.get('id'):
        user = models.User.objects.get(id=request.session.get('id'))
        login_name = user.username
    if request.method == 'GET':
        pro_id = request.GET.get('id')
        problem = models.Problem.objects.get(id=pro_id)
        if login_name:
            user = models.User.objects.get(id=request.session.get('id'))
            is_answered = models.Answer_Ship.objects.filter(user=user, problem=problem).exists()
            return render(request, 'Template_Prob.html', locals())
        return render(request, 'Template_Prob.html', locals())


def wp(request):
    login_name = ''
    if request.session.get('id'):
        login_name = models.User.objects.get(id=request.session.get('id')).username
    if request.method == 'GET':
        pro_id = request.GET.get('id')
        page = request.GET.get('page')
        pro_id = int(pro_id)
        page = int(page)
        wp_list = models.problem_solution.objects.filter(problem_id=pro_id)
        wp_num = len(wp_list)
        page_num = math.ceil(wp_num / 3)
        if page_num != 0:
            if page > page_num or page <= 0:
                return redirect('../wp_list/?id=' + str(pro_id) + '&page=1')
        else:
            if page != 1:
                return redirect('../wp_list/?id=' + str(pro_id) + '&page=1')
        wp_list = wp_list[(page-1)*3:page*3]
        is_agreed = []
        for wp in wp_list:
            if request.session.get('id'):
                user = models.User.objects.get(id=request.session.get('id'))
                is_agreed.append(models.user_wp.objects.filter(user=user, wp=wp).exists())
            else:
                is_agreed.append(0)
        former = page - 1
        latest = page + 1
        if former == 0:
            former = 1
        if latest > page_num:
            if page_num == 0:
                latest = 1
            else:
                latest = page_num
        page_num_list = []
        for i in range(page_num):
            page_num_list.append(i + 1)
        number1 = page * 3 - 2
        number2 = page * 3 - 1
        number3 = page * 3
        return render(request, 'Template_WP.html', locals())


def pro_answer(request):
    user_id = request.session.get('id')
    if user_id == None:
        return redirect('/problems/')
    user = models.User.objects.get(id=user_id)
    message = 0
    if request.method == 'GET':
        pro_id = request.GET.get('id')
        problem = models.Problem.objects.get(id=pro_id)
        answer = request.GET.get('flag')
        if answer == problem.answer:
            problem.answered_user_number += 1
            problem.save()
            message = 1
            exist = models.Answer_Ship.objects.filter(user=user, problem=problem).exists()
            if exist:
                pass
            else:
                new_ship = models.Answer_Ship()
                new_ship.user = user
                new_ship.problem = problem
                new_ship.save()
                user.answers += 1
                user.scores += problem.scores
                if problem.type == 1:
                    user.web += 1
                elif problem.type == 2:
                    user.misc += 1
                elif problem.type == 3:
                    user.pwn += 1
                elif problem.type == 4:
                    user.crypto += 1
                elif problem.type == 5:
                    user.reverse += 1
                user.save()
                if user.team:
                    user.team.scores += problem.scores
                    t_exist = models.Problem_Team_Ship.objects.filter(team=user.team, problem=problem).exists()
                    if t_exist:
                        t_ship = models.Problem_Team_Ship.objects.get(team=user.team, problem=problem)
                        t_ship.answer_member_num += 1
                    else:
                        t_ship = models.Problem_Team_Ship()
                        t_ship.team = user.team
                        t_ship.problem = problem
                        if problem.type == 1:
                            user.team.web += 1
                        elif problem.type == 2:
                            user.team.misc += 1
                        elif problem.type == 3:
                            user.team.pwn += 1
                        elif problem.type == 4:
                            user.team.crypto += 1
                        elif problem.type == 5:
                            user.team.reverse += 1
                        user.team.answers += 1
                    user.team.save()
                    t_ship.save()
    if message:
        return HttpResponse('You are right!')
    else:
        return HttpResponse('You are wrong!')


def wp_upload(request, pro_id):
    if not request.session.get('id'):
        return HttpResponse('please log in first')
    user = models.User.objects.get(id=request.session.get('id'))
    problem = models.Problem.objects.get(id=int(pro_id))
    message = ''
    if not models.Answer_Ship.objects.filter(user=user, problem=problem).exists():
        return HttpResponse('please finish this problem first')
    if request.method == 'POST':
        file = request.FILES.get("file", None)
        if not file:
            message = "no files for upload!"
            return render(request, 'wp_upload.html', locals())
        if not file.name.endswith("pdf"):
            message = "only PDF is accepted!"
            return render(request, 'wp_upload.html', locals())
        file.name = user.username + "-" + problem.title + '.pdf'
        title = request.POST.get("title")
        introduction = request.POST.get("introduction")
        if os.path.exists(file.name):
            os.remove(file.name)
        destination = open(os.path.join("wp", file.name), 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        exist = models.Answer_Ship.objects.filter(user=user, problem=problem).exists()
        if exist:
            relationship = models.Answer_Ship.objects.get(user=user, problem=problem)
            if models.problem_solution.objects.filter(relationship=relationship).exists():
                solution = models.problem_solution.objects.get(relationship=relationship)
                solution.address = file.name
                solution.introduction = introduction
                solution.title = title
                solution.save()
            else:
                solution = models.problem_solution()
                solution.problem_id = pro_id
                solution.relationship = relationship
                solution.address = file.name
                solution.introduction = introduction
                solution.title = title
                solution.save()
        else:
            message = 'Please finish this problem first'
            return render(request, 'wp_upload.html', locals())
        message = 'upload successfully'
        return render(request, 'wp_upload.html', locals())
    return render(request, 'wp_upload.html', locals())


def wp_download(request, wp_id):
    ship = models.problem_solution.objects.get(id=wp_id)
    name = ship.address
    try:
        response = StreamingHttpResponse(open('F:/untitled1/wp/'+name, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename('F:/untitled1/wp/'+name)
        return response
    except Exception:
        raise Http404


def agree_wp(request):
    if not request.session.get('id'):
        return redirect('/')
    user = models.User.objects.get(id=request.session.get('id'))
    if request.method == 'GET':
        wp_id = request.GET.get('id')
        wp = models.problem_solution.objects.get(id=wp_id)
        if models.user_wp.objects.filter(user=user, wp=wp).exists():
            Agree = models.user_wp.objects.get(user=user, wp=wp)
            Agree.delete()
            wp.good -= 1
            wp.save()
            return HttpResponse('取消点赞')
        else:
            new_Agree = models.user_wp()
            new_Agree.user = user
            new_Agree.wp = wp
            new_Agree.save()
            wp.good += 1
            wp.save()
            return HttpResponse('点赞成功')


def pro_source_download(request, name):
    try:
        response = StreamingHttpResponse(open('F:/untitled1/pro_source/'+name, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename('F:/pro_source/wp/'+name)
        return response
    except Exception:
        raise Http404


def web1(request):
    if request.method == 'POST':
        flag = 'space{1jkustni7sh}'
        return render(request, 'DisabledButton.html', locals())
    return render(request, 'DisabledButton.html')


def web2(request):
    return render(request, 'SimpleJS.html')

