import base64
import pyotp
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls.base import reverse
from django.utils.cache import time
from django.utils.http import urlencode
from django.utils.timezone import now
from .forms import SignUpForm, UnlockForm
from .forms import TOTPURLForm
from .models import TOTPEntry
from .crypto import decrypt_secret, derive_user_key, encrypt_secret

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
    if request.user.is_authenticated:
        return redirect('totps-ui')
    return render(request, 'core/home.html')


@login_required
def add_totp_view(request):
    if request.method == 'POST':
        form = TOTPURLForm(request.POST)
        if form.is_valid():
            otp_url = form.cleaned_data['otp_url']

            parsed = urllib.parse.urlparse(otp_url)
            if parsed.scheme != 'otpauth' or parsed.netloc != 'totp':
                form.add_error('otp_url', 'Invalid TOTP URL format.')
                return render(request, 'core/add_totp.html', {'form': form})

            label = urllib.parse.unquote(parsed.path[1:])
            account_name = label.split(':')[-1] if ':' in label else label
            query = urllib.parse.parse_qs(parsed.query)

            secret = query.get('secret', [None])[0]
            issuer = query.get('issuer', [None])[0]
            digits = int(query.get('digits', [6])[0])
            period = int(query.get('period', [30])[0])

            if not secret:
                form.add_error('otp_url', 'Secret is missing in the URL.')
                return render(request, 'core/add_totp.html', {'form': form})

            key_b64 = request.session.get('totp_key')
            if not key_b64 or request.session.get('totp_key_expires', 0) < time.time():
                unlock_url = reverse('unlock')
                query = urlencode({'next': request.path})
                return redirect(f'{unlock_url}?{query}')

            key = base64.b64decode(key_b64)
            encrypted_secret = encrypt_secret(secret, key)

            TOTPEntry.objects.create(
                user=request.user,
                account_name=account_name,
                issuer=issuer,
                encrypted_secret=encrypted_secret,
                digits=digits,
                period=period
            )

            return redirect('home')
    else:
        form = TOTPURLForm()
    return render(request, 'core/add_totp.html', {'form': form})

@login_required
def unlock_view(request):
    if request.method == 'POST':
        form = UnlockForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = request.user

            if not user.check_password(password):
                form.add_error('password', 'Incorrect password')
            else:
                # Derive key using user's salt
                salt = bytes(user.userprofile.encryption_salt)
                key = derive_user_key(password, salt)

                # Store derived key in session
                request.session['totp_key'] = key.decode()
                request.session['totp_key_expires'] = int(time.time()) + 300  # optional 5 min expiry

                # Redirect to original target
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
    else:
        form = UnlockForm()

    return render(request, 'core/unlock.html', {'form': form})

def totps_ui_view(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/totps_ui.html')

def current_totps_view(request):
    if "totp_key" not in request.session:
        return JsonResponse({"error": "unauthorized"}, status=401)

    user_key = request.session["totp_key"].encode()
    entries = TOTPEntry.objects.filter(user=request.user)
    response = []

    for entry in entries:
        try:
            secret = decrypt_secret(bytes(entry.encrypted_secret), user_key)
            totp = pyotp.TOTP(secret)
            otp = totp.now()
            interval = totp.interval  # default 30
            refresh_at = ((int(now().timestamp()) // interval) + 1) * interval
            response.append({
                "issuer": entry.issuer,
                "account_name": entry.account_name,
                "otp": otp,
                "refreshes_at": refresh_at,
            })
        except Exception as e:
            print(e)
            # Could not decrypt or generate
            response.append({
                "issuer": entry.issuer,
                "account_name": entry.account_name,
                "otp": None,
                "refreshes_at": None,
                "error": "Decryption failed"
            })

    return JsonResponse(response, safe=False)
