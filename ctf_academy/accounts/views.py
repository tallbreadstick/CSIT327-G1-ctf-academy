from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Challenge, Category, UserProfile
from django.db.models import Sum, Q, Case, When, BooleanField

# --- ADDED IMPORTS FOR JWT AND API PROTECTION ---
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

# --- NEW VIEW TO GENERATE TOKEN WITH CUSTOM PAYLOAD ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- REMOVED THE OLD LoginView(APIView) CLASS ---
# The class above replaces it and handles token generation automatically.

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

# --- EXAMPLE OF A PROTECTED API ENDPOINT ---
# Any request to this view must include a valid JWT in the Authorization header.
# The library automatically rejects expired, tampered, or invalid tokens.
class ProtectedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is protected data, you are authenticated!'}
        return Response(content)

# ========== HTML PAGE VIEWS (Unchanged but with protection examples) ==========

def home_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard_page")
    return render(request, "accounts/home.html")

def about_page(request):
    return render(request, "accounts/about.html")

def register_page(request):
    # This view remains unchanged
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "accounts/register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "accounts/register.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "accounts/register.html")
        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "accounts/register.html")
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! You can log in now.")
        return redirect("login_page")
    return render(request, "accounts/register.html")

def login_page(request):
    # If user is already logged in, redirect them
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard_page")
        else:
            return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect without message
            if user.is_superuser:
                return redirect("admin_dashboard_page")
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "accounts/login.html")
    
    # GET request - just show the form
    return render(request, "accounts/login.html")

def logout_page(request):
    logout(request)
    return render(request, "accounts/logout.html")

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard_page(request):
    return render(request, "accounts/admin_dashboard.html")


@login_required
def profile_page(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        bio = request.POST.get("bio", "")
        base64_image = request.POST.get("base64_image")
        image_file = request.FILES.get("profile_image")  # from <input type="file">
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        profile_picture = request.FILES.get("profile_picture")  # Added this para sa profile picture

        changes_made = False

        # --- Update user info ---
        if (
            user.first_name != first_name
            or user.last_name != last_name
            or user.username != username
            or user.email != email
        ):
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            changes_made = True

        # --- Handle password change ---
        if current_password or new_password or confirm_password:
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
                return redirect("profile_page")

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect("profile_page")

            try:
                validate_password(new_password, user)
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                changes_made = True
            except ValidationError as e:
                for err in e.messages:
                    messages.error(request, err)
                return redirect("profile_page")

        # --- Update bio ---
        if bio != profile.bio:
            profile.bio = bio
            changes_made = True

        # --- Handle image update (base64 or file upload) ---
        import base64
        if base64_image:
            try:
                profile.set_base64_image(base64_image)
                changes_made = True
            except Exception as e:
                messages.error(request, f"Error saving base64 image: {e}")
                return redirect("profile_page")

        elif image_file:
            try:
                # Convert uploaded file → base64 → binary
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                profile.set_base64_image(encoded)
                changes_made = True
            except Exception as e:
                messages.error(request, f"Error saving image file: {e}")
                return redirect("profile_page")

        # --- Save changes ---
        if changes_made:
            user.save()
            profile.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.info(request, "No changes were made.")

        return redirect("profile_page")

    # --- Prepare data for rendering ---
    image_base64 = profile.get_base64_image()
    image_uri = f"data:image/jpeg;base64,{image_base64}" if image_base64 else None

    return render(request, "accounts/profile.html", {
        "user": user,
        "profile": profile,
        "image_uri": image_uri,
    })


@login_required
def challenges_page(request):
    user = request.user

    # --- Basic collections ---
    categories = Category.objects.all().order_by("name")
    qs = Challenge.objects.filter(is_active=True).select_related("category")

    # --- Filters from query string ---
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if difficulty:
        qs = qs.filter(difficulty=difficulty)

    if q:
        # simple search across title and description
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))

    qs = qs.order_by("id")

    # --- Stats: totals & points ---
    total_count = qs.count()
    points_total = qs.aggregate(total_points=Sum("points"))["total_points"] or 0

    completed_count = 0
    in_progress_count = 0
    points_earned = 0

    # Determine completion tracking strategy:
    # 1) If Challenge has an M2M 'completed_by', use it.
    # 2) Else try optional ChallengeProgress model (user, challenge, status).
    # 3) Otherwise show zeros (no tracking implemented).
    try:
        # Method 1: M2M completed_by
        if hasattr(Challenge, "completed_by"):
            completed_qs = qs.filter(completed_by=user)
            completed_count = completed_qs.count()
            points_earned = completed_qs.aggregate(points=Sum("points"))["points"] or 0

            # annotate per-challenge flags
            challenges = list(qs)
            completed_ids = set(completed_qs.values_list("id", flat=True))
            for ch in challenges:
                ch.is_completed = (ch.id in completed_ids)
                # tools_count placeholder: if topology contains 'tools' list, count it
                try:
                    ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0
                except Exception:
                    ch.tools_count = 0

        else:
            # Method 2: optional ChallengeProgress model
            from .models import ChallengeProgress  # may not exist
            progress_qs = ChallengeProgress.objects.filter(user=user, challenge__in=qs)

            completed_count = progress_qs.filter(status="completed").count()
            in_progress_count = progress_qs.filter(status="in_progress").count()
            points_earned = progress_qs.filter(status="completed").aggregate(points=Sum("challenge__points"))["points"] or 0

            challenges = list(qs)
            # map statuses by challenge id
            prog_map = {p.challenge_id: p.status for p in progress_qs}
            for ch in challenges:
                ch.is_completed = prog_map.get(ch.id) == "completed"
                ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0

    except Exception:
        # Fallback: no completion tracking available
        completed_count = 0
        in_progress_count = 0
        points_earned = 0
        challenges = list(qs)
        for ch in challenges:
            ch.is_completed = False
            try:
                ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0
            except Exception:
                ch.tools_count = 0

    stats = {
        "total": total_count,
        "points_total": points_total,
        "completed": completed_count,
        "in_progress": in_progress_count,
        "points_earned": points_earned,
        "categories_count": categories.count(),
    }

    context = {
        "categories": categories,
        "challenges": challenges,
        "DIFFICULTY_CHOICES": Challenge.Difficulty.choices,
        "selected_category": category_slug,
        "selected_difficulty": difficulty,
        "q": q,
        "stats": stats,
    }

    return render(request, "accounts/challenges.html", context)


@login_required
def leaderboards_page(request):
    return render(request, "accounts/leaderboards.html")

@login_required
def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    categories = Category.objects.all()

    return render(request, "accounts/challenge.html", {
        "challenge": challenge,
        "categories": categories,
    })