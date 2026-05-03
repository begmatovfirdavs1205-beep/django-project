from django.contrib import admin

from .models import QuizQuestion, QuizResult, Subject, UserProfile


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'prompt', 'correct_option')
    list_filter = ('subject',)
    search_fields = ('prompt',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'score_percent', 'correct_answers', 'total_questions', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('user__username',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_quizzes', 'average_score', 'best_score')
    search_fields = ('user__username',)
