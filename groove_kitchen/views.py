import os
from decouple import config
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .utils import *
from .models import Customer

# Create your views here.
def index(request):
    return render(request, 'index.html')

def registration(request):
    if request.method == 'POST':
        data = request.POST

        password = data.get('password')
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        email_address = data.get('email_address')


        if User.objects.filter(username=email_address).exists():
            return JsonResponse({"status": 'email_taken'})
        
        if len(password) < 8:
            return JsonResponse({"status": 'short_password'})
        
        if is_valid_email(email_address):

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=email_address,
                email=email_address,
                password=password,
            )
            user.set_password(password)
            user.is_staff=False
            user.save()
            return JsonResponse({"status": 200, "message": "Your account was successfully created!"})
        
        return JsonResponse({"status": 'invalid_email'})

    return render(request, 'registration/registration.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        data = request.POST

        username = data.get('email_address')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_staff:
                login(request, user)
                return redirect('home')
        return JsonResponse({"status": 404})
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login_view')

def about_us(request):
    return render(request, 'utils/about.html')

def password_form(request):
    if request.method == 'POST':
        email_address = request.POST.get('email_address')

        if not is_valid_email(email_address):
            return JsonResponse({"status": 'invalid_email', 'message': 'The email address you entered is invalid.'})
        
        customer = User.objects.filter(email=email_address).first()
        if customer:
            banner = os.path.join(settings.BASE_DIR, 'groove_kitchen', 'static', 'img', 'logo.PNG')
            validation_code = generate_validation_code()

            send_email(
                subject="Rest Password",
                body_text = '',
                body_html=f'''
                    <html>
                        <body>
                            <div style="text-align: center;">
                                <img src="{banner}" alt="logo" style="width: 100%; height: auto;"/>
                            </div>
                            <h4>Dear {customer.first_name} {customer.last_name},</h4>
                            <p> You have recently requsted to reset your password for your account {customer.email}.</p>
                            <p> To create a new password, please use the validation code below. </p>
                            <p style="margin-bottom: 10px;"> Validation Code: {validation_code}</p>
                            <p> If you didn't make this request, we suggest you log into your account and change your password.</p> 
                            <p> Kind regards,</p>
                            <p> Groove Kitchen</p>
                        </body>
                    </html>
                ''',
                from_email=config('DEFAULT_FROM_EMAIL'),
                to_email=email_address,
            )
            Customer.objects.create( user=customer, validation_code=validation_code )
            
            return JsonResponse({"status": 200, 'message': 'A password reset link has been sent to your email address.'})
        else:
            return JsonResponse({"status": 404, 'message': 'No user with that email address exists.'})
        
    return render(request, 'registration/password_form.html')

def password_done(request):
    if request.method == 'POST':
        validation_code = request.POST.get('validation_code')
       
        customer = Customer.objects.filter(validation_code=validation_code).first()
        if customer:
            customer.is_validated=True
            customer.save(update_fields=['is_validated'])
            return JsonResponse({"status": 200, 'message': 'Your account is successfully validated.', 'uid': customer.user.pk})
        else:
            return JsonResponse({"status": 404, 'message': 'The validation code you provided is invalid'})

    return render(request, 'registration/password_done.html')

def password_confirm(request, uidb64):
    if request.method == 'POST':
        print(request.POST)
        data = request.POST

        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({"status": 400, 'message': 'Passwords do not match'})

        if len(password) < 8:
            return JsonResponse({"status": 400, 'message': 'Password must be at least 8 characters long.'})
        try:
            customer = User.objects.get(pk=uidb64)
            customer.set_password(password)
            customer.save()
            return JsonResponse({"status": 200, 'message': 'Your password has been successfully updated.'})
        except ObjectDoesNotExist:
            return JsonResponse({"status": 404, 'message': 'User not found.'})

    return render(request, 'registration/password_confirm.html', {'uid': uidb64})

def password_complete(request):
    return render(request, 'registration/password_complete.html')

