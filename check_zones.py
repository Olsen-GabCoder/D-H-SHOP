#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import ShippingZone, ShippingRate
from accounts.models import Address

def check_zones_and_addresses():
    print("=== DIAGNOSTIC ZONES DE LIVRAISON ===")
    
    # Vérifier toutes les zones actives
    active_zones = ShippingZone.objects.filter(is_active=True)
    print(f"\n📦 Zones actives ({active_zones.count()}) :")
    
    for zone in active_zones:
        print(f"\nZone: {zone.name}")
        print(f"Villes couvertes: {zone.covered_cities}")
        
        # Tarifs associés
        rates = zone.rates.filter(is_active=True)
        for rate in rates:
            print(f"  - Tarif {rate.id}: {rate.get_delivery_type_display()} - {rate.cost} FCFA")
    
    # Vérifier les adresses existantes
    print(f"\n🏠 Adresses enregistrées :")
    addresses = Address.objects.all()
    for addr in addresses:
        print(f"ID {addr.id}: {addr.full_name} - {addr.city} (Code: {addr.postal_code})")
        
        # Vérifier la couverture
        covered = False
        for zone in active_zones:
            if zone.is_city_covered(addr.city):
                covered = True
                print(f"  ✅ Couverte par: {zone.name}")
                break
        
        if not covered:
            print(f"  ❌ NON COUVERTE par aucune zone active!")

if __name__ == "__main__":
    check_zones_and_addresses()