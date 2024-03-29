from django.shortcuts import redirect, render
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from users.forms import SignUpForm, UserLoginForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
from django.conf import settings  
from django.core.mail import send_mail  

#ajax validation
# from jsonview.decorators import json_view
# from django.template.context_processors import csrf
#Create your views here.
@login_required(login_url='login/')

def home(request):
    return render(request, "user_information.html")



#@json_view 
def register(request):
    context = {}

    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            
            try:
                email = request.POST.get('email')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                phone = request.POST.get('phone')
                password = request.POST.get('password1')
                auth_token = str(uuid.uuid4())
                profile_obj = UserProfile.objects.create(email = email, first_name = first_name, last_name = last_name, phone = phone, auth_token = auth_token )
                profile_obj.set_password(password)
                profile_obj.save()
                print(auth_token)
                sendMailAfterRagistration(email, auth_token)   
                return redirect("/send_mail")      

            except Exception as e:
                print(e)
        context['register_form']=form

    else:
        form=SignUpForm()
        context['register_form']=form
    
    return render(request, 'register.html', context)

def sendMailAfterRagistration(email, token):
    subject = "Your account need to be verified"
    message = f'Hi! click the link to verify your account http://127.0.0.1:8000/verified/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def verifiedView(request, auth_token):
    try:
        profile_obj = UserProfile.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('login')
        else:
            return redirect('error')
    
    except Exception:
        print(Exception)

def errorPage(request):
    return  render(request , 'error.html')

    # form = SignUpForm(request.POST or None)
    # if form.is_valid():
    #     form.save()
    #     return {'succes' : True}

    # context = {}
    # context.update(csrf(request))
    # form_html = render_crispy_form(form, context=context)
    # return {'success':False, 'form_html': form_html}
    




def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user.is_verified == False:
            messages.success(request, 'Check your Email to verify your Account!!')
        else:
            login(request, user)
        if next:
            return redirect(next)
        return redirect('/')

    context = {
        'login_form': form,
    }
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect('login')

# class EditProfileView(UpdateView):
#     model = UserProfile
#     template_name = "registration/edit_profile.html"
#     success_url = reverse_lazy('user-info')
#     fields = ['first_name','last_name','phone']

def EditProfile(request):
    context={}
    check = UserProfile.objects.filter(id=request.user.id)
    if len(check)>0:
        data = UserProfile.objects.get(id=request.user.id)
        context["data"]=data
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone"]

        user = UserProfile.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.save()
        context["status"] = "Changes Saved"
        return redirect('/')
    return render(request, "edit_profile.html")


def sendEmailView(request):
    return render(request, "send_mail.html")




