from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Challenge, Category, UserProfile, Favorite, ChallengeProgress
from django.db.models import Sum, Q, Case, When, IntegerField
from django.http import JsonResponse, HttpResponseBadRequest
import traceback
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# --- ADDED IMPORTS FOR JWT AND API PROTECTION ---
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
import json


from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.core.paginator import Paginator
from django.utils import timezone


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
    # Independent filters: status axis and favorites axis
    status_filter = request.GET.get("status", "")  # '', 'completed', 'incomplete'
    favorites_filter = request.GET.get("favorites", "")  # '', '1'

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
        "difficulty": "difficulty",
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

    # --- Apply status filter BEFORE computing stats (since user expects counts for filtered set) ---
    if status_filter == "completed":
        completed_ids = ChallengeProgress.objects.filter(
            user=user, status=ChallengeProgress.Status.COMPLETED
        ).values_list("challenge_id", flat=True)
        qs = qs.filter(id__in=completed_ids)
    elif status_filter == "incomplete":
        # Incomplete defined as any progress not completed (attempted, in progress, unsolved)
        incom_ids = ChallengeProgress.objects.filter(
            user=user,
        ).exclude(status=ChallengeProgress.Status.COMPLETED).values_list("challenge_id", flat=True)
        qs = qs.filter(id__in=incom_ids)

    if favorites_filter == "1":
        fav_ids = Favorite.objects.filter(user=user).values_list("challenge_id", flat=True)
        qs = qs.filter(id__in=fav_ids)

    # --- Stats: totals & points for current filtered queryset ---
    total_count = qs.count()
    points_total = qs.aggregate(total_points=Sum("points"))["total_points"] or 0

    completed_count = 0
    in_progress_count = 0
    points_earned = 0

    try:
        # Check if using legacy model structure (safeguard)
        if hasattr(Challenge, "completed_by"):
            completed_qs = qs.filter(completed_by=user)
            completed_count = completed_qs.count()
            points_earned = completed_qs.aggregate(points=Sum("points"))["points"] or 0

            challenges = list(qs)
            completed_ids = set(completed_qs.values_list("id", flat=True))
            for ch in challenges:
                ch.is_completed = (ch.id in completed_ids)
                ch.is_in_progress = False # Legacy model fallback
                try:
                    ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0
                except Exception:
                    ch.tools_count = 0
        else:
            # Standard ChallengeProgress path
            progress_qs = ChallengeProgress.objects.filter(user=user, challenge__in=qs)
            completed_count = progress_qs.filter(status=ChallengeProgress.Status.COMPLETED).count()
            in_progress_count = progress_qs.filter(status=ChallengeProgress.Status.IN_PROGRESS).count()
            points_earned = progress_qs.filter(status=ChallengeProgress.Status.COMPLETED).aggregate(points=Sum("challenge__points"))["points"] or 0

            challenges = list(qs)
            prog_map = {p.challenge_id: p.status for p in progress_qs}
            
            for ch in challenges:
                status = prog_map.get(ch.id)
                ch.is_completed = (status == ChallengeProgress.Status.COMPLETED)
                ch.is_in_progress = (status == ChallengeProgress.Status.IN_PROGRESS) # <--- Logic Added Here
                try:
                    ch.tools_count = len(ch.topology.get("tools", [])) if ch.topology else 0
                except Exception:
                    ch.tools_count = 0

    except Exception:
        # Fallback if DB error occurs
        completed_count = 0
        in_progress_count = 0
        points_earned = 0
        challenges = list(qs)
        for ch in challenges:
            ch.is_completed = False
            ch.is_in_progress = False
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
        "selected_status": status_filter,
        "favorites_filter": favorites_filter,
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
    users_qs = User.objects.filter(is_active=True).order_by("username")

    # Preload progress for all users to compute points from completed challenges
    from collections import defaultdict
    from datetime import timedelta
    
    progress_rows = ChallengeProgress.objects.filter(status=ChallengeProgress.Status.COMPLETED)
    points_map = defaultdict(int)
    completed_count_map = defaultdict(int)
    completion_dates_map = defaultdict(set)

    for p in progress_rows.select_related("challenge"):
        points_map[p.user_id] += p.challenge.points
        completed_count_map[p.user_id] += 1
        if p.completed_at:
            local_date = timezone.localtime(p.completed_at).date()
            completion_dates_map[p.user_id].add(local_date)

    # Calculate streaks
    streak_map = {}
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)

    for user_id, dates in completion_dates_map.items():
        streak = 0
        check_date = today
        
        if check_date not in dates:
            if yesterday in dates:
                check_date = yesterday
            else:
                streak_map[user_id] = 0
                continue

        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)
        
        streak_map[user_id] = streak

    leaders = []
    for u in users_qs:
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
            "points": points_map.get(u.id, 0),
            "challenges": completed_count_map.get(u.id, 0),
            "streak": streak_map.get(u.id, 0),
            "image_uri": image_uri,
            "date_joined": u.date_joined,
        })

    # Order leaders by points desc then username
    leaders.sort(key=lambda r: (-r["points"], r["username"]))
    top = leaders[:3]
    rest = leaders[3:]
    start_rank = len(top) + 1

    # Current user's rank (1-based) if present in list
    current_user_rank = None
    current_user_stats = None
    for idx, row in enumerate(leaders, start=1):
        if row["id"] == request.user.id:
            current_user_rank = idx
            current_user_stats = row
            break

    context = {
        "top": top,
        "leaders": rest,
        "all_leaders": leaders,  # optional full list if template needs it
        "current_user_rank": current_user_rank,
        "current_user_stats": current_user_stats,
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
    # Inject temporary gameplay command instructions for Ring Around The Rosie
    # Use slug for robustness instead of title text match.
    if challenge.slug == "ring-around-the-rosie":
        initial_content += """

Commands (temporary prototype):
    /inprogress   -> mark this challenge as In Progress
    /complete     -> mark this challenge as Completed and award points (one-time)
Type commands in the Terminal window. Use 'help' for generic terminal help.
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

    # Pull last progress for resume and detect unsaved warnings
    progress = None
    last_state = None
    unsaved_warning = False
    try:
        # Ensure a progress row exists as soon as a challenge is opened
        progress, created = ChallengeProgress.objects.get_or_create(
            user=request.user, challenge=challenge,
            defaults={"status": ChallengeProgress.Status.ATTEMPTED}
        )
        last_state = progress.last_state
        if not progress.last_saved_ok and progress.status != ChallengeProgress.Status.COMPLETED:
            unsaved_warning = True
        # When viewing non-readonly, switch to in-progress and pessimistically mark save as not-ok
        if request.GET.get("readonly") != "1":
            if progress.status in [ChallengeProgress.Status.ATTEMPTED, ChallengeProgress.Status.UNSOLVED]:
                progress.status = ChallengeProgress.Status.IN_PROGRESS
            progress.last_saved_ok = False
            progress.save(update_fields=["status", "last_saved_ok", "updated_at"])
    except Exception:
        pass

    # Fallback: ensure progress row exists & status is IN_PROGRESS when page is opened (non-readonly)
    if request.GET.get("readonly") != "1":
        try:
            if progress is None:
                progress, _ = ChallengeProgress.objects.get_or_create(
                    user=request.user, challenge=challenge,
                    defaults={"status": ChallengeProgress.Status.IN_PROGRESS}
                )
            if progress.status in [ChallengeProgress.Status.ATTEMPTED, ChallengeProgress.Status.UNSOLVED]:
                ChallengeProgress.objects.filter(pk=progress.pk).update(
                    status=ChallengeProgress.Status.IN_PROGRESS,
                    updated_at=timezone.now()
                )
        except Exception:
            # Silent fallback; we surface errors only on explicit POST actions
            pass

    readonly = request.GET.get("readonly") == "1"

    return render(request, "accounts/challenge.html", {
        "challenge": challenge,
        "categories": categories,
        "initial_text_content": initial_content,
        "is_favorite": is_favorite,
        "readonly": readonly,
        "last_state": last_state,
        "unsaved_warning": unsaved_warning,
        "save_progress_url": reverse('save_progress', args=[challenge.id]),
        "update_status_url": reverse('update_challenge_status', args=[challenge.id]),
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


@login_required
@csrf_exempt  # Prototype: remove when front-end CSRF stable
def save_progress(request, challenge_id: int):
    """Persist user's last_state for a challenge and mark save as successful.
    Expected JSON body: { "last_state": <any json-serializable> }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    challenge = get_object_or_404(Challenge, id=challenge_id)
    import json
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        payload = {}
    last_state = payload.get("last_state")
    try:
        prog, _ = ChallengeProgress.objects.get_or_create(
            user=request.user, challenge=challenge,
            defaults={"status": ChallengeProgress.Status.IN_PROGRESS}
        )
        # Apply updates
        prog.last_state = last_state
        prog.last_saved_ok = True
        if prog.status == ChallengeProgress.Status.ATTEMPTED:
            prog.status = ChallengeProgress.Status.IN_PROGRESS
        prog.save()  # full save (avoid update_fields mismatch with DB schema)
        return JsonResponse({"ok": True})
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return JsonResponse({"ok": False, "message": f"Save failed: {type(e).__name__}: {e}", "debug": tb}, status=500)


@login_required
@csrf_exempt  # Prototype: remove when front-end CSRF stable
def update_challenge_status(request, challenge_id: int):
    """Update a user's ChallengeProgress status via simple POST.
    Accepts form-encoded or JSON body with 'status'. Supported values: in_progress, completed.
    Returns JSON: { ok, status, points_awarded?, message }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    challenge = get_object_or_404(Challenge, id=challenge_id)
    # Extract status from POST or JSON
    status_val = request.POST.get("status")
    if not status_val:
        import json
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            status_val = payload.get("status")
        except Exception:
            status_val = None
    if status_val not in ["in_progress", "completed"]:
        return JsonResponse({"ok": False, "message": "Invalid status."}, status=400)
    try:
        prog, _ = ChallengeProgress.objects.get_or_create(
            user=request.user, challenge=challenge,
            defaults={"status": ChallengeProgress.Status.ATTEMPTED}
        )
        if status_val == "in_progress":
            if prog.status == ChallengeProgress.Status.COMPLETED:
                return JsonResponse({"ok": True, "status": prog.status, "message": "Already completed. Cannot revert to In Progress."})
            if prog.status != ChallengeProgress.Status.IN_PROGRESS:
                prog.status = ChallengeProgress.Status.IN_PROGRESS
                prog.save()
            return JsonResponse({"ok": True, "status": prog.status, "message": "Marked In Progress."})
        # completed path
        if prog.status == ChallengeProgress.Status.COMPLETED:
            return JsonResponse({"ok": True, "status": prog.status, "message": "Already completed. Points previously awarded."})
        prog.mark_completed()
        return JsonResponse({"ok": True, "status": prog.status, "points_awarded": challenge.points, "message": f"Congratulations! Challenge completed. +{challenge.points} points."})
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return JsonResponse({"ok": False, "message": f"Server error ({type(e).__name__}): {e}", "debug": tb}, status=500)


@login_required
@csrf_exempt
def api_mark_inprogress(request):
    """Endpoint /inprogress
    POST body or form data must include 'slug' or 'id'. Marks challenge IN_PROGRESS.
    Returns current status; does not award points.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    slug = request.POST.get("slug")
    ch_id = request.POST.get("id")
    if not slug and not ch_id:
        # Try JSON body
        import json
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            payload = {}
        slug = payload.get("slug")
        ch_id = payload.get("id")
    try:
        if slug:
            challenge = get_object_or_404(Challenge, slug=slug)
        else:
            challenge = get_object_or_404(Challenge, id=int(ch_id))
    except Exception:
        return JsonResponse({"ok": False, "message": "Challenge not found."}, status=404)
    prog, _ = ChallengeProgress.objects.get_or_create(
        user=request.user, challenge=challenge,
        defaults={"status": ChallengeProgress.Status.ATTEMPTED}
    )
    if prog.status == ChallengeProgress.Status.COMPLETED:
        return JsonResponse({"ok": True, "status": prog.status, "message": "Already completed."})
    if prog.status != ChallengeProgress.Status.IN_PROGRESS:
        prog.status = ChallengeProgress.Status.IN_PROGRESS
        prog.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True, "status": prog.status, "message": "Marked In Progress."})


