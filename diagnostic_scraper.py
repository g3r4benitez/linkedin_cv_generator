"""Script de diagnóstico para generar un archivo HTML de ejemplo."""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "linkedin_cv_generator"))

from linkedin_cv_generator.src.scraper.linkedin_scraper import LinkedInScraper

def diagnostic_mode():
    """Modo diagnóstico para inspeccionar la estructura de LinkedIn."""
    print("Iniciando modo diagnóstico...")
    scraper = LinkedInScraper(headless=False)
    
    try:
        print("1. Se abrirá LinkedIn. Inicia sesión manualmente.")
        print("2. Navega a tu perfil.")
        print("3. Presiona Enter cuando estés listo para diagnosticar.")
        
        scraper.login_manual()
        
        # Navegar a un perfil de ejemplo
        profile_url = "https://www.linkedin.com/in/gerardobenitez/"
        scraper.driver.get(profile_url)
        import time
        time.sleep(5)
        
        # Diagnosticar selectores
        from selenium.webdriver.common.by import By
        
        print("\n=== DIAGNÓSTICO DE SELECTORES ===")
        
        # Nombre
        print("\nBuscando nombre...")
        selectors = [
            "h1.text-heading-xlarge",
            "h1.text-heading-large",
            "h1[class*='heading']",
            "h1",
            "*[data-control-name='profile_name']"
        ]
        for selector in selectors:
            try:
                element = scraper.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Nombre encontrado con '{selector}': {element.text[:50]}")
                break
            except:
                print(f"✗ No con '{selector}'")
        
        # Headline
        print("\nBuscando headline...")
        selectors = [
            "div.text-body-medium",
            "div[class*='headline']",
            ".text-body-medium",
            "h2[class*='headline']"
        ]
        for selector in selectors:
            try:
                element = scraper.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Headline encontrado con '{selector}': {element.text[:50]}")
                break
            except:
                print(f"✗ No con '{selector}'")
        
        # Todos los h1 y h2
        print("\nElementos h1 encontrados:")
        try:
            h1_elements = scraper.driver.find_elements(By.TAG_NAME, "h1")
            for i, elem in enumerate(h1_elements):
                print(f"  h1 #{i}: {elem.text[:50]} (class: {elem.get_attribute('class')})")
        except:
            print("  No se encontraron h1")
        
        print("\nElementos h2 con texto relevante:")
        try:
            h2_elements = scraper.driver.find_elements(By.TAG_NAME, "h2")
            for i, elem in enumerate(h2_elements[:10]):
                print(f"  h2 #{i}: {elem.text[:50]} (class: {elem.get_attribute('class')})")
        except:
            print("  No se encontraron h2")
        
        # Guardar HTML
        with open("assets/linkedin_structure.html", "w", encoding="utf-8") as f:
            f.write(scraper.driver.page_source)
        print("\nHTML completo guardado en assets/linkedin_structure.html")
        
        # Extraer con el scraper principal
        print("\n=== INTENTO DE EXTRACCIÓN CON SCRAPER PRINCIPAL ===")
        profile_data = scraper.extract_profile(profile_url)
        print(json.dumps(profile_data, indent=2, ensure_ascii=False))
        
    finally:
        scraper.close()

if __name__ == "__main__":
    import json
    from selenium.webdriver.common.by import By
    diagnostic_mode()