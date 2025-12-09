# Testing User Suspension System

## Setup

### Create Test Accounts
You'll need at least 3 accounts:
1. **admin** - Admin account (already exists)
2. **moderator_user** - Will be made a moderator
3. **regular_user** - Will be suspended
4. **another_user** - For viewing suspended user's profile

### Make Someone a Moderator
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Login as admin (USER: adminb24, PASS: UVAcs3240f25b24)
3. Navigate to **Users** → **Profiles**
4. Find moderator_user's profile
5. Check the **is_moderator** checkbox
6. Click **Save**

---

## Test 1: Suspend a User via Profile Page

**Setup:**
1. Login as regular_user
2. Create a post with some test content
3. Logout

**Test:**
1. Login as moderator_user
2. Navigate to regular_user's profile (e.g., `/users/profile/view/regular_user/`)
3. Click **Suspend User** button
4. Enter reason: "Posting inappropriate content"
5. Click **Suspend User**

**Expected Results:**
- ✅ Redirected to user's profile
- ✅ Success message: "regular_user has been suspended for: Posting inappropriate content"
- ✅ Profile now shows "🚫 Account Suspended" badge
- ✅ "Suspend User" button changes to "Reinstate User"
- ✅ Suspension details visible:
  - Reason
  - Suspended by moderator_user
  - Timestamp

**Database Verification:**
1. Go to Admin → Users → Profiles
2. Click on regular_user's profile
3. Should see:
   - `is_suspended = True`
   - `suspension_reason = "Posting inappropriate content"`
   - `suspended_by = moderator_user`
   - `suspended_at = [current date/time]`

---

## Test 2: Suspended User Cannot Create Posts

**Setup:**
1. Login as regular_user (who is now suspended)
2. Go to forum

**Test:**
1. Try to create a new post
2. Should be redirected to post list with error message
3. Error should display: "Your account has been suspended. Reason: Posting inappropriate content"

**Expected Results:**
- ✅ User cannot access post creation form
- ✅ Receives error message with suspension reason
- ✅ Post list displayed instead
- ✅ No post was created

---

## Test 3: Suspended User Cannot Add Comments

**Setup:**
1. Login as regular_user (suspended)
2. Go to a post detail page

**Test:**
1. Try to post a comment
2. Fill in comment form and submit

**Expected Results:**
- ✅ Cannot post comment
- ✅ Error message shows: "Your account has been suspended. Reason: Posting inappropriate content"
- ✅ Redirected back to post detail
- ✅ No comment was created

---

## Test 4: Suspended User CAN View Content

**Setup:**
1. Login as regular_user (suspended)
2. Navigate to forum

**Test:**
1. Browse posts
2. Read comments
3. View user profiles

**Expected Results:**
- ✅ Can view all posts normally
- ✅ Can read comments
- ✅ Can see other user profiles
- ✅ Viewing functionality works normally
- ✅ Only creation/posting is blocked

---

## Test 5: Reinstate User via Profile Page

**Setup:**
1. Login as moderator_user
2. Go to regular_user's profile

**Test:**
1. Click **Reinstate User** button
2. Review suspension details displayed
3. Click **Yes, Reinstate User**

**Expected Results:**
- ✅ Success message: "regular_user has been reinstated."
- ✅ "🚫 Account Suspended" badge disappears
- ✅ "Reinstate User" button changes back to "Suspend User"
- ✅ Suspension details no longer displayed

**Verify:**
1. Logout and login as regular_user
2. Try to create a post - should work normally
3. Try to add a comment - should work normally

---

## Test 6: View Suspended Users List

**Setup:**
1. Login as moderator_user
2. Have at least one suspended user

**Test:**
1. Navigate to `/users/suspended-users/`

**Expected Results:**
- ✅ Table displays with columns:
  - Username
  - Display Name
  - Suspension Reason
  - Suspended By
  - Suspended At
- ✅ Shows regular_user with all suspension details
- ✅ "Reinstate" button available for each user
- ✅ Can click reinstate button to reinstate user directly

---

## Test 7: Admin Bulk Suspend

**Setup:**
1. Go to Admin → Users → Profiles
2. Have multiple regular users not yet suspended

**Test:**
1. Select 2-3 users
2. Choose "Suspend selected users" from dropdown
3. Click Go

**Expected Results:**
- ✅ All selected users marked as `is_suspended = True`
- ✅ Can see them in suspended users list
- ✅ They cannot create posts/comments

---

## Test 8: Admin Bulk Reinstate

**Setup:**
1. Go to Admin → Users → Profiles
2. Filter by `is_suspended = True`
3. Have multiple suspended users

