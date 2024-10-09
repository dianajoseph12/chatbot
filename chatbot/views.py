import re
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import redis
from .forms import SignUpForm, UploadForm, HolidayForm
from django.contrib.auth import authenticate, login, logout
from .chatbot_using_llm import initialize_llm, create_embeddingandcollection
from .models import Upload, User, UserRedisHistory
from django.contrib import messages
import uuid

r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_admin = form.cleaned_data.get("is_admin", False)
                user.is_employee = form.cleaned_data.get("is_employee", False)
                user.save()
                messages.success(request, "Registration successful.")
                return redirect("login_view")
            except Exception as e:
                print(f"Error saving user: {e}")
                messages.error(
                    request, "An error occurred during registration. Please try again."
                )
        else:
            print(form.errors)
            messages.error(
                request, "There was an error with the form. Please check your input."
            )
    else:
        form = SignUpForm()

    return render(request, "register.html", {"form": form})


def login_view(request):

    if "username" in request.session:
        messages.success(request, "success")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        print(user.is_authenticated, request.user.is_authenticated)

        if user and user.is_active:
            login(request, user)
        print(user.is_authenticated, request.user.is_authenticated)

        if user is not None and user.is_admin:
            request.session["username"] = username
            return redirect("adminpage")

        elif user is not None and user.is_employee:
            request.session["username"] = username
            return redirect("employee")
        else:
            messages.info(request, "invalid credentials")
            return redirect("login_view")
    else:
        return render(request, "login.html")


def adminpage(request):
    username = request.session.get("username")
    user = User.objects.get(username=username)
    if user.is_admin:
        history_entry = UserRedisHistory.objects.filter(user=user).first()
        if history_entry:
            redis_key = history_entry.redis_key
            chat_history = r.lrange(f"chat:{redis_key}", 0, -1)
        else:
            chat_history = []
        collections = Upload.objects.all()
        request.GET.get("collection_name")

        return render(
            request,
            "admin.html",
            {
                "user": user,
                "collections": collections,
                "chat_history": chat_history,
            },
        )

    else:
        return redirect("login_view")


def upload(request):

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if not form.is_valid():
            
            print(form.errors)

        if form.is_valid():
            
            file = request.FILES["file_name"]
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description")
            
            collection_name = f"{uuid.uuid4()}"
            
            print(
                f"File: {file}, Collection Name: {collection_name}, Title: {title}, Description: {description}"
            )
            try:
                Upload.objects.create(
                    file_name=file,
                    collection_name=collection_name,
                    title=title,
                    description=description,
                )
                collection_created = create_embeddingandcollection(
                    collection_name, file
                )
                if not collection_created:
                    print("ERROR")
                if collection_created:
                    print("Collection Created:", collection_created)

                    messages.success(
                        request, "File uploaded and processed successfully."
                    )
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

            return redirect("adminpage")
        else:
            print(form.errors)
        form = UploadForm()

    return render(request, "admin.html", {"form": form})


def employee(request):
    username = request.session.get("username")
    user = User.objects.get(username=username)
    if user.is_employee:
        history_entry = UserRedisHistory.objects.filter(user=user).first()
        if history_entry:
            redis_key = history_entry.redis_key
            chat_history = r.lrange(f"chat:{redis_key}", 0, -1)
        else:
            chat_history = []
        collections = Upload.objects.all()
        request.GET.get("collection_name")
        return render(
            request,
            "employee.html",
            {
                "user": user,
                "collections": collections,
                "chat_history": chat_history,
            },
        )
    else:
        return redirect("login_view")


def logout_user(request):
    logout(request)
    return redirect("login_view")


def getResponse(request):
    userMessage = request.GET.get("userMessage")

    selected_collection = request.GET.get("collection_name")
    

    if request.user.is_authenticated:
        user = request.user

        try:
            history_entry = UserRedisHistory.objects.filter(user=user).first()

            if history_entry:

                redis_key = history_entry.redis_key
                print(
                    f"Fetched existing redis_key for user {user.username}: {redis_key}"
                )
            else:

                redis_key = str(uuid.uuid4())
                UserRedisHistory.objects.create(
                    user=user, redis_key=redis_key, created_at=timezone.now()
                )
                print(
                    f"Generated and stored new redis_key for user {user.username}: {redis_key}"
                )

        except Exception as e:
            print(f"Error fetching or creating Redis history: {e}")
            return HttpResponse("Error processing Redis key.")

        r.rpush(f"chat:{redis_key}", f"User: {userMessage}")

        final_result = initialize_llm(redis_key, userMessage, selected_collection)

        r.rpush(f"chat:{redis_key}", f"Chatbot: {final_result}")

        chat_history = r.lrange(f"chat:{redis_key}", 0, -1)

    return HttpResponse(final_result)


def getChatHistory(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            history_entry = UserRedisHistory.objects.filter(user=user).first()
            if history_entry:
                redis_key = history_entry.redis_key

                chat_history = r.lrange(f"chat:{redis_key}", 0, -1)

                return JsonResponse({"chat_history": chat_history})
            else:
                return JsonResponse({"chat_history": []})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "User is not authenticated."}, status=403)


def add_holiday(request):

    if request.method == "POST":

        form = HolidayForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Holiday added successfully!")

            return redirect("adminpage")
    else:
        form = HolidayForm()

    return render(request, "add_holiday.html", {"form": form})
