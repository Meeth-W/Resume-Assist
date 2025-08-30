# Resume Assist API - Endpoints Documentation

## Base URL
    http://localhost:5005

## Authentication Routes (`/auth`)

  ------------------------------------------------------------------------------------
  Method   Endpoint         Description      Request Body (JSON)
  -------- ---------------- ---------------- -----------------------------------------
  POST     /auth/register   Register a new   { "username": "john123", "password":
                            user             "pass123", "name": "John Doe", "email":
                                             "john@mail.com", "phone": "1234567890" }

  POST     /auth/login      Login and get    { "username": "john123", "password":
                            JWT token        "pass123" }

  PUT      /auth/update     Update user      { "token": "JWT_TOKEN", "name": "John
                            details (except  Smith", "email": "new@mail.com", "phone":
                            username)        "9876543210" }

  DELETE   /auth/delete     Delete user      { "token": "JWT_TOKEN" }
                            account          
  ------------------------------------------------------------------------------------

## Root Route

------------------------------------------------------------------------
  Method   Endpoint   Description
  -------- ---------- -----------------------------
  GET      /          Returns welcome + ping time

------------------------------------------------------------------------

## Notes

-   **JWT Token** is required for updating and deleting accounts.
-   `username` is unique and cannot be changed after registration.
-   Passwords are stored using **Argon2** hashing for security.
