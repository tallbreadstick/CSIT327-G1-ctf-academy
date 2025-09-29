from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def register(request):
    """Registration page -> after successful registration redirect to login."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")   # uses the named 'login' route (django.contrib.auth)
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/registration.html", {"form": form})


def login_view(request):
    """Optional custom login view — safe to have, but project-level auth URLs may be used instead."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")  # send to dashboard which shows admin/general appropriately
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "registration/login.html")


def logout_view(request):
    auth_logout(request)
    return render(request, "registration/login.html")



@login_required
def dashboard(request):
    """
    Single entrypoint for /dashboard/
    Shows admin.html if user.is_superuser, otherwise general.html.
    """
    if request.user.is_superuser:
        return render(request, "dashboard/admin.html")
    return render(request, "dashboard/general.html")


@login_required
def general(request):
    """Direct route for /dashboard/general/"""
    return render(request, "dashboard/general.html")


@login_required
def admin_dashboard(request):
    """Direct route for /dashboard/admin-dashboard/"""
    return render(request, "dashboard/admin.html")
