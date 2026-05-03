function getCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (tokenMeta) {
        return tokenMeta.getAttribute('content');
    }
    const cookie = document.cookie
        .split(';')
        .map((c) => c.trim())
        .find((c) => c.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

async function askAIHelper() {
    const input = document.getElementById('ai-question');
    const output = document.getElementById('ai-answer');
    if (!input || !output) return;

    const question = input.value.trim();
    if (!question) {
        output.textContent = 'Введите вопрос для AI-помощника.';
        return;
    }

    output.textContent = 'AI думает...';

    const response = await fetch('/api/ai-helper/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ question }),
    });

    const data = await response.json();
    output.textContent = data.answer || data.error || 'Ошибка сервера.';
}

async function submitQuiz(event) {
    event.preventDefault();

    const form = document.getElementById('quiz-form');
    const root = document.getElementById('quiz-root');
    const resultBox = document.getElementById('quiz-result');
    if (!form || !root || !resultBox) return;

    const answers = {};
    const radios = form.querySelectorAll('input[type="radio"]:checked');
    radios.forEach((radio) => {
        const questionId = radio.name.replace('q_', '');
        answers[questionId] = radio.value;
    });

    resultBox.style.display = 'block';
    resultBox.classList.remove('result-success');
    resultBox.textContent = 'Проверяем ответы...';

    const response = await fetch(root.dataset.submitUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ answers }),
    });

    const data = await response.json();
    if (!response.ok) {
        resultBox.textContent = data.error || 'Не удалось проверить тест.';
        return;
    }

    resultBox.classList.add('result-success');
    resultBox.innerHTML = `
        <h3>Результат: ${data.score_percent}%</h3>
        <p>Верных ответов: ${data.correct_answers} из ${data.total_questions}</p>
        <p>${data.message}</p>
    `;
}

function initAnimations() {
    const cards = document.querySelectorAll('.card, .subject-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 60 * index);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const aiBtn = document.getElementById('ai-ask-btn');
    if (aiBtn) {
        aiBtn.addEventListener('click', askAIHelper);
    }

    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', submitQuiz);
    }

    initAnimations();
});