@login_required
@csrf_exempt
def api_mark_complete(request):
    """Endpoint /complete
    POST body or form data must include 'slug' or 'id'. Marks challenge COMPLETED and awards points.
    Idempotent: points only returned first time.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    slug = request.POST.get("slug")
    ch_id = request.POST.get("id")
    if not slug and not ch_id:
        import json
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            payload = {}
        slug = payload.get("slug")
        ch_id = payload.get("id")
    try:
        if slug:
            challenge = get_object_or_404(Challenge, slug=slug)
        else:
            challenge = get_object_or_404(Challenge, id=int(ch_id))
    except Exception:
        return JsonResponse({"ok": False, "message": "Challenge not found."}, status=404)
    prog, _ = ChallengeProgress.objects.get_or_create(
        user=request.user, challenge=challenge,
        defaults={"status": ChallengeProgress.Status.ATTEMPTED}
    )
    if prog.status == ChallengeProgress.Status.COMPLETED:
        # Already completed— do not re-award points
        return JsonResponse({"ok": True, "status": prog.status, "points_awarded": 0, "message": "Already completed."})
    prog.mark_completed()
    return JsonResponse({"ok": True, "status": prog.status, "points_awarded": challenge.points, "message": f"Completed. +{challenge.points} points."})


@login_required
def completed_challenges_page(request):
    """List all challenges the user has completed with completion date."""
    progress_qs = ChallengeProgress.objects.filter(
        user=request.user, status=ChallengeProgress.Status.COMPLETED
    ).select_related("challenge", "challenge__category").order_by("-completed_at")

    items = []
    for p in progress_qs:
        ch = p.challenge
        items.append({
            "id": ch.id,
            "slug": ch.slug,
            "title": ch.title,
            "category": ch.category.name if ch.category else "",
            "completed_at": p.completed_at,
        })

    return render(request, "accounts/completed_challenges.html", {"items": items})


@login_required
def incomplete_challenges_page(request):
    """List attempted/unsolved/in-progress challenges with status and warnings."""
    progress_qs = ChallengeProgress.objects.filter(
        user=request.user,
        status__in=[
            ChallengeProgress.Status.ATTEMPTED,
            ChallengeProgress.Status.IN_PROGRESS,
            ChallengeProgress.Status.UNSOLVED,
        ],
    ).select_related("challenge", "challenge__category").order_by("-updated_at")

    items = []
    for p in progress_qs:
        ch = p.challenge
        items.append({
            "id": ch.id,
            "slug": ch.slug,
            "title": ch.title,
            "category": ch.category.name if ch.category else "",
            "status": p.get_status_display(),
            "unsaved": not p.last_saved_ok,
        })

    return render(request, "accounts/incomplete_challenges.html", {"items": items})


def chatbot_page(request):
    """Render the chatbot page"""
    return render(request, 'accounts/chatbot.html')


def chatbot_api(request):
    """Handle chatbot API requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Check if API key is configured
        if not settings.GEMINI_API_KEY:
            return JsonResponse({
                'error': 'Gemini API key not configured. Please add GEMINI_API_KEY to your .env file.',
                'success': False
            }, status=500)
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use generate_content directly without specifying model
        # This uses the default available model
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        # System context for CTF Academy
        context = """You are a helpful AI assistant for CTF Academy, a LeetCode-style learning platform for offensive cybersecurity. 

CTF Academy offers:
- Logical cybersecurity challenges focusing on reasoning and problem-solving
- Sandboxed environments for safe exploration
- Leaderboards and streak tracking for competition
- Various challenge categories (Web, Cryptography, Reverse Engineering, etc.)

Answer questions about:
- Cybersecurity concepts and techniques
- How to approach CTF challenges
- Platform features and navigation
- General offensive security topics

Be helpful, encouraging, and educational. Keep responses concise and actionable."""
        
        full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        
        # Try the working models for this API key (Gemini 2.0/2.5)
        model_attempts = [
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-flash-latest',
            'gemini-2.5-pro',
            'gemini-pro-latest',
        ]
        
        response_text = None
        for model_name in model_attempts:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                response_text = response.text
                print(f"✓ SUCCESS with model: {model_name}")
                break
            except Exception as e:
                error_msg = str(e)[:150]
                print(f"✗ Model '{model_name}' failed: {error_msg}")
                continue
        
        if not response_text:
            return JsonResponse({
                'error': 'Could not generate response with any available model. Please check your API key permissions.',
                'success': False
            }, status=500)
        
        return JsonResponse({
            'response': response_text,
            'success': True
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({
            'error': 'Invalid JSON format',
            'success': False
        }, status=400)
    
    except Exception as e:
        print(f"Chatbot API error: {type(e).__name__}: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return JsonResponse({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }, status=500)
        

# ============================================================================
# 1. ENHANCED ADMIN DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_dashboard_page(request):
    """Enhanced admin dashboard with comprehensive analytics"""
    
    # === USER STATISTICS ===
    total_users = User.objects.filter(is_active=True).count()
    new_users_this_month = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Top performers (most points)
    top_users = []
    for user in User.objects.filter(is_active=True)[:10]:
        completed = ChallengeProgress.objects.filter(
            user=user, 
            status=ChallengeProgress.Status.COMPLETED
        )
        total_points = completed.aggregate(
            points=Sum('challenge__points')
        )['points'] or 0
        
        top_users.append({
            'username': user.username,
            'email': user.email,
            'points': total_points,
            'completed_count': completed.count(),
            'date_joined': user.date_joined
        })
    
    top_users.sort(key=lambda x: x['points'], reverse=True)
    top_users = top_users[:5]
    
    # === CHALLENGE STATISTICS ===
    total_challenges = Challenge.objects.filter(is_active=True).count()
    
    # Challenge completion rates
    challenges_with_stats = []
    for challenge in Challenge.objects.filter(is_active=True):
        progress_counts = ChallengeProgress.objects.filter(
            challenge=challenge
        ).values('status').annotate(count=Count('id'))
        
        completed = 0
        in_progress = 0
        attempted = 0
        
        for p in progress_counts:
            if p['status'] == ChallengeProgress.Status.COMPLETED:
                completed = p['count']
            elif p['status'] == ChallengeProgress.Status.IN_PROGRESS:
                in_progress = p['count']
            elif p['status'] == ChallengeProgress.Status.ATTEMPTED:
                attempted = p['count']
        
        total_attempts = completed + in_progress + attempted
        completion_rate = (completed / total_attempts * 100) if total_attempts > 0 else 0
        
        challenges_with_stats.append({
            'id': challenge.id,
            'title': challenge.title,
            'slug': challenge.slug,
            'category': challenge.category.name,
            'difficulty': challenge.difficulty,
            'points': challenge.points,
            'completed': completed,
            'in_progress': in_progress,
            'attempted': attempted,
            'completion_rate': round(completion_rate, 1)
        })
    
    # Sort by completion rate
    challenges_with_stats.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    # Most popular (favorited) challenges
    popular_challenges = Challenge.objects.annotate(
        fav_count=Count('favorited_by')
    ).order_by('-fav_count')[:5]
    
    # === PROGRESS ANALYTICS ===
    # Completion trend (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_completions = ChallengeProgress.objects.filter(
        status=ChallengeProgress.Status.COMPLETED,
        completed_at__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('completed_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Format for chart
    completion_trend = [
        {'date': item['day'].strftime('%Y-%m-%d'), 'count': item['count']}
        for item in daily_completions
    ]
    
    # === DIFFICULTY DISTRIBUTION ===
    difficulty_stats = Challenge.objects.filter(
        is_active=True
    ).values('difficulty').annotate(
        count=Count('id')
    ).order_by('difficulty')
    
    # === RECENT ACTIVITY ===
    recent_progress = ChallengeProgress.objects.select_related(
        'user', 'challenge'
    ).order_by('-updated_at')[:10]
    
    recent_activities = []
    for progress in recent_progress:
        recent_activities.append({
            'user': progress.user.username,
            'challenge': progress.challenge.title,
            'status': progress.get_status_display(),
            'timestamp': progress.updated_at,
            'points': progress.challenge.points if progress.status == ChallengeProgress.Status.COMPLETED else 0
        })
    
    context = {
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        'total_challenges': total_challenges,
        'top_users': top_users,
        'challenges_with_stats': challenges_with_stats[:10],
        'popular_challenges': popular_challenges,
        'completion_trend': completion_trend,
        'difficulty_stats': list(difficulty_stats),
        'recent_activities': recent_activities,
    }
    
    return render(request, "accounts/admin_dashboard.html", context)


# ============================================================================
# 2. USER MANAGEMENT
# ============================================================================

@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def admin_users_page(request):
    """Render the user management page with actual data"""
    from datetime import timedelta
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    
    # === USER STATISTICS ===
    total_users = User.objects.filter(is_active=True).count()
    
    # Active users (logged in within last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    active_users = User.objects.filter(
        is_active=True,
        last_login__gte=seven_days_ago
    ).count()
    
    # Admin users count
    admin_users = User.objects.filter(is_active=True, is_staff=True).count()
    
    # New users this month
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_this_month = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    
    # Calculate growth percentage (compare to previous month)
    sixty_days_ago = timezone.now() - timedelta(days=60)
    previous_month_users = User.objects.filter(
        date_joined__gte=sixty_days_ago,
        date_joined__lt=thirty_days_ago
    ).count()
    
    if previous_month_users > 0:
        growth_percentage = round(
            ((new_users_this_month - previous_month_users) / previous_month_users) * 100,
            1
        )
    else:
        growth_percentage = 100 if new_users_this_month > 0 else 0
    
    # === ALL USERS WITH DETAILS ===
    users_list = []
    for user in User.objects.all().order_by('-date_joined'):
        # Get completed challenges count
        completed_count = ChallengeProgress.objects.filter(
            user=user,
            status=ChallengeProgress.Status.COMPLETED
        ).count()
        
        # Calculate total points
        total_points = ChallengeProgress.objects.filter(
            user=user,
            status=ChallengeProgress.Status.COMPLETED
        ).aggregate(points=Sum('challenge__points'))['points'] or 0
        
        users_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'points': total_points,
            'completed_count': completed_count,
        })
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'new_users_this_month': new_users_this_month,
        'growth_percentage': growth_percentage,
        'users': users_list,
    }
    
    return render(request, "accounts/admin_users.html", context)


