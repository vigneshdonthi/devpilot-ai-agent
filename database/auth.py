from database.supabase_client import supabase


# =========================================================
# REGISTER
# =========================================================

def register_user(email: str, password: str):

    try:

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        return {
            "success": True,
            "user": response.user,
            "session": response.session,
            "error": None,
        }

    except Exception as e:

        return {
            "success": False,
            "user": None,
            "session": None,
            "error": str(e),
        }


# =========================================================
# LOGIN
# =========================================================

def login_user(email: str, password: str):

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        return {
            "success": True,
            "user": response.user,
            "session": response.session,
            "error": None,
        }

    except Exception as e:

        return {
            "success": False,
            "user": None,
            "session": None,
            "error": str(e),
        }


# =========================================================
# LOGOUT
# =========================================================

def logout_user():

    try:

        supabase.auth.sign_out()

        return {
            "success": True,
            "error": None,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SEND PASSWORD RESET EMAIL
# =========================================================

def send_password_reset(email: str):

    try:

        supabase.auth.reset_password_for_email(
            email
        )

        return {
            "success": True,
            "error": None,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SET RECOVERY SESSION
# =========================================================

def set_recovery_session(access_token: str, refresh_token: str):

    try:
        response = supabase.auth.set_session(
            access_token,
            refresh_token,
        )

        return {
            "success": True,
            "user": response.user,
            "session": response.session,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "user": None,
            "session": None,
            "error": str(e),
        }


# =========================================================
# UPDATE PASSWORD
# =========================================================

def update_password(new_password: str):

    try:

        response = supabase.auth.update_user(
            {
                "password": new_password,
            }
        )

        return {
            "success": True,
            "user": response.user,
            "error": None,
        }

    except Exception as e:

        return {
            "success": False,
            "user": None,
            "error": str(e),
        }