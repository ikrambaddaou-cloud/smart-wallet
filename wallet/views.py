from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
import calendar
from dateutil.relativedelta import relativedelta

# Imports pour les métriques de classification
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix

# Import de vos modèles locaux
from .models import Transaction

def get_ai_prediction(amount, day_of_week):
    # Logique de votre modèle (Ex: Random Forest / Linear Regression adapté)
    # Pour le test, on retourne une catégorie fictive basée sur le montant
    if float(amount) > 1000:
        return "Home Improvement"
    elif float(amount) > 100:
        return "Shopping"
    else:
        return "Fast Food"

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # 1. INITIALISATION DU SOLDE INITIAL (Session)
    if 'solde_initial' not in request.session:
        request.session['solde_initial'] = 5000.0

    # 2. GESTION DES REQUÊTES POST
    if request.method == 'POST':
        if 'update_balance' in request.POST:
            new_balance = request.POST.get('solde_initial')
            if new_balance:
                request.session['solde_initial'] = float(new_balance)
                request.session.modified = True
                request.session.save()
            return redirect('dashboard')

        amount_val = request.POST.get('amount')
        category_selected = request.POST.get('category')  # Catégorie choisie/corrigée
        if amount_val:
            current_day_of_week = timezone.now().weekday()
            # On obtient la prédiction pure de l'IA
            ai_predicted_cat = get_ai_prediction(amount_val, current_day_of_week)
            
            # Sauvegarde dans la base de données
            # Idéalement votre modèle stocke 'category' (réelle) et 'predicted_category'
            Transaction.objects.create(
                user=request.user,
                amount=float(amount_val),
                category=category_selected  # Ici on stocke la catégorie finale
            )
            return redirect('dashboard')
    
    # 3. LOGIQUE DE COMPARAISON MENSUELLE
    now = timezone.now()
    current_month_total = Transaction.objects.filter(
        user=request.user,
        timestamp__year=now.year,
        timestamp__month=now.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    last_month_date = now - relativedelta(months=1)
    last_month_total = Transaction.objects.filter(
        user=request.user,
        timestamp__year=last_month_date.year,
        timestamp__month=last_month_date.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    difference = float(current_month_total) - float(last_month_total)

    # 4. LOGIQUE IA : GESTION ET PROJECTION
    solde_initial = float(request.session['solde_initial'])
    solde_actuel = solde_initial - float(current_month_total)
    
    jours_dans_le_mois = calendar.monthrange(now.year, now.month)[1]
    jours_restants = jours_dans_le_mois - now.day
    jours_ecoules = now.day if now.day > 0 else 1
    
    depense_quotidienne_moyenne = float(current_month_total) / jours_ecoules
    solde_estime_fin_mois = solde_actuel - (depense_quotidienne_moyenne * jours_restants)
    
    if solde_estime_fin_mois < 0:
        ai_balance_status = "Alerte Découvert : Votre rythme de dépense actuel dépasse votre solde disponible avant la fin du mois !"
        status_color = "danger"
    elif solde_estime_fin_mois < (solde_initial * 0.15):
        ai_balance_status = "Attention Budgétaire : Le solde prédictif de fin de mois est critique. Limitez les dépenses non-essentielles."
        status_color = "warning"
    else:
        ai_balance_status = "Santé Financière Excellente : Vos flux sont stables et votre solde est optimisé pour ce cycle."
        status_color = "success"

    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')

    # 5. CALCUL DE L'ACCURACY ET MATRICE DE CONFUSION (Simulation IA)
    # Pour générer une vraie évaluation, nous comparons la catégorie de la transaction
    # avec ce que l'IA aurait prédit à la volée pour cette même transaction.
    y_true = []
    y_pred = []
    
    for tx in transactions:
        # On simule la prédiction que l'IA aurait faite sur ce montant
        simulated_pred = get_ai_prediction(tx.amount, tx.timestamp.weekday())
        y_true.append(tx.category)
        y_pred.append(simulated_pred)

    # Valeurs par défaut si pas assez de données
    accuracy_pct = 0.0
    matrix_data = []
    labels_list = []

    if len(y_true) > 0:
        # Calcul de la précision
        accuracy_pct = accuracy_score(y_true, y_pred) * 100
        
        # Liste des catégories uniques présentes pour aligner la matrice
        labels_list = sorted(list(set(y_true + y_pred)))
        
        # Calcul de la matrice de confusion brute
        raw_matrix = confusion_matrix(y_true, y_pred, labels=labels_list)
        
        # Structuration pour faciliter l'affichage en tableau HTML (Ligne par Ligne)
        for i, row in enumerate(raw_matrix):
            matrix_data.append({
                'label': labels_list[i],
                'values': row.tolist()
            })

    context = {
        'transactions': transactions,
        'current_month_total': round(float(current_month_total), 2),
        'last_month_total': round(float(last_month_total), 2),
        'difference': round(difference, 2),
        'solde_initial': round(solde_initial, 2),
        'solde_actuel': round(solde_actuel, 2),
        'solde_estime_fin_mois': round(solde_estime_fin_mois, 2),
        'ai_balance_status': ai_balance_status,
        'status_color': status_color,
        
        # Nouvelles variables pour le template
        'accuracy': round(accuracy_pct, 2),
        'matrix_data': matrix_data,
        'matrix_labels': labels_list,
    }
    
    return render(request, 'wallet/dashboard.html', context)

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'