@login_required
@user_passes_test(is_admin)
def admin_users_list(request):
    """API endpoint to list all users with pagination and search"""
    search_query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    
    users_qs = User.objects.filter(is_active=True)
    
    if search_query:
        users_qs = users_qs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(users_qs.order_by('-date_joined'), 20)
    page_obj = paginator.get_page(page)
    
    users_data = []
    for user in page_obj:
        completed = ChallengeProgress.objects.filter(
            user=user,
            status=ChallengeProgress.Status.COMPLETED
        ).count()
        
        favorites = Favorite.objects.filter(user=user).count()
        
        total_points = ChallengeProgress.objects.filter(
            user=user,
            status=ChallengeProgress.Status.COMPLETED
        ).aggregate(points=Sum('challenge__points'))['points'] or 0
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'is_active': user.is_active,
            'completed_challenges': completed,
            'favorites': favorites,
            'total_points': total_points
        })
    
    return JsonResponse({
        'users': users_data,
        'page': page,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count
    })


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def admin_user_update(request, user_id):
    """Update user details"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")
    
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Update fields
        if 'username' in data:
            target_user.username = data['username']
        if 'email' in data:
            target_user.email = data['email']
        if 'first_name' in data:
            target_user.first_name = data['first_name']
        if 'last_name' in data:
            target_user.last_name = data['last_name']
        if 'is_active' in data:
            target_user.is_active = data['is_active']
        
        target_user.save()
        
        return JsonResponse({
            'ok': True,
            'message': f'User {target_user.username} updated successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(is_admin)
@csrf_exempt
def admin_user_delete(request, user_id):
    """Deactivate a user"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")
    
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user.is_superuser:
        return JsonResponse({
            'ok': False,
            'message': 'Cannot deactivate admin users'
        }, status=400)
    
    target_user.delete() 
    
    return JsonResponse({
        'ok': True,
        'message': f'User {target_user.username} deleted.'
    })


