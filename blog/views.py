from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm


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

    return render(request, 'blog/home.html', {'user': request.user})


def logout_view(request):
    logout(request)
    return redirect('login')
