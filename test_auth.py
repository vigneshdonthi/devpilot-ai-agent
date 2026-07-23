from database.auth import login_user


email = input("Email: ")
password = input("Password: ")

result = login_user(email, password)


if result["success"]:

    print("Login successful!")

    print(
        "User ID:",
        result["user"].id
    )

    print(
        "Email:",
        result["user"].email
    )

else:

    print(
        "Login failed:",
        result["error"]
    )