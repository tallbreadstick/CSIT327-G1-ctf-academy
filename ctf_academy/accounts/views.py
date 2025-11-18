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
from .models import Challenge, Category, UserProfile, Favorite
from django.db.models import Sum, Q, Case, When, IntegerField
from django.http import JsonResponse, HttpResponseBadRequest

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
    sort_by = request.GET.get("sort_by", "id")  # default sort by id

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if difficulty:
        qs = qs.filter(difficulty=difficulty)

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    # --- Sort mapping ---
    sort_options = {
        "id": "id",
        "points": "-points",
        "difficulty": "difficulty",  # you could also do "-difficulty" if needed
        "title": "title",
    }

    qs = qs.order_by(sort_options.get(sort_by, "id"))

    if sort_by == "difficulty":
        qs = qs.annotate(
            difficulty_order=Case(
                When(difficulty="easy", then=1),
                When(difficulty="medium", then=2),
                When(difficulty="hard", then=3),
                default=4,
                output_field=IntegerField()
            )
        ).order_by("difficulty_order")

    # --- Stats: totals & points ---
    total_count = qs.count()
    points_total = qs.aggregate(total_points=Sum("points"))["total_points"] or 0

    completed_count = 0
    in_progress_count = 0
    points_earned = 0

    try:
        if hasattr(Challenge, "completed_by"):
            completed_qs = qs.filter(completed_by=user)
            completed_count = completed_qs.count()
            points_earned = completed_qs.aggregate(points=Sum("points"))["points"] or 0

            challenges = list(qs)
            completed_ids = set(completed_qs.values_list("id", flat=True))
            for ch in challenges:
                ch.is_completed = (ch.id in completed_ids)
                try:
                    ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0
                except Exception:
                    ch.tools_count = 0
        else:
            from .models import ChallengeProgress
            progress_qs = ChallengeProgress.objects.filter(user=user, challenge__in=qs)
            completed_count = progress_qs.filter(status="completed").count()
            in_progress_count = progress_qs.filter(status="in_progress").count()
            points_earned = progress_qs.filter(status="completed").aggregate(points=Sum("challenge__points"))["points"] or 0

            challenges = list(qs)
            prog_map = {p.challenge_id: p.status for p in progress_qs}
            for ch in challenges:
                ch.is_completed = prog_map.get(ch.id) == "completed"
                ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0

    except Exception:
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

    # Favorites for current user
    try:
        favorite_ids = set(Favorite.objects.filter(user=user).values_list("challenge_id", flat=True))
    except Exception:
        favorite_ids = set()

    for ch in challenges:
        ch.is_favorite = ch.id in favorite_ids

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
        "selected_sort": sort_by,
        "q": q,
        "stats": stats,
    }

    return render(request, "accounts/challenges.html", context)


@login_required
def leaderboards_page(request):
    """
    Dynamic leaderboards backed by the existing database.
    There is no scoring system yet, so everyone is shown with 0 points.
    Ordering falls back to most recent users first so the page looks alive.
    """
    # Pull active users from DB (Supabase Postgres via Django settings)
    users_qs = User.objects.filter(is_active=True).order_by("-date_joined")

    leaders = []
    for u in users_qs:
        # Try to grab an inline image from profile if present
        image_uri = None
        try:
            if hasattr(u, "profile"):
                img_b64 = u.profile.get_base64_image()
                if img_b64:
                    image_uri = f"data:image/jpeg;base64,{img_b64}"
        except Exception:
            image_uri = None

        leaders.append({
            "id": u.id,
            "username": u.username,
            "points": 0,            # placeholder until scoring lands
            "challenges": 0,        # placeholder
            "streak": 0,            # placeholder
            "image_uri": image_uri,
            "date_joined": u.date_joined,
        })

    # Top 3 for podium, rest for table
    top = leaders[:3]
    rest = leaders[3:]
    start_rank = len(top) + 1

    # Current user's rank (1-based) if present in list
    current_user_rank = None
    for idx, row in enumerate(leaders, start=1):
        if row["id"] == request.user.id:
            current_user_rank = idx
            break

    context = {
        "top": top,
        "leaders": rest,
        "all_leaders": leaders,  # optional full list if template needs it
        "current_user_rank": current_user_rank,
        "start_rank": start_rank,
    }

    return render(request, "accounts/leaderboards.html", context)

@login_required
def challenge_detail(request, slug):
    # Fetch the challenge
    challenge = get_object_or_404(Challenge, slug=slug)
    categories = Category.objects.all()

    # Build initial content for the text editor
    initial_content = f"""Challenge: {challenge.title}
Category: {challenge.category.name if challenge.category else 'N/A'}
Points: {challenge.points}
Difficulty: {challenge.difficulty}

Description:
{challenge.description or 'No description provided.'}
"""
    # Mark safe for rendering inside <textarea>
    from django.utils.safestring import mark_safe
    initial_content = mark_safe(initial_content)

    # Favorite state for this challenge
    is_favorite = False
    if request.user.is_authenticated:
        try:
            is_favorite = Favorite.objects.filter(user=request.user, challenge=challenge).exists()
        except Exception:
            is_favorite = False

    return render(request, "accounts/challenge.html", {
        "challenge": challenge,
        "categories": categories,
        "initial_text_content": initial_content,
        "is_favorite": is_favorite,
    })


@login_required
def toggle_favorite(request, challenge_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    challenge = get_object_or_404(Challenge, id=challenge_id)
    try:
        fav, created = Favorite.objects.get_or_create(user=request.user, challenge=challenge)
        if created:
            return JsonResponse({"favorited": True})
        fav.delete()
        return JsonResponse({"favorited": False})
    except Exception:
        return JsonResponse({"error": "Unable to save favorite. Please try again."}, status=500)


@login_required
def favorites_page(request):
    try:
        favs = Favorite.objects.filter(user=request.user).select_related("challenge", "challenge__category").order_by("-created_at")
    except Exception:
        favs = []
    challenges = [f.challenge for f in favs] if hasattr(favs, '__iter__') else []
    for ch in challenges:
        ch.is_favorite = True
    return render(request, "accounts/favorites.html", {"challenges": challenges})