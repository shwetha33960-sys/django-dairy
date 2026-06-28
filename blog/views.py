from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm
from .models import DiaryPage, TodoItem


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url)
    else:
        form = LoginForm(request)

    return render(request, 'blog/login.html', {'form': form, 'next': next_url})


def home(request):
    if not request.user.is_authenticated:
        login_url = reverse('login')
        return redirect(f"{login_url}?next={request.path}")

    pages = DiaryPage.objects.none()
    selected_date = None
    diary_entry = None
    written_date = None
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        written_date = request.POST.get('written_date')
        search_date = request.POST.get('search_date')
        page_content = request.POST.get('page', '')
        entry_id = request.POST.get('entry_id')

        if action == 'save':
            if written_date and page_content.strip():
                DiaryPage.objects.create(
                    owner=request.user,
                    search_date=search_date or written_date,
                    written_date=written_date,
                    page=page_content,
                )
                return redirect('home')
            error = 'Please add a written date and some page content before saving.'

        elif action == 'search':
            if search_date:
                pages = DiaryPage.objects.filter(owner=request.user, search_date=search_date)
                diary_entry = pages.order_by('-created_at').first()
                selected_date = search_date

        elif action == 'delete' and entry_id:
            DiaryPage.objects.filter(pk=entry_id, owner=request.user).delete()
            return redirect('home')

    return render(request, 'blog/home.html', {
        'user': request.user,
        'pages': pages,
        'selected_date': selected_date,
        'diary_entry': diary_entry,
        'written_date': written_date,
        'error': error,
    })


def delete_page(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        DiaryPage.objects.filter(pk=pk, owner=request.user).delete()
    return redirect('home')


def side_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Handle delete action
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            entry_id = request.POST.get('entry_id')
            if entry_id:
                DiaryPage.objects.filter(pk=entry_id, owner=request.user).delete()
            return redirect('side_page')

    # Handle date search filter
    search_date = request.GET.get('search_date', '')
    entries = DiaryPage.objects.filter(owner=request.user).order_by('-written_date', '-created_at')

    if search_date:
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(search_date, '%Y-%m-%d').date()
            entries = entries.filter(
                models.Q(written_date=parsed_date) | models.Q(search_date=parsed_date)
            )
        except ValueError:
            pass

    grouped = []
    seen_dates = set()
    entry_ids_by_date = {}

    for entry in entries:
        date_value = entry.written_date or entry.search_date
        if not date_value:
            continue
        date_key = date_value.strftime('%Y-%m-%d')
        if date_key not in seen_dates:
            grouped.append({
                'date': date_value.strftime('%b %d, %Y'),
                'key': date_key,
                'content': entry.page or ''
            })
            seen_dates.add(date_key)
            entry_ids_by_date[date_key] = [entry.pk]
        else:
            for group in grouped:
                if group['key'] == date_key:
                    group['content'] += '\n\n' + (entry.page or '')
                    break
            entry_ids_by_date[date_key].append(entry.pk)

    # Attach entry IDs to each group for delete functionality
    for group in grouped:
        group['entry_ids'] = entry_ids_by_date.get(group['key'], [])

    return render(request, 'blog/side_page.html', {
        'pages': grouped,
        'search_date': search_date,
    })


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'blog/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def todo_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            title = request.POST.get('title', '').strip()
            if title:
                TodoItem.objects.create(owner=request.user, title=title)
            return redirect('todo_page')

        elif action == 'toggle':
            item_id = request.POST.get('item_id')
            if item_id:
                try:
                    item = TodoItem.objects.get(pk=item_id, owner=request.user)
                    item.completed = not item.completed
                    item.save()
                except TodoItem.DoesNotExist:
                    pass
            return redirect('todo_page')

        elif action == 'delete':
            item_id = request.POST.get('item_id')
            if item_id:
                TodoItem.objects.filter(pk=item_id, owner=request.user).delete()
            return redirect('todo_page')

    todos = TodoItem.objects.filter(owner=request.user)
    total = todos.count()
    done = todos.filter(completed=True).count()
    active = total - done

    return render(request, 'blog/todo.html', {
        'todos': todos,
        'total': total,
        'done': done,
        'active': active,
    })
