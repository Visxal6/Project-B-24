# Testing the Moderator System

## Setup Steps

### 1. Create Test Accounts
You'll need at least 2 accounts: one regular user and one moderator.

```
Regular User:
- Username: testuser
- Password: testpass123

Moderator User:
- Username: moderator
- Password: modpass123
```

### 2. Make Someone a Moderator
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Login with your admin credentials (USER = adminb24, PASS = UVAcs3240f25b24)
3. Navigate to **Users** → **Profiles**
4. Find the moderator user's profile
5. Check the **is_moderator** checkbox
6. Click **Save**

---

## Testing the Moderator Features

### Test 1: Flag a Post as Inappropriate

**Setup:**
1. Login as the regular user (testuser)
2. Create a test post with some content

**Test:**
1. Logout and login as moderator
2. Go to that post's detail page
3. You should see three new buttons: **Flag**, **Edit**, **Remove**
4. Click **Flag** button
5. Add a moderation note (e.g., "Inappropriate language")
6. Submit
7. **Expected Result:** Post should still be visible but marked as flagged

**Verify in Admin:**
- Go to Admin → Forum → Posts
- You should see the post with `is_flagged_inappropriate = True`
- The moderation note should be saved

---

### Test 2: Edit Inappropriate Post Content

**Setup:**
1. Login as regular user and create a post with inappropriate content
2. Logout and login as moderator

**Test:**
1. Go to the post detail page
2. Click **Edit** button
3. Remove the inappropriate content or fix the text
4. Add a moderation note explaining what was changed
5. Click **Save Changes**

**Expected Result:**
- Post content is updated
- `is_flagged_inappropriate` is set to `False`
- Moderation note is saved

**Verify:**
- View the post as a regular user - should see edited content
- Go to Admin → Posts and check the moderation note

---

### Test 3: Remove/Delete Inappropriate Post

**Setup:**
1. Login as regular user and create a post
2. Logout and login as moderator

**Test:**
1. Go to the post detail page
2. Click **Remove** button
3. Add a reason for removal (e.g., "Violates community standards")
4. Click **Remove Post Permanently**

**Expected Result:**
- Post is completely deleted
- Redirects to post list
- Post no longer appears anywhere

**Verify:**
- Try to access the post URL directly - should get 404
- Post should not appear in any lists

---

### Test 4: Flag a Comment as Inappropriate

**Setup:**
1. Login as regular user and post a comment on any post
2. Logout and login as moderator

**Test:**
1. View the post with that comment
2. Hover over the comment - you should see moderation buttons
3. Click **Flag** button
4. Add a moderation note
5. Submit

**Expected Result:**
- Comment stays visible
- Marked as flagged in database
- Moderation note saved

**Verify in Admin:**
- Go to Admin → Forum → Comments
- Filter by `is_flagged_inappropriate = True`
- See your flagged comment

---

### Test 5: Edit Inappropriate Comment

**Setup:**
1. Login as regular user and post an offensive comment
2. Logout and login as moderator

**Test:**
1. View the post with that comment
2. Click **Edit** button on the comment
3. Update the comment text to remove offensive content
4. Add a moderation note
5. Click **Save Changes**

**Expected Result:**
- Comment content is updated
- Flag is cleared (`is_flagged_inappropriate = False`)
- Other users see the edited version

---

### Test 6: Remove a Comment

**Setup:**
1. Login as regular user and post a comment
2. Logout and login as moderator

**Test:**
1. View the post with the comment
2. Click **Remove** button
3. Add reason for removal
4. Click **Remove Comment Permanently**

**Expected Result:**
- Comment is deleted
- Page refreshes or redirects
- Comment no longer appears in replies

---

### Test 7: Verify Permissions (Non-Moderators Can't Moderate)

**Setup:**
1. Login as a regular (non-moderator) user

**Test:**
1. Try to manually access moderation URL: `http://localhost:8000/forum/post/1/flag-inappropriate/`
2. **Expected Result:** HTTP 403 Forbidden error

**Alternative Test:**
1. Go to any post or comment
2. You should NOT see Flag, Edit, or Remove moderation buttons
3. Only see your own Delete buttons if you're the author

---

### Test 8: Admin Panel Bulk Actions

**Setup:**
1. Go to Django Admin → Forum → Posts
2. Select multiple posts

**Test:**
1. Use the Action dropdown to select **"Mark selected posts as inappropriate"**
2. Click **Go**
3. **Expected Result:** Selected posts should have `is_flagged_inappropriate = True`

**Reverse:**
1. Select flagged posts
2. Choose **"Clear inappropriate flag"**
3. **Expected Result:** Flag is cleared for those posts

---

## Quick Checklist

- [ ] User registration works normally
- [ ] Moderator flag is in user profile
- [ ] Non-moderators don't see moderation buttons
- [ ] Moderators see Flag, Edit, Remove buttons
- [ ] Flag action marks content as inappropriate
- [ ] Edit action clears inappropriate flag and updates content
- [ ] Remove action permanently deletes content
- [ ] Moderation notes are saved in database
- [ ] Admin panel shows is_flagged_inappropriate field
- [ ] Admin bulk actions work
- [ ] Non-moderators get 403 when trying to access moderation endpoints
- [ ] Moderation works for both posts AND comments

---

## Troubleshooting

### "No moderation buttons appear"
- Make sure you're logged in as a moderator
- Check Admin → Profiles to verify `is_moderator = True`
- Hard refresh browser (Ctrl+Shift+R)

### "403 Forbidden when clicking moderation buttons"
- User account doesn't have moderator flag
- Check the `is_moderator` field in Django Admin

### "Changes not saved"
- Check browser console for JavaScript errors
- Verify form has CSRF token (`{% csrf_token %}`)
- Check Django server logs

### "Page not found (404)"
- Make sure URL patterns in `forum/urls.py` match the template links
- Verify all moderation URL names are correct

---

## Database Check (Django Shell)

To verify data from command line:

```bash
python manage.py shell
```

```python
from users.models import Profile
from forum.models import Post, Comment

# Check moderators
Profile.objects.filter(is_moderator=True)

# Check flagged posts
Post.objects.filter(is_flagged_inappropriate=True)

# Check flagged comments
Comment.objects.filter(is_flagged_inappropriate=True)

# View moderation notes
post = Post.objects.get(pk=1)
print(post.moderation_note)
```

---

## Files to Review If Issues Occur

1. **Views:** `forum/views.py` - Check `is_moderator()` function
2. **URLs:** `forum/urls.py` - Verify URL patterns match
3. **Templates:** `forum/templates/forum/` - Check moderation buttons are rendering
4. **Models:** `forum/models.py`, `users/models.py` - Verify fields exist
5. **Admin:** `forum/admin.py` - Check admin interface configuration
