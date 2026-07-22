# Evaluation Results

**Average function score:** 0.95

**Average file score:** 0.75

---

## Q1: How does the app notify users when their trial is ending?

**Answer:**
The app notifies users when their trial is ending by sending them an email. This is handled by the `send_trial_end_soon_email` function in the `email_utils.py` file.

**Function score:** 0.50 (found: ['send_trial_end_soon_email'])

**File score:** 0.50 (found: ['email_utils.py'])

---

## Q2: What functions call send_trial_end_soon_email?

**Answer:**
The notify_trial_end function in storage/cloned_repos/app\\cron.py calls send_trial_end_soon_email.

**Function score:** 1.00 (found: ['notify_trial_end'])

**File score:** 1.00 (found: ['cron.py'])

---

## Q3: How does the app notify users when their premium subscription is ending?

**Answer:**
The app notifies users when their premium subscription is ending by sending them an email.

The notify_premium_end function in the storage/cloned_repos/app\\cron.py file is used to send an email to users who have canceled their subscription and whose subscription is ending soon.

The notify_manual_sub_end function in the storage/cloned_repos/app\\cron.py file is used to remind users that their manual subscription is ending soon.

The apple_update_notification function in the storage/cloned_repos/app\\app\\api\\views\\apple.py file is used to receive update notifications from Apple.

The get_active_subscription_end function in the storage/cloned_repos/app\\app\\models.py file is used to get the end date for any subscription type.

The subscription_end_date function in the storage/cloned_repos/app\\app\\admin\\email_search.py file is used to get the end date for any subscription type.

**Function score:** 1.00 (found: ['notify_premium_end'])

**File score:** 1.00 (found: ['cron.py'])

---

## Q4: How can an admin manually extend a user's trial?

**Answer:**
The extend_trial_1w function in the storage/cloned_repos/app\\app\\admin\\user.py file can be used to extend a user's trial by one week.

```python
def extend_trial_1w(self, ids):
    for user in User.filter(User.id.in_(ids)):
        if user.trial_end and user.trial_end > arrow.now():
            user.trial_end = user.trial_end.shift(weeks=1)
        else:
            user.trial_end = arrow.now().shift(weeks=1)

        flash(f"Extend trial for {user} to {user.trial_end}", "success")
        AdminAuditLog.extend_trial(
            current_user.id, user.id, user.trial_end, "1 week"
        )

    Session.commit()
```

The extend_trial function in the storage/cloned_repos/app\\app\\models.py file can be used to extend a user's trial by a specified time.

```python
def extend_trial(
    cls, admin_user_id: int, user_id: int, trial_end: arrow.Arrow, extend_time: str
):
    cls.create(
        admin_user_id=admin_user_id,
        action=AuditLogActionEnum.extend_trial.value,
        model="User",
        model_id=user_id,
        data={
            "trial_end": trial_end.format(arrow.FORMAT_RFC3339),
            "extend_time": extend_time,
        },
    )
```

**Function score:** 1.00 (found: ['extend_trial_1w'])

**File score:** 1.00 (found: ['user.py'])

---

## Q5: How can an admin stop a user's trial?

**Answer:**
An admin can stop a user's trial by using the stop_trial function, which can be found in the following files:
- storage/cloned_repos/app\\app\\admin\\user.py
- storage/cloned_repos/app\\app\\models.py

**Function score:** 1.00 (found: ['stop_trial'])

**File score:** 1.00 (found: ['user.py'])

---

## Q6: How does the app authenticate API requests?

**Answer:**
The app authenticates API requests using the authorize_request function, which can be found in the file storage/cloned_repos/app\\app\\api\\base.py from lines 18 to 45.

The function works by first retrieving the API code from the request headers. It then checks if the API key is valid. If the API key is not valid, the function checks if the current user is authenticated. If the current user is authenticated, the function sets the user in the global context. If the current user is not authenticated, the function returns an error message.

If the API key is valid, the function updates the API key stats and sets the user in the global context. The function then checks if the user is disabled or not active. If the user is disabled or not active, the function returns an error message. If the user is active, the function sets the API key in the global context and returns None.

The require_api_auth function is a decorator that calls the authorize_request function and returns the result of the decorated function if the authorization is successful. This function can also be found in the file storage/cloned_repos/app\\app\\api\\base.py from lines 54 to 62.

