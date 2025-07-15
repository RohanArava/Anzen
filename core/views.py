from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import UserProfile

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            login(request, user)
            return redirect('home')  # Change to your app's landing page
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

def home_view(request):
    return render(request, 'core/home.html')
