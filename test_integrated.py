#!/usr/bin/env python3
"""Test integrado completo para validar todo el flujo del sistema."""
import os
import sys
import json
import tempfile

sys.path.append(os.path.dirname(__file__))

def test_complete_flow():
    """Test completo del flujo: PDF → Parseo → Generación CV."""
    print("=" * 60)
    print("TEST INTEGRADO COMPLETO")
    print("=" * 60)
    
    results = {
        "pdf_parsing": False,
        "github_available": False,
        "resume_generation": False,
        "pdf_generation": False,
        "web_ui_ready": False
    }
    
    # Test 1: Parser de PDF de LinkedIn
    print("\n1. 🧪 Probando parser de PDF de LinkedIn...")
    try:
        from src.data.linkedin_pdf_parser import LinkedInPDFParser
        
        pdf_path = "/home/gerardo/projects/curriculum_custom/data/gerardobenittez_profile_linkedin.pdf"
        
        if os.path.exists(pdf_path):
            parser = LinkedInPDFParser(pdf_path)
            profile_data = parser.parse()
            
            # Guardar datos parseados
            parser.save_json("test_linkedin_profile.json")
            
            # Verificar datos extraídos
            assert profile_data["name"], "No se extrajo el nombre"
            assert profile_data["headline"], "No se extrajo el headline"
            assert len(profile_data["skills"]) > 0, "No se extrajeron habilidades"
            assert len(profile_data["experience"]) > 0, "No se extrajo experiencia"
            
            print(f"   ✅ Nombre: {profile_data['name']}")
            print(f"   ✅ Headline: {profile_data['headline'][:50]}...")
            print(f"   ✅ Skills: {len(profile_data['skills'])} encontradas")
            print(f"   ✅ Experiencia: {len(profile_data['experience'])} trabajos")
            
            results["pdf_parsing"] = True
        else:
            print(f"   ⚠️ PDF no encontrado: {pdf_path}")
            print("   ℹ️ Saltando test de PDF")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Verificar extractor de GitHub
    print("\n2. 🧪 Verificando extractor de GitHub...")
    try:
        from src.data.github_extractor import GitHubExtractor
        print("   ✅ GitHubExtractor importado correctamente")
        results["github_available"] = True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Generador de CV
    print("\n3. 🧪 Probando generador de CV...")
    try:
        from src.ai.resume_generator import ResumeGenerator
        
        # Datos de prueba basados en el PDF parseado
        test_profile = {
            "name": "Gerardo Benitez",
            "headline": "AI Engineer | Full Stack Developer",
            "contact_info": {
                "email": "gerardobenitez@gmail.com",
                "phone": "+541123990625"
            },
            "summary": "Backend Developer 9+ years building scalable distributed systems",
            "skills": ["Python", "FastAPI", "Docker", "AWS", "Node.js", "Kafka", "RabbitMQ"],
            "experience": [
                {
                    "title": "Back End Developer",
                    "company": "FORWARD Platform",
                    "dates": "May 2022 - Present",
                    "description": "Payment ecosystem with PayPal integration"
                }
            ],
            "education": [
                {
                    "institution": "Universidad Nacional de La Matanza",
                    "degree": "Ingenieria en informática",
                    "dates": "2015 - 2018"
                }
            ],
            "languages": ["Spanish (Native)", "English (Full Professional)"],
            "github_highlights": {
                "featured_projects": [
                    {
                        "name": "linkedin-cv-generator",
                        "description": "AI-powered CV generator",
                        "language": "Python",
                        "stars": 5,
                        "url": "https://github.com/gerardobenitez/linkedin-cv-generator"
                    }
                ]
            },
            "github_username": "gerardobenitez"
        }
        
        generator = ResumeGenerator()
        
        # Generar CV de prueba
        html_resume = generator.generate_resume(test_profile)
        
        # Generar en múltiples formatos
        outputs = generator.generate_multiple_formats(test_profile)
        
        # Test HTML
        html_path = outputs.get("html")
        assert html_path and os.path.exists(html_path), f"No se creó el HTML: {html_path}"
        with open(html_path, 'r') as f:
            content = f.read()
            assert "<h1>" in content, "No se renderizó el nombre"
            assert "Gerardo Benitez" in content, "No se incluye el nombre"
        
        results["resume_generation"] = True
        print(f"   ✅ HTML generado: {html_path}")
        
        # Test PDF
        pdf_path = outputs.get("pdf")
        if pdf_path:
            assert os.path.exists(pdf_path), f"No se creó el PDF: {pdf_path}"
            
            # Verificar que es un PDF válido
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
                assert header == b'%PDF-', f"No es un PDF válido: {header}"
            
            pdf_size_kb = os.path.getsize(pdf_path) // 1024
            print(f"   ✅ PDF generado: {pdf_path} ({pdf_size_kb} KB)")
            results["pdf_generation"] = True
        else:
            print("   ⚠️ PDF no se pudo generar")
            results["pdf_generation"] = False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Verificar interfaz Streamlit
    print("\n4. 🧪 Verificando interfaz Streamlit...")
    try:
        # Compilar sintaxis
        with open("src/ui/app.py", 'r') as f:
            syntax_valid = compile(f.read(), "app.py", "exec")
        print("   ✅ Sintaxis del archivo Streamlit válida")
        results["web_ui_ready"] = True
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 TODOS LOS TESTS PASARON!" if all_passed else "⚠️ Algunos tests fallaron"))
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)