**Function score:** 1.00 (found: ['authorize_request'])

**File score:** 1.00 (found: ['base.py'])

---

## Q7: What is sudo mode and how does the app check if it is currently active for a request?

**Answer:**
Sudo mode is a mode that can be entered by a user, validating their password, and exited by the same user.

The app checks if sudo mode is active for a request by calling the check_sudo_mode_is_active function, which can be found in the file storage/cloned_repos/app\\app\\api\\base.py.

The app also checks if sudo mode is active for a session by calling the check_session_sudo_mode_is_active function, which can be found in the file storage/cloned_repos/app\\app\\api\\base.py.

**Function score:** 1.00 (found: ['check_sudo_mode_is_active', 'check_session_sudo_mode_is_active'])

**File score:** 1.00 (found: ['base.py'])

---

## Q8: What happens when an API request is made without a valid API key or session?

**Answer:**
If an API request is made without a valid API key or session, the authorize_request function in the file storage/cloned_repos/app\\app\\api\\base.py will return a JSON response with an error message "Wrong api key" and a status code of 401.

Here's the relevant code snippet:

```python
def authorize_request() -> Optional[Tuple[str, int]]:
    api_code = request.headers.get("Authentication")
    api_key = ApiKey.get_by(code=api_code)

    if not api_key:
        if current_user.is_authenticated:
            if current_user.is_authenticated and request.headers.get(
                constants.HEADER_ALLOW_API_COOKIES
            ):
                g.user = current_user
        else:
            return jsonify(error="Wrong api key"), 401
```

This function checks if a valid API key is provided in the request headers. If not, it checks if the current user is authenticated. If neither condition is met, it returns the error response.

**Function score:** 1.00 (found: ['authorize_request'])

**File score:** 1.00 (found: ['base.py'])

---

## Q9: How does the app search for custom domains by user email, domain ID, or regex?

**Answer:**
The app searches for custom domains by user email, domain ID, or regex in the CustomDomainSearchResult class in the file storage/cloned_repos/app\\app\\admin\\custom_domain_search.py.

The search function in this class takes a query string as input and returns a CustomDomainSearchResult object. The function first checks if the query is a numeric query (i.e., a plain integer) and if so, it searches for a custom domain by domain ID. If the query contains an '@' symbol, it searches for a custom domain by user email. If the query has the form 'uid:<int>', it searches for a custom domain by user ID. If none of these conditions are met, it tries an exact domain match first, and if that fails, it tries a regex search on domain names.

Here's a breakdown of the search logic:

1. **Search by domain ID**: If the query is a plain integer, it's treated as a domain ID.
2. **Search by user email**: If the query contains an '@' symbol, it's treated as a user email.
3. **Search by user ID**: If the query has the form 'uid:<int>', it's treated as a user ID.
4. **Exact domain match**: If none of the above conditions are met, it tries to match the query exactly to a domain name.
5. **Regex search**: If the exact domain match fails, it tries a regex search on domain names.

The function uses the CustomDomain class to interact with the database and retrieve custom domain information. It also uses the CustomDomainSearchHelpers class to get validation data for custom domains.

The is_safe_regex_pattern function is used to validate regex patterns and prevent ReDoS (Regular Expression Denial of Service) attacks.

The search function returns a CustomDomainSearchResult object, which contains the following attributes:

* no_match: a boolean indicating whether a match was found
* query: the original query string
* domains: a list of custom domains that match the query
* found_by_regex: a boolean indicating whether the match was found using regex

**Function score:** 1.00 (found: ['search'])

**File score:** 0.00 (found: [])

---

## Q10: What happens when an admin deletes a custom domain?

**Answer:**
When an admin deletes a custom domain, the domain is scheduled for deletion and the deletion is logged. The domain is then deleted and the user is notified via email.

The relevant code is in the following files:
- storage/cloned_repos/app\\app\\custom_domain_utils.py
- storage/cloned_repos/app\\app\\admin\\custom_domain_search.py
- storage/cloned_repos/app\\tasks\\delete_custom_domain_job.py

**Function score:** 1.00 (found: ['delete_custom_domain'])

**File score:** 0.00 (found: [])

---

