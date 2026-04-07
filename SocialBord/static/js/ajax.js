// Функция для получения CSRF-токена из cookies
function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/)
    return match ? decodeURIComponent(match[1]) : null
}

// Функция переключения лайка на посте
function toggleLike(postId) {
    const likeButton = document.querySelector(`.btn-like[data-post-id="${postId}"]`)
    const heartIcon = likeButton.querySelector('i')
    const likeCountSpan = likeButton.querySelector('.like-count')
    // Обновляем счётчик в мобильной версии
    const mobileCountSpan = document.querySelector(`.likes-count[data-post-id="${postId}"]`)

    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: postId })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok')
        return response.json()
    })
    .then(data => {
        // Обновляем оба счётчика
        if (likeCountSpan) likeCountSpan.textContent = data.likes_count
        if (mobileCountSpan) mobileCountSpan.textContent = `${data.likes_count} ${data.likes_count === 1 ? 'лайк' : 'лайков'}`

        // Обновляем иконку
        if (data.liked) {
            heartIcon.classList.remove('bi-heart')
            heartIcon.classList.add('bi-heart-fill', 'text-danger')
        } else {
            heartIcon.classList.remove('bi-heart-fill', 'text-danger')
            heartIcon.classList.add('bi-heart')
        }
    })
    .catch(error => {
        console.error('Ошибка при обработке лайка:', error)
        alert('Произошла ошибка при постановке лайка. Попробуйте ещё раз.')
    })
}

// Инициализация обработчиков кликов для всех кнопок лайков на странице
document.addEventListener('DOMContentLoaded', () => {
    // Делегирование событий для динамически добавляемых кнопок
    document.body.addEventListener('click', function(event) {
        const target = event.target.closest('.btn-like')
        if (target) {
            event.preventDefault()
            const postId = target.dataset.postId
            toggleLike(postId)
        }
    })

    // Дополнительно: обновляем состояние кнопок при загрузке страницы
    document.querySelectorAll('.btn-like').forEach(button => {
        const postId = button.dataset.postId
        // Здесь можно добавить логику для установки начального состояния кнопки
        // Например, если в шаблоне передаётся has_liked
    })
})

// Функция для обновления состояния кнопки лайка (опционально)
function updateLikeButtonState(postId, isLiked) {
    const button = document.querySelector(`.btn-like[data-post-id="${postId}"]`)
    if (!button) return

    const icon = button.querySelector('i')

    if (isLiked) {
        icon.classList.remove('bi-heart')
        icon.classList.add('bi-heart-fill', 'text-danger')
    } else {
        icon.classList.remove('bi-heart-fill', 'text-danger')
        icon.classList.add('bi-heart')
    }
}

function confirmDelete(postId) {
    if (confirm("Вы уверены, что хотите удалить этот пост?")) {
        const csrftoken = getCSRFToken();

        fetch(`/post/${postId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${encodeURIComponent(csrftoken)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const postCard = document.querySelector(`[data-post-id="${postId}"]`);
                if (postCard) {
                    postCard.remove();
            }
            alert("Пост успешно удалён");
        } else {
            alert(data.error || "Произошла ошибка при удалении поста");
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert("Произошла сетевая ошибка. Проверьте подключение.");
    });
}
}

function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/)
    return match ? decodeURIComponent(match[1]) : null;
}


function handleCommentSubmit(event, postId) {
    event.preventDefault()
    const form = event.target
    const textarea = form.querySelector('textarea[name="text"]')
    const text = textarea.value.trim()

    if (!text) {
        alert('Текст комментария не может быть пустым')
        return
    }

    fetch(`/social/post/${postId}/add_comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `text=${encodeURIComponent(text)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addCommentToUI(data.comment, postId)
            textarea.value = ''
            updateCommentsCount(postId, 1) // +1 при добавлении
        } else {
            alert(data.error || 'Ошибка при добавлении комментария')
        }
    })
    .catch(error => {
        console.error('Ошибка:', error)
        alert('Произошла ошибка при отправке комментария')
    })
}

function addCommentToUI(commentData, postId) {
    const commentsContainer = document.querySelector(`[data-post-id="${postId}"] .comments`)
    if (!commentsContainer) return

    const commentHTML = `
        <div class="comment mb-2 p-2 bg-light rounded" data-comment-id="${commentData.id}">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${commentData.author}</strong>
            ${commentData.can_delete ? '<span class="badge bg-secondary ms-2">Вы</span>' : ''}
                </div>
                <small class="text-muted">только что</small>
            </div>
            <p class="mb-1">${commentData.text}</p>
            ${commentData.can_delete ? `
                <div class="text-end">
                    <button class="btn btn-sm btn-outline-danger"
            onclick="confirmDeleteComment(${commentData.id}, ${postId})">
                Удалить
            </button>
        </div>` : ''}
        </div>
    `

    commentsContainer.insertAdjacentHTML('afterbegin', commentHTML)
}

function confirmDeleteComment(commentId, postId) {
    if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
        fetch(`/social/comment/${commentId}/delete/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`)
                if (commentElement) commentElement.remove()
                                updateCommentsCount(postId, -1) // -1 при удалении
            } else {
                alert(data.error || 'Ошибка при удалении комментария')
            }
        })
        .catch(error => {
            console.error('Ошибка при удалении комментария:', error)
            alert('Произошла ошибка при удалении комментария')
        })
    }
}

function updateCommentsCount(postId, change = 1) {
    const countElement = document.querySelector(`[data-post-id="${postId}"] .comments h6`)
    if (!countElement) return

    const match = countElement.textContent.match(/\((\d+)\)/)
    if (match) {
        const currentCount = parseInt(match[1], 10)
        const newCount = Math.max(0, currentCount + change)
        countElement.textContent = countElement.textContent.replace(/\(\d+\)/, `(${newCount})`)
    }
}
