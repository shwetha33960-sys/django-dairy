from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm
from .models import DiaryPage


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = LoginForm(request)

    return render(request, 'blog/login.html', {'form': form})


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

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
                    search_date=search_date or written_date,
                    written_date=written_date,
                    page=page_content,
                )
                return redirect('home')
            error = 'Please add a written date and some page content before saving.'

        elif action == 'search':
            if search_date:
                pages = DiaryPage.objects.filter(search_date=search_date)
                diary_entry = pages.order_by('-created_at').first()
                selected_date = search_date

        elif action == 'delete' and entry_id:
            DiaryPage.objects.filter(pk=entry_id).delete()
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
    if request.method == 'POST':
        DiaryPage.objects.filter(pk=pk).delete()
    return redirect('home')


def side_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    entries = DiaryPage.objects.order_by('-written_date', '-created_at')
    grouped = []
    seen_dates = set()

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
        else:
            for group in grouped:
                if group['key'] == date_key:
                    group['content'] += '\n\n' + (entry.page or '')
                    break

    return render(request, 'blog/side_page.html', {
        'pages': grouped,
    })


def logout_view(request):
    logout(request)
    return redirect('login')
