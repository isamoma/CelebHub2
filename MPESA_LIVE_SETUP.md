# Live M-Pesa STK Push Setup & Testing Guide

## Status: ✅ Production-Ready

Your application is now configured to use **live M-Pesa endpoints** (production).

---

## Configuration Summary

### Environment Variables (instance/.env)
```dotenv
MPESA_ENV=production                                    # Switches to live endpoints
MPESA_CONSUMER_KEY=6E8uL2bCO7A8VTvwKdQF4AAyNb7xeFhQA1bQwau11q41f9Il9pmCu6IRzHOFCn6m
MPESA_CONSUMER_SECRET=MykRvhWpHdFitAO7ZhrI0wwOID7GQTAvAi0Xt3C9HNyOvwUD
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://celebhub2.onrender.com/mpesa/callback
```

### Key Endpoints in Your App
- **User Payment Form**: `/user/dashboard` → Feature Me form (KSh 500)
- **Profile Payment Form**: `/celebrity/<slug>` → Feature Me form (any amount)
- **STK Push Initiator**: `POST /pay` (requires authentication)
- **Callback Handler**: `POST /mpesa/callback` (CSRF-exempt, updates celebrity featured status)

---

## How It Works (Live)

1. **User logs in** → `/user/login` or `/signup`
2. **User enters M-Pesa phone** → POST to `/pay` with phone, amount
3. **STK prompt appears** → User enters M-Pesa PIN
4. **Payment completes** → M-Pesa PUSTs (HTTP notification) to `/mpesa/callback`
5. **Celebrity marked featured** → `featured=True` for 30 days, status="paid"
6. **Homepage updated** → Featured profile appears on homepage

### Production Base URL
```
https://api.safaricom.co.ke  (live endpoints)
```

### Sandbox Base URL (for testing before production)
- Change `MPESA_ENV=sandbox` in `.env` to test without actual charges
- Uses: `https://sandbox.safaricom.co.ke`

---

## Testing Live STK Push Locally

To test with a real M-Pesa phone number without deploying:

### Option 1: Local Testing (Recommended for first test)
```bash
# 1. Set MPESA_ENV to sandbox first to avoid real charges
export MPESA_ENV=sandbox
python -m flask run

# 2. Navigate to http://127.0.0.1:5000
# 3. Sign up or log in
# 4. Go to dashboard and enter a test phone number (Safaricom test number if available)
# 5. Click "Feature (KSh 500)"
# 6. An STK prompt should appear on the test phone
```

### Option 2: Deploy & Test in Production
```bash
# After verifying with sandbox:
# 1. Push code to Render (auto-deploys)
# 2. Set MPESA_ENV=production in Render env vars
# 3. Test on live domain: https://celebhub2.onrender.com/user/dashboard
# 4. User experiences real STK push on their phone
```

---

## Verification Checklist

Before going live, verify:

- ✅ `MPESA_ENV=production` in `.env` (or Render env vars)
- ✅ `MPESA_CALLBACK_URL=https://celebhub2.onrender.com/mpesa/callback` is correct
- ✅ Admin credentials set: `ADMIN_USERNAMES=ISAMOMAadmin` with `ADMIN_PASSWORD`
- ✅ Database configured (MONGO_URI or in-memory Mongo)
- ✅ M-Pesa consumer Key/Secret/Shortcode/Passkey are valid
- ✅ Test with a small amount (e.g., KSh 100) first
- ✅ Check `/admin/dashboard` after payment completes (celebrity should be marked featured)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" at `/admin/login` | Check ADMIN_USERNAMES and ADMIN_PASSWORD in `.env` |
| STK prompt doesn't appear | Verify MPESA_ENV, consumer key/secret, and phone number format (07XXXXXXXX) |
| Callback not received | Check MPESA_CALLBACK_URL is publicly accessible; test with `POST /mpesa/callback` manually |
| Celebrity not marked featured | Check admin dashboard → submissions; ensure callback ResultCode=0 (success) |
| Payment stuck as "pending" | If callback fails, manually check M-Pesa transaction logs or re-test |

---

## Next Steps

1. **Deploy to Render** (if not already):
   ```bash
   git push origin main
   ```
   Render auto-deploys. Set env vars in Render dashboard if different from local.

2. **Test with KSh 1-100** (small amount) to verify end-to-end flow before promoting to users.

3. **Monitor admin dashboard** for featured celebrities and payment status.

4. **Collect feedback** from initial users before promoting.

---

## File References

- **Payment Logic**: [app/routes.py](app/routes.py) lines 633-720 (STK push) and 722-772 (callback)
- **Admin Setup**: [create_admin.py](create_admin.py)
- **User Auth**: [app/templates/user/dashboard.html](app/templates/user/dashboard.html)
- **Configuration**: [instance/.env](instance/.env)

---

**Deployed at**: https://celebhub2.onrender.com
**Admin Panel**: https://celebhub2.onrender.com/admin/login
**User Dashboard**: https://celebhub2.onrender.com/user/dashboard
