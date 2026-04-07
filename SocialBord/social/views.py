from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment, Subscription
from .forms import PostForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST



def home(request):
    posts = Post.objects.select_related('author').prefetch_related(
        'likes', 'comments'
    ).order_by('-created_at')

    paginator = Paginator(posts, 10)  # 10 постов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Добавляем информацию о лайках для текущего пользователя
    for post in page_obj:
        if request.user.is_authenticated:
            post.has_liked = post.likes.filter(user=request.user).exists()
        else:
            post.has_liked = False

    return render(request, 'social/home.html', {
        'page_obj': page_obj
    })



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'social/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'social/login.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')



@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно создан!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'social/create_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Проверка, что пользователь — автор поста
    if post.author != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот пост")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('profile', request.user.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'social/edit_post.html', {'form': form, 'post': post})

@login_required
@require_POST
def delete_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)

        # Проверка прав: только автор может удалить пост
        if post.author != request.user:
            return JsonResponse({
                'success': False,
                'error': 'У вас нет прав на удаление этого поста'
            }, status=403)

        post.delete()
        return JsonResponse({'success': True})

    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Пост не найден'
        }, status=404)



@method_decorator(csrf_exempt, name='dispatch')
class LikePostView(View):
    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Не авторизован'}, status=401)

        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })



@login_required
def subscribe(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    Subscription.objects.get_or_create(subscriber=request.user, target=target_user)
    return redirect('profile', user_id=user_id)



@login_required
def unsubscribe(request, user_id):
    Subscription.objects.filter(subscriber=request.user, target_id=user_id).delete()
    return redirect('profile', user_id=user_id)



def profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            target=profile_user
        ).exists()

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_subscribed': is_subscribed,
        'subscription_count': profile_user.subscribers.count(),
        'subscribed_count': profile_user.subscriptions.count()
    }
    return render(request, 'social/profile.html', context)



def search(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(text__icontains=query).select_related('author')
        users = User.objects.filter(username__icontains=query)
    else:
        posts = Post.objects.none()
        users = User.objects.none()

    return render(request, 'social/search.html', {
        'query': query,
        'posts': posts,
        'users': users
    })

@login_required
@require_POST
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '').strip()

    if not text:
        return JsonResponse({'error': 'Текст комментария не может быть пустым'}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        text=text
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'author': comment.author.username,
            'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
            'can_delete': comment.author == request.user
        }
    })

@login_required
def delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id)

    # Проверяем, что пользователь — автор комментария или администратор
    if comment.author != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Нет прав на удаление'}, status=403)

    comment.delete()
    return JsonResponse({'success': True})

