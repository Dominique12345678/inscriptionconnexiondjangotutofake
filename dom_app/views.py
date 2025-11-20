# dom_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Utilisateur 
from django.conf import settings # Nous pourrions en avoir besoin si on gère la durée de session

# --- VUE D'INSCRIPTION (Identique à la version précédente, car elle est déjà manuelle) ---
def inscription(request):
    if request.method == 'POST':
        # Récupération manuelle des données
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        errors = {} 

        # Validation de base et vérification des erreurs 1 par 1
        if not username: errors['username'] = "Le nom d'utilisateur est obligatoire."
        if not email: errors['email'] = "L'email est obligatoire."
        if not password: errors['password'] = "Le mot de passe est obligatoire."
        if not password_confirm: errors['password_confirm'] = "La confirmation du mot de passe est obligatoire."

        if password and password_confirm and password != password_confirm:
            errors['password_confirm'] = "Les deux mots de passe ne correspondent pas."

        if username and Utilisateur.objects.filter(username=username).exists():
            errors['username'] = "Ce nom d'utilisateur est déjà utilisé."

        if email and Utilisateur.objects.filter(email=email).exists():
            errors['email'] = "Cet email est déjà associé à un compte."
        
        # Création de l'utilisateur
        if not errors:
            try:
                Utilisateur.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, 'Inscription réussie ! Vous pouvez maintenant vous connecter.')
                return redirect('connexion')  
            except Exception as e:
                messages.error(request, f"Une erreur inattendue est survenue lors de l'enregistrement : {e}")
        else:
            for field, error_message in errors.items():
                messages.error(request, f"{field.capitalize()}: {error_message}")
    
    return render(request, 'inscription.html')

# --- VUE DE CONNEXION SANS AUTHENTICATE NI LOGIN ---
def connexion(request):
    # Si l'utilisateur est déjà "connecté" via notre session manuelle
    # Note : request.user.is_authenticated ne fonctionne plus, nous vérifions la session
    if request.session.get('user_id'): 
        return redirect('accueil')

    if request.method == 'POST':
        # Récupération manuelle des données
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        errors = {} 
        user_match = None

        # ERREUR 1: Champs vides
        if not username or not password:
            errors['general'] = "Veuillez entrer votre nom d'utilisateur et votre mot de passe."

        # Si les champs ne sont pas vides, on continue les vérifications
        if not errors:
            try:
                # 1. Tenter de récupérer l'utilisateur
                user_match = Utilisateur.objects.get(username=username)
            except Utilisateur.DoesNotExist:
                # ERREUR 2: Utilisateur non trouvé
                errors['username'] = "Nom d'utilisateur ou mot de passe incorrect."
            
            # Si l'utilisateur est trouvé
            if user_match:
                # 2. Vérifier le mot de passe manuellement (utilise le hachage)
                # Cette méthode est fournie par AbstractBaseUser
                if not user_match.check_password(password):
                    # ERREUR 3: Mot de passe incorrect
                    errors['password'] = "Nom d'utilisateur ou mot de passe incorrect."

        # --- PROCESSUS DE CONNEXION MANUELLE ---
        if not errors and user_match:
            # Succès : Définir la session manuellement (équivalent de login)
            request.session['user_id'] = user_match.id
            messages.success(request, f'Bienvenue, {user_match.username} !')
            return redirect('accueil')
        else:
            # Échec : Afficher l'erreur la plus pertinente
            for field, error_message in errors.items():
                messages.error(request, f"{error_message}") # Afficher l'erreur générale ou spécifique
                
    return render(request, 'connexion.html')

# Dans n'importe quelle vue protégée (par exemple 'accueil')
def accueil(request):
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')
        
    try:
        current_user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        # L'utilisateur de la session n'existe plus (cas rare)
        return redirect('deconnexion')

    # Maintenant, vous utilisez current_user dans votre contexte
    context = {'user': current_user, 'message': f'Contenu réservé à {current_user.username}'}
    return render(request, 'accueil.html', context)

# dom_app/views.py (à ajouter à la fin de vos autres vues)
# ... code des vues inscription et connexion ...

# --- VUE DE DÉCONNEXION MANUELLE ---
def deconnexion(request):
    """
    Déconnecte l'utilisateur en supprimant manuellement l'ID de l'utilisateur
    de la session.
    """
    # 1. Vérifie si la clé 'user_id' existe dans la session
    if 'user_id' in request.session:
        # 2. Supprime la clé de la session
        del request.session['user_id']
    
    # 3. Supprime la session entière (bonne pratique de sécurité)
    # Bien que l'ID de l'utilisateur soit supprimé, on peut purger le reste.
    request.session.flush()
    
    # 4. Envoie un message de confirmation
    messages.info(request, "Vous êtes maintenant déconnecté. À bientôt !")
    
    # 5. Redirige l'utilisateur vers la page de connexion
    return redirect('connexion')