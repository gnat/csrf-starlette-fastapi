# csrf-starlette-fastapi
Dead simple CSRF security middleware for Starlette ⭐ and Fast API ⚡

* Will work with either a `<input type="hidden">` field or ajax request headers, interchangeably.
* Uses stateless [Double Submit Cookie](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#double-submit-cookie) method, like Django.
* Tiny, easy to audit.

### Install

1. Add `csrf_middleware.py` to your project `/middleware` folder.
2. Import `from app.middleware.csrf_middleware import CSRFMiddleware`.
3. Add Middleware to Starlette or FastAPI `app = Starlette(routes=routes, middleware=[Middleware(CSRFMiddleware)])`

### Usage

1. Pass `request.state.csrftoken` to your template engine (such as jinja2).
    1. Use it directly in HTML `<input type="hidden" name="csrftoken" value="{{ csrftoken }}" />`
    2. Use it in a request header named 'csrftoken' (for javascript / ajax frameworks such as [htmx](https://htmx.org/))

### Why?

To make available something more simple and auditable than the typical libraries for this as of 2022:
* https://github.com/simonw/asgi-csrf
* https://github.com/frankie567/starlette-csrf
* https://github.com/piccolo-orm/piccolo_api/blob/master/piccolo_api/csrf/middleware.py 
