from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    else:
        form = AuthenticationForm()
    
    return render(request, 'nguoi_dung/login.html', {'form': form})

