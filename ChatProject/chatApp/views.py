from django.shortcuts import render, redirect
from django.contrib import messages
from .Login import criar_usuario, autenticar_usuario

# Registro usando MySQL e bcrypt
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from .Login import criar_usuario, autenticar_usuario

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not username or not password or not confirm:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('register')

        if password != confirm:
            messages.error(request, "As senhas não coincidem.")
            return redirect('register')

        if not criar_usuario(username, password):
            messages.error(request, "Usuário já existe.")
            return redirect('register')

        messages.success(request, "Usuário registrado com sucesso. Faça login.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if autenticar_usuario(username, password):
            # Aqui você precisa logar o usuário manualmente no Django
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Cria um "espelho" no sistema do Django apenas para login funcionar
                user = User.objects.create_user(username=username, password=password)

            login(request, user)
            request.session['username'] = username
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Credenciais inválidas'})

    return render(request, 'login.html')


# Verifica se usuário está logado usando session
def index(request):
    if 'username' not in request.session:
        return redirect('login')
    return render(request, 'index.html', {'username': request.session['username']})

def room(request, room_name):
    if 'username' not in request.session:
        return redirect('login')
    return render(request, 'room.html', {
        'room_name': room_name,
        'username': request.session['username']
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')
