from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import QuizQuestion, QuizResult, Subject


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')


def ensure_demo_data():
    if Subject.objects.exists():
        return

    subjects = {
        'Математика': {
            'description': 'Алгебра, геометрия и логическое мышление.',
            'questions': [
                ('Сколько будет 7 * 8?', '54', '56', '58', '64', 'B'),
                ('Корень из 144 равен?', '10', '11', '12', '13', 'C'),
                ('Решите: 2x + 6 = 14', 'x = 2', 'x = 3', 'x = 4', 'x = 5', 'C'),
            ],
        },
        'История': {
            'description': 'Ключевые события и даты мировой истории.',
            'questions': [
                ('В каком году началась Вторая мировая война?', '1938', '1939', '1940', '1941', 'B'),
                ('Кто построил Великую китайскую стену?', 'Династия Цинь', 'Династия Тан', 'Монголы', 'Римляне', 'A'),
                ('Где была подписана Декларация независимости США?', 'Вашингтон', 'Нью-Йорк', 'Филадельфия', 'Бостон', 'C'),
            ],
        },
        'Информатика': {
            'description': 'Основы алгоритмов, логики и программирования.',
            'questions': [
                ('Что означает HTML?', 'HyperText Markup Language', 'High Transfer Machine Language', 'Home Tool Markup Language', 'Hyperlink Text Machine Logic', 'A'),
                ('Какой язык чаще всего используется в Data Science?', 'Python', 'HTML', 'CSS', 'SQL', 'A'),
                ('Что делает цикл for?', 'Удаляет файлы', 'Повторяет блок кода', 'Создает сервер', 'Шифрует данные', 'B'),
            ],
        },
    }

    for name, data in subjects.items():
        subject = Subject.objects.create(name=name, description=data['description'])
        for question in data['questions']:
            QuizQuestion.objects.create(
                subject=subject,
                prompt=question[0],
                option_a=question[1],
                option_b=question[2],
                option_c=question[3],
                option_d=question[4],
                correct_option=question[5],
            )


def index(request):
    ensure_demo_data()
    return render(request, 'index.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        context['error'] = 'Неверный логин или пароль.'

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    ensure_demo_data()

    subjects = Subject.objects.all()
    results = request.user.quiz_results.select_related('subject')[:8]

    profile = request.user.profile
    profile.recalculate()

    subject_stats = request.user.quiz_results.values('subject__name').annotate(
        avg_score=Avg('score_percent'),
        best_score=Max('score_percent'),
    )

    return render(
        request,
        'dashboard.html',
        {
            'subjects': subjects,
            'results': results,
            'profile': profile,
            'subject_stats': subject_stats,
        },
    )


@login_required
def quiz_view(request, subject_id):
    ensure_demo_data()

    subject = get_object_or_404(Subject, id=subject_id)
    questions = subject.questions.all()
    return render(
        request,
        'quiz.html',
        {
            'subject': subject,
            'questions': questions,
        },
    )


@login_required
@require_POST
def submit_quiz_api(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    questions = list(subject.questions.all())

    try:
        import json

        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Некорректные данные запроса.'}, status=400)

    answers = data.get('answers', {})
    if not isinstance(answers, dict):
        return JsonResponse({'error': 'Поле answers должно быть объектом.'}, status=400)

    correct = 0
    for q in questions:
        selected = str(answers.get(str(q.id), '')).upper()
        if selected == q.correct_option:
            correct += 1

    total = len(questions)
    score = round((correct / total) * 100, 1) if total else 0

    QuizResult.objects.create(
        user=request.user,
        subject=subject,
        correct_answers=correct,
        total_questions=total,
        score_percent=score,
    )
    request.user.profile.recalculate()

    return JsonResponse(
        {
            'message': 'Тест успешно проверен!',
            'correct_answers': correct,
            'total_questions': total,
            'score_percent': score,
        }
    )


@login_required
@require_POST
def ai_helper_api(request):
    try:
        import json

        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Некорректные данные запроса.'}, status=400)

    question = data.get('question', '').strip()
    if not question:
        return JsonResponse({'error': 'Введите вопрос для AI-помощника.'}, status=400)

    # Простая симуляция AI-ответа на основе ключевых слов.
    q = question.lower()
    if 'мат' in q or 'алгеб' in q or 'геометр' in q:
        answer = 'Разбей задачу на шаги: формула -> подстановка -> вычисление -> проверка ответа.'
    elif 'истор' in q or 'дата' in q or 'войн' in q:
        answer = 'Используй метод таймлайна: событие, причина, итог и 1 ключевая дата для запоминания.'
    elif 'python' in q or 'код' in q or 'алгоритм' in q:
        answer = 'Начни с псевдокода, затем реализуй минимальный рабочий пример и добавь проверки.'
    else:
        answer = 'Сфокусируйся на цели темы, выдели 3 ключевые идеи и закрепи их мини-тестом из 5 вопросов.'

    return JsonResponse({'question': question, 'answer': answer})


@login_required
@require_GET
def subjects_api(request):
    subjects = list(Subject.objects.values('id', 'name', 'description'))
    return JsonResponse({'subjects': subjects})


@login_required
@require_GET
def stats_api(request):
    results = request.user.quiz_results.select_related('subject')
    payload = [
        {
            'subject': r.subject.name,
            'score_percent': r.score_percent,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for r in results[:20]
    ]
    return JsonResponse({'results': payload})
