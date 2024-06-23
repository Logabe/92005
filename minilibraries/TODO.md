# TODO
1. Setup project using `django-admin` and `manage.py`
2. Create Basic HTML template/scaffold
  1. Create index and home pages (home will be shown to logged in users)
  2. Some basic styling (more can be added as we go)
3. Create data representations ('models') of the basic types
  - Book
  - Library
  - User (provided by Django)
  - Membership
  - Request for a book
4. Create book registration form or page
  1. Create an HTML form that asks for a book's ISBN
  2. Take HTTP POST form data and turn that into a Book model.
    1. Get ISBN from form data
    2. Send HTTP request for that book to OpenLibrary API
    3. Use ISBN from form, OLID, Title from request and User to create a Book object and save it to the database.
  3. Add some books to the database for testing
5. Create book listing page
  1. Use CSS Grid to layout books
  2. Query DB for the Title, OLID and internal ID of each book the user has access to.
  3. Use OpenLibrary Cover API to get book covers
6. Create book details page
  1. Get title and OLID from database
  2. Use OLID to get cover, summary
7. Create user login/registration page
8. Implement borrowing system
-- VVV HERE VVV --
9. Create proper home page
  1. Use CSS Grid to create page layout
  2. Use Flexbox to make book rows
10. Finalise website templates & CSS design (make it look nice)
  1. Create index page (not home)
11. Test, Test, Test - Break EVERYTHING while you can

OPTIONAL COOL STUFF:
12. Add search to book listing page