**Test:**
1. Select all suspended users
2. Choose "Reinstate selected users" from dropdown
3. Click Go

**Expected Results:**
- ✅ All selected users marked as `is_suspended = False`
- ✅ `suspended_at`, `suspension_reason`, `suspended_by` are cleared
- ✅ Users can now create posts/comments
- ✅ No longer appear in suspended users list

---

## Test 9: Non-Moderator Cannot Suspend

**Setup:**
1. Login as another_user (not a moderator)
2. Go to regular_user's profile

**Test:**
1. Look for "Suspend User" button

**Expected Results:**
- ✅ "Suspend User" button NOT visible
- ✅ If manually navigating to `/users/suspend/regular_user/`:
  - Should redirect to home page or show no moderation buttons
  - No suspension form displayed

---

## Test 10: Admin Moderator Actions

**Setup:**
1. Go to Admin → Users → Profiles
2. Select a user

**Test:**
1. Use "Promote to moderator" action to make user a moderator
2. Save

**Expected Results:**
- ✅ User's `is_moderator = True`
- ✅ User can now suspend other users
- ✅ User can access `/users/suspended-users/`

**Reverse:**
1. Select same user
2. Use "Remove moderator status" action
3. Save

**Expected Results:**
- ✅ User's `is_moderator = False`
- ✅ User can no longer suspend users
- ✅ Redirected when trying to access moderator features

---

## Test 11: Suspension Data Persistence

**Setup:**
1. Suspend a user with specific reason
2. Close browser/logout
3. Login as different moderator

**Test:**
1. Navigate to suspended user's profile
2. View suspension details

**Expected Results:**
- ✅ Suspension data still present
- ✅ Original moderator name shows
- ✅ Original suspension reason shows
- ✅ Timestamp unchanged

---

## Test 12: Re-Suspension Prevention

**Setup:**
1. User is already suspended

**Test:**
1. Login as moderator
2. Go to suspended user's profile
3. Try to suspend again

**Expected Results:**
- ✅ "Suspend User" button changes to "Reinstate User"
- ✅ If manually navigating to suspend page, shows warning:
  - "regular_user is already suspended"
  - Redirects back to profile

---

## Database Check (Django Shell)

```bash
python manage.py shell
```

```python
from users.models import Profile
from django.contrib.auth.models import User

# Check suspended users
Profile.objects.filter(is_suspended=True)

# Check specific user
user = User.objects.get(username='regular_user')
print(f"Suspended: {user.profile.is_suspended}")
print(f"Reason: {user.profile.suspension_reason}")
print(f"Suspended By: {user.profile.suspended_by}")
print(f"Suspended At: {user.profile.suspended_at}")

# Check moderators
Profile.objects.filter(is_moderator=True)

# Suspend a user programmatically
moderator = User.objects.get(username='moderator_user')
user.profile.suspend(moderator, "Test suspension reason")

# Reinstate a user programmatically
user.profile.reinstate()
```

---

## Troubleshooting

### "Cannot find Suspend User button"
- Make sure you're logged in as a moderator
- Check Admin → Profiles that user has `is_moderator = True`
- Hard refresh browser (Ctrl+Shift+R)
- Make sure you're viewing another user's profile (can't suspend yourself)

### "Suspended user can still post"
- Check database to verify `is_suspended = True`
- Check forum/views.py post_create and post_detail functions have suspension checks
- Make sure suspension check isn't in a try/except that silently fails
- Restart Django server

### "Reinstate button not appearing"
- Verify user is actually suspended: `is_suspended = True`
- Check profile_view.html template has reinstate button code
- Admin shows `is_suspended = False` for user

### "Error message not showing"
- Check messages are configured in settings.py
- Check templates include messages block
- Check forum/views.py has `from django.contrib import messages`

---

## Performance Notes

- Suspension check happens on every post/comment creation (minimal overhead)
- Bulk operations in admin are efficient with QuerySet.update()
- No N+1 queries in suspended users list (uses select_related)

---

## Quick Test Checklist

- [ ] Create test moderator account
- [ ] Suspend user via profile page ✓
- [ ] Verify suspension badge on profile
- [ ] Verify suspended user can't post
- [ ] Verify suspended user can't comment
- [ ] Verify suspended user can still view content
- [ ] Reinstate user via profile
- [ ] Verify reinstated user can post
- [ ] View suspended users list
- [ ] Admin bulk suspend works
- [ ] Admin bulk reinstate works
- [ ] Non-moderator can't suspend
- [ ] Suspension data persists
- [ ] Can't double-suspend user
