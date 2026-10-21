#!/usr/bin/env python3
"""Test básico de inicialización del scraper."""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

def test_scraper_initialization():
    """Test básico de inicialización del scraper."""
    print("Inicializando LinkedInScraper (modo headless)...")
    from scraper.linkedin_scraper import LinkedInScraper
    
    try:
        scraper = LinkedInScraper(headless=True)
        print("✓ Scraper inicializado correctamente")
        
        # Navegar a LinkedIn para test
        scraper.driver.get("https://www.linkedin.com")
        print("✓ Navegador abierto correctamente")
        
        scraper.close()
        print("✓ Navegador cerrado correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEST BÁSICO DE SCRAPER")
    print("=" * 50)
    success = test_scraper_initialization()
    print("=" * 50)
    if success:
        print("✅ TEST PASÓ")
    else:
        print("❌ TEST FALLÓ")
    print("=" * 50)