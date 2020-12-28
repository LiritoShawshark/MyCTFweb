from django.db import models


class Team(models.Model):
    team_name = models.CharField(max_length=10, unique=True)
    leader = models.CharField(max_length=10)
    member_num = models.IntegerField(default=1)
    answers = models.IntegerField(default=0)
    scores = models.IntegerField(default=0)
    web = models.IntegerField(default=0)
    misc = models.IntegerField(default=0)
    pwn = models.IntegerField(default=0)
    crypto = models.IntegerField(default=0)
    reverse = models.IntegerField(default=0)
    motto = models.CharField(max_length=255, default='To be or not to be is a problem')
    
    def __str__(self):
        return self.team_name
        
    class Meta:
        ordering = ['-scores']
        verbose_name = '队伍'
        verbose_name_plural = '队伍'


class User(models.Model):
    username = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=10)
    stu_id = models.CharField(max_length=10, unique=True)
    scores = models.IntegerField(default=0)
    answers = models.IntegerField(default=0)
    web = models.IntegerField(default=0)
    misc = models.IntegerField(default=0)
    pwn = models.IntegerField(default=0)
    crypto = models.IntegerField(default=0)
    reverse = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    c_time = models.DateTimeField(auto_now_add=True)
    motto = models.CharField(max_length=255, default="I'm lazy so here's no motto.")

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-scores']
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Problem(models.Model):
    PROBLEM_TYPE = (
        (1, 'web problem'),
        (2, 'misc problem'),
        (3, 'pwn problem'),
        (4, 'crypto problem'),
        (5, 'reverse problem'),
    )
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=255)
    type = models.IntegerField(choices=PROBLEM_TYPE)
    answer = models.CharField(max_length=255)
    uploader = models.CharField(max_length=20, default='original')
    scores = models.IntegerField(default=0)
    address = models.CharField(max_length=255, default='')
    answered_user_number = models.IntegerField(default=0)
    answered_user = models.ManyToManyField(User, through='Answer_Ship')
    answered_team = models.ManyToManyField(Team, through='Problem_Team_Ship')

    def __str__(self):
        return str(self.id)+':'+self.title

    class Meta:
        ordering = ['id']
        verbose_name = '题目'
        verbose_name_plural = '题目'


class Answer_Ship(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING)
    Answered_Time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username+'-'+str(self.problem.id)+':'+self.problem.title


class Problem_Team_Ship(models.Model):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING)
    answer_member_num = models.IntegerField(default=1)

    def __str__(self):
        return self.team.team_name+'-'+str(self.problem.id)+':'+self.problem.title


class problem_solution(models.Model):
    relationship = models.ForeignKey(Answer_Ship, on_delete=models.DO_NOTHING)
    problem_id = models.IntegerField(default=0)
    address = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    introduction = models.CharField(max_length=255)
    check = models.BooleanField(default=False)
    good = models.IntegerField(default=0)

    def __str__(self):
        return self.relationship.user.username + "'s solution for " + self.relationship.problem.title


class user_wp(models.Model):
    wp = models.ForeignKey(problem_solution, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ag_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' agree with ' + self.wp.relationship.user.username + "'s wp."


class user_application(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    apply_time = models.TimeField(auto_now_add=True)

    class Meta:
        ordering = ['apply_time']

    def __str__(self):
        return self.user.username + "'s application for " + self.team.team_name


class captcha(models.Model):
    address = models.CharField(max_length=50)
    answer = models.CharField(max_length=50)