# ============================================================================
# 3. CHALLENGE ANALYTICS (VIEW ONLY - NO CRUD)
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_challenge_analytics(request, challenge_id):
    """Get detailed analytics for a specific challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Progress breakdown
    progress_counts = ChallengeProgress.objects.filter(
        challenge=challenge
    ).values('status').annotate(count=Count('id'))
    
    status_breakdown = {}
    for item in progress_counts:
        status_breakdown[item['status']] = item['count']
    
    # Average completion time
    completed_progress = ChallengeProgress.objects.filter(
        challenge=challenge,
        status=ChallengeProgress.Status.COMPLETED,
        completed_at__isnull=False
    )
    
    completion_times = []
    for p in completed_progress:
        if p.started_at and p.completed_at:
            delta = p.completed_at - p.started_at
            completion_times.append(delta.total_seconds() / 60)  # minutes
    
    avg_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Favorite count
    favorite_count = Favorite.objects.filter(challenge=challenge).count()
    
    return JsonResponse({
        'challenge': {
            'id': challenge.id,
            'title': challenge.title,
            'difficulty': challenge.difficulty,
            'points': challenge.points
        },
        'status_breakdown': status_breakdown,
        'average_completion_time_minutes': round(avg_time, 2),
        'favorite_count': favorite_count,
        'completion_times': completion_times[:10]
    })


# ============================================================================
# 4. USER PROGRESS DETAILS
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_user_progress(request, user_id):
    """Get detailed progress for a specific user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get all progress
    progress_qs = ChallengeProgress.objects.filter(
        user=user
    ).select_related('challenge', 'challenge__category').order_by('-updated_at')
    
    progress_data = []
    total_points = 0
    
    for progress in progress_qs:
        challenge = progress.challenge
        
        # Calculate time spent if completed
        time_spent = None
        if progress.completed_at and progress.started_at:
            delta = progress.completed_at - progress.started_at
            time_spent = int(delta.total_seconds() / 60)  # minutes
        
        # Add points if completed
        if progress.status == ChallengeProgress.Status.COMPLETED:
            total_points += challenge.points
        
        progress_data.append({
            'challenge_id': challenge.id,
            'challenge_title': challenge.title,
            'challenge_slug': challenge.slug,
            'category': challenge.category.name,
            'difficulty': challenge.difficulty,
            'points': challenge.points,
            'status': progress.status,
            'status_display': progress.get_status_display(),
            'started_at': progress.started_at.isoformat() if progress.started_at else None,
            'updated_at': progress.updated_at.isoformat(),
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
            'time_spent_minutes': time_spent,
            'last_saved_ok': progress.last_saved_ok
        })
    
    # Get favorites
    favorites = Favorite.objects.filter(user=user).select_related('challenge')
    favorite_data = [
        {
            'challenge_id': fav.challenge.id,
            'challenge_title': fav.challenge.title,
            'created_at': fav.created_at.isoformat()
        }
        for fav in favorites
    ]
    
    return JsonResponse({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.isoformat()
        },
        'progress': progress_data,
        'favorites': favorite_data,
        'total_points': total_points,
        'completed_count': len([p for p in progress_data if p['status'] == 'completed']),
        'in_progress_count': len([p for p in progress_data if p['status'] == 'in_progress'])
    })


