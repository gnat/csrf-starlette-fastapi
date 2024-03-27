import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

class CSRFMiddleware(BaseHTTPMiddleware):
	"""
	CSRF / Cross Site Request Forgery Security Middleware for Starlette and FastAPI.
		1. Add this middleware using the middleware= parameter of your app.
		2. request.state.csrftoken will now be available.
		3. Use directly in an HTML <form> POST with <input type="hidden" name="csrftoken" value="{{ csrftoken }}" />
		4. Use with javascript / ajax POST by sending a request header 'csrftoken' with request.state.csrftoken
	Notes
		Users must should start on a "safe page" (a typical GET request) to generate the initial CSRF cookie.
		Uses session level CSRF so you can use frameworks such as htmx, without issues. (https://htmx.org/)
		Token is stored in request.state.csrftoken for use in templates.
	Reference
		https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
	"""
	async def dispatch(self, request, call_next):
		CSRF_TOKEN_NAME = 'csrftoken'
		CSRF_TOKEN_EXPIRY = 10 * 24 * 60 * 60 # Valid for 10 days before regeneration.
		request.state.csrftoken = '' # Always available even if we don't get it from cookie.

		token_from_post = False
		token_new_cookie = False
		token_from_cookie = request.cookies.get(CSRF_TOKEN_NAME, None)
		token_from_header = request.headers.get(CSRF_TOKEN_NAME, None)
		if hasattr(request.state, "post"):
			token_from_post = request.state.post.get(CSRF_TOKEN_NAME, None)

		# 🍪 Fetch the cookie only if we're using an appropriate request method (like Django does).
		if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
			if not token_from_cookie or len(token_from_cookie) < 30: # Sanity check. UUID always > 30.
				return PlainTextResponse("No CSRF cookie set!", status_code=403) # 🔴 Fail check.
			if (str(token_from_cookie) != str(token_from_post)) and (str(token_from_cookie) != str(token_from_header)):
				return PlainTextResponse("CSRF cookie does not match!", status_code=403) # 🔴 Fail check.
		else:
			# 🍪 Generates the cookie if one does not exist.
			# Has to be the same token throughout session! NOT a nonce.
			# 	"if you record a nonce value everytime I load a form and then I can't go back to a different tab and submit that first form I will dislike your site."
			if not token_from_cookie:
				token_from_cookie = str(uuid.uuid4())
				token_new_cookie = True

		# 🟢 All good. Pass csrftoken up to controllers, templates.
		request.state.csrftoken = token_from_cookie

		# ⏰ Wait for response to happen.
		response = await call_next(request)

		# 🍪 Set CSRF cookie on the response.
		if token_new_cookie and token_from_cookie:
			response.set_cookie(CSRF_TOKEN_NAME, token_from_cookie, CSRF_TOKEN_EXPIRY, path='/', domain=None, secure=False, httponly=False, samesite='strict')

		return response
