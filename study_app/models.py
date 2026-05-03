from django.contrib.auth.models import User
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class QuizQuestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    prompt = models.CharField(max_length=255)
    option_a = models.CharField(max_length=150)
    option_b = models.CharField(max_length=150)
    option_c = models.CharField(max_length=150)
    option_d = models.CharField(max_length=150)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        return f'{self.subject.name}: {self.prompt[:45]}'


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='results')
    correct_answers = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    score_percent = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.subject.name} ({self.score_percent:.0f}%)'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_quizzes = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0)
    best_score = models.FloatField(default=0)

    def __str__(self):
        return f'Profile: {self.user.username}'

    def recalculate(self):
        # Пересчет статистики на основе всех попыток пользователя.
        results = self.user.quiz_results.all()
        self.total_quizzes = results.count()
        if self.total_quizzes:
            self.average_score = round(sum(r.score_percent for r in results) / self.total_quizzes, 1)
            self.best_score = round(max(r.score_percent for r in results), 1)
        else:
            self.average_score = 0
            self.best_score = 0
        self.save(update_fields=['total_quizzes', 'average_score', 'best_score'])