# ============================================================================
# 5. CATEGORY STATISTICS
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_category_stats(request):
    """Get statistics grouped by category"""
    categories = Category.objects.all()
    
    category_stats = []
    
    for category in categories:
        challenges = Challenge.objects.filter(category=category, is_active=True)
        challenge_count = challenges.count()
        
        # Count completions across all challenges in this category
        total_completions = ChallengeProgress.objects.filter(
            challenge__category=category,
            status=ChallengeProgress.Status.COMPLETED
        ).count()
        
        # Total points available in this category
        total_points = challenges.aggregate(total=Sum('points'))['total'] or 0
        
        # Most popular challenge in category
        popular_challenge = challenges.annotate(
            completion_count=Count('progress', filter=Q(progress__status=ChallengeProgress.Status.COMPLETED))
        ).order_by('-completion_count').first()
        
        category_stats.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'icon_class': category.icon_class,
            'challenge_count': challenge_count,
            'total_completions': total_completions,
            'total_points': total_points,
            'most_popular': {
                'title': popular_challenge.title if popular_challenge else None,
                'completions': popular_challenge.completion_count if popular_challenge else 0
            } if popular_challenge else None
        })
    
    return JsonResponse({
        'categories': category_stats,
        'total_categories': len(category_stats)
    })


# ============================================================================
# 6. DATA EXPORT
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_export_data(request):
    """Export admin data as JSON"""
    export_type = request.GET.get('type', 'users')
    
    if export_type == 'users':
        users = User.objects.filter(is_active=True).values(
            'id', 'username', 'email', 'date_joined', 'is_active'
        )
        return JsonResponse({'users': list(users)})
    
    elif export_type == 'challenges':
        challenges = Challenge.objects.filter(is_active=True).values(
            'id', 'title', 'slug', 'difficulty', 'points', 'category__name'
        )
        return JsonResponse({'challenges': list(challenges)})
    
    elif export_type == 'progress':
        progress = ChallengeProgress.objects.select_related(
            'user', 'challenge'
        ).values(
            'user__username',
            'challenge__title',
            'status',
            'started_at',
            'updated_at',
            'completed_at'
        )
        return JsonResponse({'progress': list(progress)})
    
    return JsonResponse({'error': 'Invalid export type'}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Get detailed information for a specific user"""
    user = get_object_or_404(User, id=user_id)
    
    # Calculate user stats
    completed_count = ChallengeProgress.objects.filter(
        user=user,
        status=ChallengeProgress.Status.COMPLETED
    ).count()
    
    total_points = ChallengeProgress.objects.filter(
        user=user,
        status=ChallengeProgress.Status.COMPLETED
    ).aggregate(points=Sum('challenge__points'))['points'] or 0
    
    favorites_count = Favorite.objects.filter(user=user).count()
    
    # Recent activity
    recent_progress = ChallengeProgress.objects.filter(
        user=user
    ).select_related('challenge').order_by('-updated_at')[:5]
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'completed_count': completed_count,
        'total_points': total_points,
        'favorites_count': favorites_count,
        'recent_activity': [
            {
                'challenge_title': p.challenge.title,
                'status': p.get_status_display(),
                'updated_at': p.updated_at
            }
            for p in recent_progress
        ]
    }
    
    return JsonResponse({'user': user_data})
