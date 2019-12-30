import pytest
from app import mail

def test_register(setUp, populate_db):
    with mail.record_messages() as outbox:
        """
        GIVEN an already registred user
        WHEN some one tries to use the same username and/or email
        THEN error messages are prompt to ask user to choose differents logins
        """
        response = setUp.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Congratulations" not in response.data
        assert "Merci d&#39;utiliser un pseudo différent." in response.data.decode("utf-8")
        assert "Merci d&#39;utiliser un email différent." in response.data.decode("utf-8")

        """
        GIVEN a never used email and username
        WHEN user fill the registration form
        THEN a message appear on the GUI and an email is sent
        """
        response = setUp.post('/auth/register', data={
            'email': 'donald@example.com',
            'username': 'donald',
            'password': 'duck',
            'password2': 'duck'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Un mail de confirmation vous a été envoyé." in response.data.decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].subject == "[ITORA] Confirmation du compte"


def test_confirmation(setUp, populate_db, new_users):
    """
    GIVEN a non confirmed user
    WHEN he tries to access to aunauthorized pages
    THEN he is routed to unconfirmed page
    """
    response = setUp.post('/auth/login', data={
        'username': 'mary',
        'password': 'fox'
    }, follow_redirects=True)
    response = setUp.get('/managepost', follow_redirects=True)
    assert response.status_code == 200
    print(response.data.decode("utf-8"))
    assert "Vous n'avez pas encore confirmer votre compte." in response.data.decode("utf-8")
    response = setUp.get('/edit_profile', follow_redirects=True)
    assert response.status_code == 200
    assert "Vous n'avez pas encore confirmer votre compte." in response.data.decode("utf-8")

    """
    GIVEN a new registred user
    WHEN he's using a false token
    THEN an error message is displayed
    """
    response = setUp.get('/auth/confirm/falseToken', follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation est invalide ou a expiré." in response.data.decode("utf-8")
    response = setUp.get('/managepost', follow_redirects=True)
    assert response.status_code == 200
    assert b"Bonjour mary, vous souhaitez :" not in response.data
    
    """
    GIVEN a new registred user
    WHEN he confirms his email adress
    THEN he can access to unauthorized pages
    """
    u1, u2, u3, u4 = new_users
    token3 = u3.get_confirm_token()
    response = setUp.get('/auth/confirm/'+token3, follow_redirects=True)
    assert response.status_code == 200
    assert "Vous avez confirmé votre compte. Merci !" in response.data.decode("utf-8")
    response = setUp.get('/managepost', follow_redirects=True)
    assert response.status_code == 200
    assert b"Bonjour mary" in response.data


def test_login(setUp, populate_db):
    """
    GIVEN an unknown username or false password
    WHEN user tries to login
    THEN an error message appear
    """
    response = setUp.post('/auth/login', data={
        'username': 'donald',
        'password': 'duck'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Pseudo ou mot de passe incorrect" in response.data
    assert b"Profile" not in response.data

    """
    GIVEN a registred user
    WHEN he tries to login with correct identifiers
    THEN he is correctly logged in
    """
    response = setUp.post('/auth/login', data={
        'username': 'john',
        'password': 'cat'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"login" not in response.data
    assert b"Messages" in response.data

    """
    GIVEN a logged user
    WHEN he tries to logout
    THEN he is correctly logged out
    """
    response = setUp.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"logout" not in response.data


def test_reset_password(setUp, populate_db):
    with mail.record_messages() as outbox:
        """
        GIVEN a non stored email
        WHEN it's used to reset a password
        THEN an error message appear
        """
        response = setUp.post('/auth/reset_password_request', data={
            'email': 'donald@example.com'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Cet email est inconnu. Merci d&#39;utiliser l&#39;email avec lequel tu t&#39;es enregistré." in response.data.decode("utf-8")

        """
        GIVEN a stored email
        WHEN it's used to reset a password
        THEN an email with instructions is sent
        """
        response = setUp.post('/auth/reset_password_request', data={
            'email': 'john@example.com'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "Vérifiez vos emails pour réinitialiser le mot de passe" in response.data.decode("utf-8")
        assert len(outbox) == 1
        assert outbox[0].subject == "[ITORA] Réinitialisation du mot de passe"