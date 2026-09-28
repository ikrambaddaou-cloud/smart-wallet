from django.contrib import admin
from django.urls import path, include
from wallet.views import SignUpView  # Importez la vue ici


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wallet.urls')), # Votre dashboard
    path('accounts/signup/', SignUpView.as_view(), name='signup'), # AJOUTEZ CETTE LIGNE
    path('accounts/', include('django.contrib.auth.urls')),
]