#!/usr/bin/env python3
"""Script de prueba para validar el setup inicial."""

import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

def test_imports():
    """Verifica que todas las dependencias críticas se importan correctamente."""
    print("Verificando dependencias...")
    
    try:
        import streamlit
        print("✓ Streamlit version:", streamlit.__version__)
    except ImportError as e:
        print("✗ Error importando Streamlit:", e)
        return False
    
    try:
        import selenium
        print("✓ Selenium version:", selenium.__version__)
    except ImportError as e:
        print("✗ Error importando Selenium:", e)
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ webdriver_manager importado correctamente")
    except ImportError as e:
        print("✗ Error importando webdriver_manager:", e)
        return False
    
    try:
        import langchain_community
        print("✓ Langchain Community version:", langchain_community.__version__)
    except ImportError as e:
        print("✗ Error importando Langchain:", e)
        return False
    
    try:
        import langchain_openai
        print("✓ Langchain OpenAI importado correctamente")
    except ImportError as e:
        print("✗ Error importando Langchain OpenAI:", e)
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ Python-dotenv importado correctamente")
    except ImportError as e:
        print("✗ Error importando dotenv:", e)
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup importado correctamente")
    except ImportError as e:
        print("✗ Error importando BeautifulSoup:", e)
        return False
    
    try:
        import openai
        print("✓ OpenAI SDK version:", openai.__version__)
    except ImportError as e:
        print("✗ Error importando OpenAI:", e)
        return False
    
    return True

def test_scraper_import():
    """Verifica que el módulo de scraper se puede importar."""
    print("\nVerificando importación de módulos...")
    
    # Test LinkedIn Scraper
    try:
        from scraper.linkedin_scraper import LinkedInScraper
        print("✓ LinkedInScraper importado correctamente")
    except Exception as e:
        print(f"✗ Error importando LinkedInScraper: {e}")
        return False
    
    # Test GitHub Extractor
    try:
        from data.github_extractor import GitHubExtractor
        print("✓ GitHubExtractor importado correctamente")
    except Exception as e:
        print(f"✗ Error importando GitHubExtractor: {e}")
        return False
    
    # Test LinkedIn PDF Parser
    try:
        from data.linkedin_pdf_parser import LinkedInPDFParser
        print("✓ LinkedInPDFParser importado correctamente")
    except Exception as e:
        print(f"✗ Error importando LinkedInPDFParser: {e}")
        return False
    
    # Test Resume Generator
    try:
        from ai.resume_generator import ResumeGenerator
        print("✓ ResumeGenerator importado correctamente")
    except Exception as e:
        print(f"✗ Error importando ResumeGenerator: {e}")
        return False
    
    return True

def test_directories():
    """Verifica que las carpetas necesarias existen."""
    print("\nVerificando estructura de archivos...")
    required_dirs = [
        "assets",
        "cvs_generados",
        "src/scraper",
        "src/ai",
        "src/templates"
    ]
    
    for dir_name in required_dirs:
        path = os.path.join(os.path.dirname(__file__), dir_name)
        if os.path.exists(path):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (no existe)")
            return False
    return True

def test_env_file():
    """Verifica que el archivo .env existe."""
    print("\nVerificando configuración...")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        print("✓ Archivo .env encontrado")
        return True
    else:
        print("⚠ Archivo .env no encontrado (necesario para credenciales)")
        return True  # No crítico, pero advertir

if __name__ == "__main__":
    print("=" * 50)
    print("PRUEBA DE SETUP INICIAL")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_scraper_import())
    results.append(test_directories())
    results.append(test_env_file())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("El entorno está listo para el proof-of-concept")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores arriba")
    print("=" * 50)