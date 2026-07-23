from database.supabase_client import supabase


# =========================================================
# CREATE CHAT
# =========================================================

def create_chat(user_id, title="New Chat", mode="Agent"):

    try:
        response = (
            supabase
            .table("chats")
            .insert({
                "user_id": user_id,
                "title": title,
                "mode": mode,
            })
            .execute()
        )

        return response.data[0]

    except Exception as e:
        print("Create chat error:", e)
        return None


# =========================================================
# GET USER CHATS
# =========================================================

def get_user_chats(user_id):

    try:
        response = (
            supabase
            .table("chats")
            .select("*")
            .eq("user_id", user_id)
            .order(
                "updated_at",
                desc=True,
            )
            .execute()
        )

        return response.data

    except Exception as e:
        print("Get chats error:", e)
        return []


# =========================================================
# SAVE MESSAGE
# =========================================================

def save_message(chat_id, role, content):

    try:
        response = (
            supabase
            .table("messages")
            .insert({
                "chat_id": chat_id,
                "role": role,
                "content": content,
            })
            .execute()
        )

        return response.data[0]

    except Exception as e:
        print("Save message error:", e)
        return None


# =========================================================
# GET CHAT MESSAGES
# =========================================================

def get_chat_messages(chat_id):

    try:
        response = (
            supabase
            .table("messages")
            .select("*")
            .eq("chat_id", chat_id)
            .order(
                "created_at",
                desc=False,
            )
            .execute()
        )

        return response.data

    except Exception as e:
        print("Get messages error:", e)
        return []


# =========================================================
# UPDATE CHAT TITLE
# =========================================================

def update_chat_title(chat_id, title):

    try:
        response = (
            supabase
            .table("chats")
            .update({
                "title": title,
            })
            .eq("id", chat_id)
            .execute()
        )

        return response.data

    except Exception as e:
        print("Update title error:", e)
        return None


# =========================================================
# UPDATE CHAT MODE
# =========================================================

def update_chat_mode(chat_id, mode):

    try:
        response = (
            supabase
            .table("chats")
            .update({
                "mode": mode,
            })
            .eq("id", chat_id)
            .execute()
        )

        return response.data

    except Exception as e:
        print("Update mode error:", e)
        return None


# =========================================================
# DELETE CHAT
# =========================================================

def delete_chat_from_db(chat_id):

    try:
        (
            supabase
            .table("chats")
            .delete()
            .eq("id", chat_id)
            .execute()
        )

        return True

    except Exception as e:
        print("Delete chat error:", e)
        return False