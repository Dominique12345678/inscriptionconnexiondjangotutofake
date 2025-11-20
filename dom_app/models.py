# dom_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# --- 1. Le Gestionnaire d'Utilisateurs (UserManager) ---
class UtilisateurManager(BaseUserManager):
    """Gère la création des utilisateurs."""
    
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('Le nom d\'utilisateur est requis.')
        if not email:
            raise ValueError('L\'adresse email est requise.')
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        
        # Hache et définit le mot de passe
        user.set_password(password)
        user.save(using=self._db)
        return user

    # La fonction create_superuser est désormais supprimée !
    # Si vous en avez besoin plus tard, vous devrez la réintégrer.

# --- 2. Le Modèle Utilisateur Personnalisé ---
class Utilisateur(AbstractBaseUser):
   
    
    # Champs d'authentification principaux
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    
    # Champ d'état minimal requis par AbstractBaseUser
    is_active = models.BooleanField(default=True)
    
    # Configuration du modèle
    objects = UtilisateurManager()

    # Le champ utilisé pour se connecter
    USERNAME_FIELD = 'username'
    # Aucun REQUIRED_FIELDS nécessaire pour cette configuration simplifiée
    REQUIRED_FIELDS = ['email'] # Gardons 'email' pour la cohérence, mais il n'est pas utilisé sans create_superuser

    def __str__(self):
        return self.username